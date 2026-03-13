import json
import httpx
import logging
from sqlalchemy.orm import Session
from app.models.model import LogEvent, Incident
from app.api.chat import get_groq_key

logger = logging.getLogger(__name__)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

async def run_ai_detection(db: Session, events: list[LogEvent]):
    """
    Use AI to detect complex security incidents from a batch of logs.
    """
    if not events:
        return []

    api_key = get_groq_key()
    if not api_key:
        logger.error("GROQ_API_KEY not found. Skipping AI detection.")
        return []

    # Prepare log data for the prompt
    # We'll take a representative sample if there are too many logs to fit in context
    max_logs = 50
    sample_logs = events[:max_logs]
    
    log_summary = []
    for log in sample_logs:
        log_summary.append({
            "ts": log.timestamp,
            "src": log.source,
            "ip": log.ip,
            "act": log.action,
            "res": log.resource,
            "sev": log.severity
        })

    prompt = f"""
Analyze the following system logs and identify any security incidents or suspicious behavioral patterns that a rule-based system might miss.
Focus on:
1. Multi-step attack chains (e.g. recon followed by exploitation).
2. Stealthy anomalies (unusual resource access, odd timing).
3. Evasive maneuvers (obfuscated paths, unconventional user agents).

Logs (JSON Format):
{json.dumps(log_summary, indent=2)}

Return your findings ONLY as a JSON array of objects with the following structure:
[
  {{
    "type": "INCIDENT_TYPE",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "source_ip": "IP_ADDRESS",
    "description": "Clear, concise technical description showing WHY this is an incident and what the AI detected beyond simple patterns."
  }}
]
If no incidents are found, return an empty array [].
"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": "You are an expert SOC Analyst AI. Identify complex security incidents from raw logs."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
                timeout=30.0
            )

        if response.status_code != 200:
            logger.error(f"Groq API error: {response.status_code} - {response.text}")
            return []

        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse the JSON response
        data = json.loads(content)
        # Handle case where AI returns {"incidents": [...]} instead of bare array
        incidents_data = data.get('incidents', data) if isinstance(data, dict) else data
        
        new_incidents = []
        if isinstance(incidents_data, list):
            for item in incidents_data:
                incident = Incident(
                    type=item.get("type", "AI_DETECTED_ANOMALY"),
                    severity=item.get("severity", "MEDIUM"),
                    source_ip=item.get("source_ip", "0.0.0.0"),
                    description=f"🤖 [AI-ENHANCED] {item.get('description', 'Suspicious activity detected via neural analysis.')}",
                    timestamp=events[0].timestamp if events else None
                )
                db.add(incident)
                new_incidents.append(incident)
            
            db.commit()
            logger.info(f"AI Detection completed: {len(new_incidents)} incidents found.")
            
        return [
            {
                "id": inc.id,
                "type": inc.type,
                "severity": inc.severity,
                "source_ip": inc.source_ip,
                "description": inc.description,
                "timestamp": inc.timestamp
            }
            for inc in new_incidents
        ]

    except Exception as e:
        logger.error(f"Error during AI detection: {str(e)}")
        return []
