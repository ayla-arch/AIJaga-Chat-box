# AIJaga Chat Box

AiJaga is a Streamlit health-learning app with chat, quizzes, videos, and nearby
hospital information.

## Run locally

Use Python 3.10 or newer:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run aijaga_app.py
```

For AI features, create `.streamlit/secrets.toml` in the project folder and add
the provider keys you have:

```toml
GROQ_API_KEY = "..."
GEMINI_API_KEY = "..."
YOUTUBE_API_KEY = "..."
```

`GROQ_API_KEY` enables the primary chat provider. `GEMINI_API_KEY` enables
Gemini-backed features and fallback chat. `YOUTUBE_API_KEY` is optional.
Never commit `.streamlit/secrets.toml` or publish API keys.

## Deploy on Streamlit Community Cloud

The GitHub repository is public. To create a hosted app:

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with the
   GitHub account that can access `ayla-arch/AIJaga-Chat-box`.
2. Create an app from the `main` branch of that repository.
3. Set the app file to `aijaga_app.py`.
4. In the app's settings, add the API keys you want to use under **Secrets**
   using the TOML format shown above. Enter them directly in Streamlit's
   settings; do not put real keys in this repository.
5. Deploy the app. Streamlit will provide its public URL.

The app's quizzes and other non-AI features can load without API keys, but
chat, image/voice analysis, and YouTube search require the corresponding keys.