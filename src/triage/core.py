import json
from pathlib import Path

from .llm_client import call_llm
from .schema import (ErrorStatus, GitIssue, TriageDecision, RunConfig, ServiceResponse)


PROMPT_DIR = Path(__file__).parent / "prompts"

def load_system_prompt(prompt_version: str) -> str:
    prompt_file = PROMPT_DIR / f"{prompt_version}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError("Couldn't find prompt file")
    prompt = prompt_file.read_text().strip()
    return prompt


def build_user_prompt(issue: GitIssue) -> str:
    user_prompt = f"TITLE: {issue.title} \n BODY: {issue.body}"
    if issue.context:
        user_prompt += f"\nCONTEXT: {issue.context}"
    return user_prompt

def error_check(raw: dict):
    """
    This function goes through LLM response and creates right error status
    """
    if raw.get("api_error"):
        return None, ErrorStatus.API_FAILURE, raw["api_error"]

    if raw.get("finish_reason") == "length":
        return None, ErrorStatus.TRUNCATED, "finish_reason=length"

    text = raw.get("text")
    if not text:
        return None, ErrorStatus.MALFORMED_JSON, "empty response"

    try:
        resp_json = json.loads(text)
    except Exception as e:
        return None, ErrorStatus.MALFORMED_JSON, str(e)

    decision = TriageDecision.model_validate(resp_json)
    return decision, ErrorStatus.OK, None

    

def triage_core(issue: GitIssue,
                model: str,
                prompt_version: str,
                output_mode: str,
                temperature: float = 1,
                max_completion_tokens: int = 500) -> ServiceResponse:

    system_prompt = load_system_prompt(prompt_version)
    user_prompt = build_user_prompt(issue)

    llm_resp = call_llm(
        system_prompt=system_prompt,
        user_content=user_prompt,
        model=model,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        output_mode=output_mode
    )

    decision, error_status, error_message = error_check(llm_resp)

    return ServiceResponse(
        issue_id=issue.issue_id,
        decision=decision,
        error_status=error_status,
        error_message=error_message,
        raw_llm_response=llm_resp["text"],
        finish_reason=llm_resp["finish_reason"],
        usage={
            "input_tokens": llm_resp["input_tokens"],
            "output_tokens": llm_resp["output_tokens"],
        },
        latency_ms=llm_resp["latency_ms"],
        run_config=RunConfig(
            model_name=model,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            prompt_version=prompt_version, 
        ),
    )

