import json, os
from openai import OpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, SCRIPT_DIR, NUM_SCENES

SYSTEM_PROMPT_PATH = os.path.join(SCRIPT_DIR, "templates", "system_prompt.txt")

client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

def rewrite_article(title, body):
    with open(SYSTEM_PROMPT_PATH) as f:
        system_prompt = f.read()
    system_prompt = system_prompt.replace("{num_scenes}", str(NUM_SCENES))

    user_prompt = f"""제목: {title}
본문:
{body}

위 글을 쇼츠 대본으로 각색해줘."""

    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    text = resp.choices[0].message.content
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
        else:
            raise

    if isinstance(data, dict) and "scenes" in data:
        data = data["scenes"]
    return data
