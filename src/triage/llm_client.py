from dotenv import load_dotenv
import time
import os

from openai import OpenAI

load_dotenv()

_client = None

def _get_client():
    """Created on first call, not at import. Importing this module must not
    require a key - score and compare have no reason to need one."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

def call_llm(system_prompt: str,
             user_content: str,
             model: str,
             temperature: float,
             max_completion_tokens: int,
             output_mode: str = "prompt_only") -> dict:

    kwargs: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
        "max_completion_tokens": max_completion_tokens,
    }

    if output_mode == "json_object":
        kwargs["response_format"] = {"type": "json_object"}

    start = time.perf_counter()

    try:
        resp = _get_client().chat.completions.create(**kwargs)
    except Exception as e:
        return {
            "text": None,
            "finish_reason": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": (time.perf_counter() - start) * 1000,
            "api_error": str(e),
        }
    
    latency_ms = (time.perf_counter() - start) * 1000
    choice = resp.choices[0]
    usage = resp.usage

    return {
        "text": choice.message.content,
        "finish_reason": choice.finish_reason,
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
        "latency_ms": latency_ms,
        "api_error": None,
    }

