import json, boto3

def invoke_bedrock(skill_text, change_event, scored_tests, region, model_id, profile=None):
    session = boto3.Session(profile_name=profile, region_name=region) if profile else boto3.Session(region_name=region)
    client = session.client("bedrock-runtime")
    prompt = f"""
You are the Quality Intelligence Agent for an enterprise Testing Center of Excellence.
Follow SKILL.md exactly. Do not invent test IDs.

CHANGE EVENT:
{json.dumps(change_event, indent=2)}

EXISTING TEST INVENTORY WITH TRANSPARENT PRE-SCORES:
{json.dumps(scored_tests.to_dict(orient="records"), indent=2)}

Apply the Skill and select the minimum safe regression pack.
Use pre_score as evidence, not as the sole decision criterion.
Route AUTOMATED to TOSCA, MANUAL to MANUAL, HYBRID to HYBRID.
Return STRICT JSON only.
"""
    response = client.converse(
        modelId=model_id,
        system=[{"text": skill_text}],
        messages=[{"role":"user","content":[{"text":prompt}]}],
        inferenceConfig={"maxTokens":4000,"temperature":0.1,"topP":0.9}
    )
    return response["output"]["message"]["content"][0]["text"]

def parse_json_response(text):
    text = text.strip().replace("```json","").replace("```","").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        a,b = text.find("{"), text.rfind("}")
        return json.loads(text[a:b+1])
