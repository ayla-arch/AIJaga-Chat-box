"""Run:  python list_groq_models.py   -> prints the Groq model names your key can use."""
from groq import Groq

key = ""
with open(".streamlit/secrets.toml", encoding="utf-8") as f:
    for line in f:
        if line.strip().startswith("GROQ_API_KEY"):
            key = line.split('"')[1]

client = Groq(api_key=key)
for m in client.models.list().data:
    print(m.id)
