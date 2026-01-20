import json
import os
import boto3

BEDROCK_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "anthropic.claude-sonnet-4-20250514-v1:0")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.6"))

bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)


def _cors_headers():
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "content-type",
        "Access-Control-Allow-Methods": "OPTIONS,POST",
    }


def _build_response(status_code, body_obj=None):
    body_text = "" if body_obj is None else json.dumps(body_obj, ensure_ascii=False)
    return {
        "statusCode": status_code,
        "headers": _cors_headers(),
        "body": body_text,
    }


def _extract_prompt(event):
    body = event.get("body")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except Exception:
            body = {}
    elif body is None:
        body = {}

    prompt = (
        body.get("prompt")
        or body.get("message")
        or body.get("input")
        or body.get("text")
    )

    if not prompt and body.get("data") is not None:
        prompt = json.dumps(body.get("data"), ensure_ascii=True)

    if not prompt:
        prompt = (
            event.get("prompt")
            or event.get("message")
            or event.get("input")
            or event.get("text")
        )

    return prompt


def _extract_answer(resp_body):
    if not isinstance(resp_body, dict):
        return ""

    if "content" in resp_body and isinstance(resp_body["content"], list):
        parts = []
        for item in resp_body["content"]:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        answer = "".join(parts).strip()
        if answer:
            return answer

    for key in ("completion", "outputText", "answer", "result", "text", "message"):
        if key in resp_body and isinstance(resp_body[key], str):
            return resp_body[key].strip()

    return ""


def lambda_handler(event, context):
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod", "")
    ).upper()

    if method == "OPTIONS":
        return _build_response(204, None)

    prompt = _extract_prompt(event)
    if not prompt:
        return _build_response(400, {"error": "missing prompt"})

    try:
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "messages": [{"role": "user", "content": prompt}],
        }

        resp = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json",
        )

        resp_body = json.loads(resp["body"].read())
        answer = _extract_answer(resp_body)
        if not answer:
            return _build_response(502, {"error": "empty model response"})

        return _build_response(200, {"answer": answer})
    except Exception as exc:
        return _build_response(500, {"error": str(exc)})
