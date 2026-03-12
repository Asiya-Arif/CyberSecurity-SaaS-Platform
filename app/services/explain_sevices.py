"""
Oracle Explain Service
Provides logic for generating technical security explanations for detected incidents.
"""

def generate_oracle_prompt(incident_type, severity, ip, description, timestamp=None, endpoint=None, method=None, status=None, raw_log=None):
    """
    Constructs a detailed prompt for the AI Oracle based on actual incident row data.
    """
    context = f"[CONTEXT]\n"
    context += f"Incident Type: {incident_type}\n"
    context += f"Severity: {severity}\n"
    context += f"Source IP: {ip}\n"
    context += f"Description: {description}\n"
    
    if timestamp: context += f"Timestamp: {timestamp}\n"
    if endpoint: context += f"Endpoint: {endpoint}\n"
    if method: context += f"Method: {method}\n"
    if status: context += f"Status Code: {status}\n"
    if raw_log: context += f"Raw Log Evidence: {raw_log}\n"
        
    prompt = f"""{context}

[INSTRUCTION]
Analyze this incident in simple security terms. Every explanation MUST strictly follow this layout:

[ANALYSIS]
Short explanation describing:
* what happened
* why it was flagged
* what the suspicious behavior indicates

[MITIGATION]
>> mitigation step 1
>> mitigation step 2
>> mitigation step 3

[VERDICT]
THREAT_CONFIRMED: <classification>

Example classification values:
* ACTIVE_RECONNAISSANCE
* BRUTE_FORCE_ATTEMPT
* SUSPICIOUS_ENDPOINT_ACCESS
* MALICIOUS_AUTOMATION
* POTENTIAL_CREDENTIAL_ATTACK

If the provided context is insufficient to generate a complete analysis, you MUST return this exact fallback message:

[ANALYSIS]
Oracle could not generate a complete explanation because the incident data is incomplete.

[MITIGATION]
>> Review the uploaded dataset for missing fields
>> Ensure incident logs include IP, endpoint, and request type
>> Re-run analysis after correcting the dataset

[VERDICT]
THREAT_STATUS: INSUFFICIENT_DATA

Keep it concise, technical, and strictly formatted.
"""
    return prompt

def get_fallback_message():
    """Returns the standard fallback message when data is insufficient."""
    return """[ANALYSIS]
Oracle could not generate a complete explanation because the incident data is incomplete.

[MITIGATION]
>> Review the uploaded dataset for missing fields
>> Ensure incident logs include IP, endpoint, and request type
>> Re-run analysis after correcting the dataset

[VERDICT]
THREAT_STATUS: INSUFFICIENT_DATA"""
