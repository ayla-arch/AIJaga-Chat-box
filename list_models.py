"""Run:  python list_models.py   -> prints the model names your API key can use."""
from google import genai

key = ""
with open(".streamlit/secrets.toml", encoding="utf-8") as f:
    for line in f:
        if line.strip().startswith("GEMINI_API_KEY"):
            key = line.split('"')[1]

client = genai.Client(api_key=key)
for m in client.models.list():
    if "generateContent" in (m.supported_actions or []):
        print(m.name.replace("models/", ""))
