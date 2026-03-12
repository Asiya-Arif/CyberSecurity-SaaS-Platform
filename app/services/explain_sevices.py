"""
Oracle Explain Service
Provides logic for generating technical security explanations for detected incidents.
"""

def generate_oracle_prompt(incident_type, severity, ip, description, raw_log=None):
    """
    Constructs a detailed prompt for the AI Oracle based on actual incident row data.
    """
    context = f"[CONTEXT]\nIncident Type: {incident_type}\nSeverity: {severity}\nSource IP: {ip}\nSystem Description: {description}"
    
    if raw_log:
        context += f"\nRaw Log Evidence: {raw_log}"
        
    prompt = f"{context}\n\n[INSTRUCTION]\nAnalyze this specific security event. Provide a high-accuracy technical explanation and 3 direct mitigation steps. Use terminal-style formatting with [ANALYSIS], [MITIGATION], and [VERDICT] headers. Keep it concise and technical."
    
    return prompt

def get_fallback_message():
    """Returns the standard fallback message when data is insufficient."""
    return "Oracle could not generate an explanation for this incident due to insufficient or incompatible data."
