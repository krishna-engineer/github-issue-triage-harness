from triage.llm_client import call_llm


SYSTEM = (
    'You triage GitHub issues. Return ONLY JSON: '
    '{"issue_type": one of ["bug","feature_request","other"], '
    '"urgency": one of ["low","normal","critical"], '
    '"needs_human": true or false}'
)
USER = "TITLE: App crashes on login\n\nBODY:\nEvery user gets a 500 on sign-in since the deploy."
 
result = call_llm(
    system_prompt=SYSTEM,
    user_content=USER,
    model="gpt-5-nano",
    temperature=1,
    max_completion_tokens=1000,
    output_mode="json_object",
)

print(result)