"""
AiJaga — retro "AiJaga TV" health assistant with Dr. Azmi, built with Streamlit.

Run it with:
    pip install -r requirements.txt
    streamlit run AiJaga-prototype.py

Main page: Dr. Azmi's greeting + chat box, with VIDEO and QUIZ buttons on the right.
The VIDEO and QUIZ buttons open their own pages; every page has a HOME button.
"""

import html
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AiJaga", page_icon="🩺", layout="wide")

DOCTOR = "Dr. Azmi"

# ---------------------------------------------------------------------------
# 1. Colours (Bright and Dark themes)
# ---------------------------------------------------------------------------
THEMES = {
    "bright": {
        "page": "#F6F1E7", "frame": "#EBC99D", "frame_edge": "#D4A774", "frame_text": "#6E4F2C",
        "screen": "#E1EEEA", "scan": "rgba(255,255,255,0.5)", "ink": "#1C2B33", "sub": "#344A50",
        "card": "#FFFFFF", "chat_bg": "#F2F7F5", "teal": "#2D6A5C", "coral": "#E36F52",
        "chip": "#D3EAE2", "btn_text": "#FFFFFF", "online": "#2FAE5E",
    },
    "dark": {
        "page": "#111517", "frame": "#3B3229", "frame_edge": "#2A231C", "frame_text": "#C9A982",
        "screen": "#13221F", "scan": "rgba(0,0,0,0.28)", "ink": "#E4F1ED", "sub": "#A8C3BC",
        "card": "#1A2E2A", "chat_bg": "#152623", "teal": "#5CC0A6", "coral": "#F08A6E",
        "chip": "#1F3A34", "btn_text": "#0D1916", "online": "#4FD481",
    },
}

# ---------------------------------------------------------------------------
# 2. Content
# ---------------------------------------------------------------------------
# QUICK_QUESTIONS = [
#     "Why do I get headaches?",
#     "How to lower blood pressure",
#     "First aid for burns",
#     "Tips for better sleep",
# ]

QUIZ = [
    {"q": "How long should you scrub your hands with soap when washing them?",
     "options": ["About 5 seconds", "At least 20 seconds", "Exactly 2 minutes"], "answer": 1,
     "explain": "Scrub for at least 20 seconds — about as long as humming “Happy Birthday” twice."},
    {"q": "What is the best first aid for a minor burn?",
     "options": ["Put ice directly on it", "Spread butter or toothpaste on it",
                 "Cool it under cool running water for about 20 minutes"], "answer": 2,
     "explain": "Cool running water helps. Ice, butter and toothpaste can make the skin damage worse."},
    {"q": "How much sleep do most adults need each night?",
     "options": ["4–5 hours", "7–9 hours", "11–12 hours"], "answer": 1,
     "explain": "Most adults need 7 to 9 hours of sleep a night to feel and work their best."},
    {"q": "What is a normal resting heart rate for most adults?",
     "options": ["30–40 beats per minute", "60–100 beats per minute", "120–150 beats per minute"], "answer": 1,
     "explain": "For most adults a resting heart rate between 60 and 100 beats per minute is normal. Very fit people can be lower."},
    {"q": "Which of these can be a sign of dehydration?",
     "options": ["Pale, clear urine", "A runny nose", "Feeling very thirsty with dark yellow urine"], "answer": 2,
     "explain": "Strong thirst and dark yellow urine are common signs your body needs more fluids."},
]

# Put a real video link (YouTube or .mp4) in "url" and it will play on the Video page.
VIDEOS = [
    {"title": "Washing your hands the right way", "tag": "HYGIENE", "url": None,
     "desc": "Learn the simple steps that wash away germs and help stop infections from spreading."},
    {"title": "First aid for burns", "tag": "FIRST AID", "url": None,
     "desc": "What to do in the first minutes after a minor burn — and what not to put on it."},
    {"title": "CPR basics", "tag": "FIRST AID", "url": None,
     "desc": "An introduction to hands-only CPR. Always call 999 first in a real emergency."},
    {"title": "Building a healthy plate", "tag": "NUTRITION", "url": None,
     "desc": "How to balance vegetables, protein and whole grains in your everyday meals."},
    {"title": "Better sleep habits", "tag": "WELLBEING", "url": None,
     "desc": "Small changes to your evening routine that can help you sleep more soundly."},
    {"title": "Spotting dehydration", "tag": "EVERYDAY HEALTH", "url": None,
     "desc": "Common signs that your body needs more fluids, and easy ways to stay hydrated."},
]

WELCOME = (f"Hi, I'm {DOCTOR}! Ask me a health question by typing below, "
           "or tap + to add a photo or a voice note.")
CHAT_INSTRUCTIONS = (
    "You are Dr. Azmi, AiJaga's AI health education assistant in Malaysia. "
    "Answer in the user's language using short, accessible plain text. "
    "Provide general health information. Do not claim to be a clinician, diagnose, "
    "or prescribe. For signs of an emergency, advise calling local emergency services "
    "(999 in Malaysia) immediately. Do not request identifying information."
)
DISCLAIMER = "AiJaga shares general health information, not a diagnosis. In an emergency, call 999."

# ---------------------------------------------------------------------------
# 3. Pixel art (SVG drawings made of little squares)
# ---------------------------------------------------------------------------
LOGO_SVG = """
<svg width="{w}" height="{h}" viewBox="0 0 17 15" shape-rendering="crispEdges" role="img" aria-label="AiJaga logo">
<rect x="3" y="2" width="4" height="1" fill="#3E8EC2"/><rect x="2" y="3" width="6" height="3" fill="#3E8EC2"/>
<rect x="3" y="6" width="4" height="1" fill="#3E8EC2"/>
<rect x="1" y="8" width="8" height="1" fill="#3E8EC2"/><rect x="0" y="9" width="10" height="6" fill="#3E8EC2"/>
<rect x="3" y="8" width="1" height="5" fill="#1C2B33"/><rect x="6" y="8" width="1" height="3" fill="#1C2B33"/>
<rect x="2" y="12" width="3" height="2" fill="#1C2B33"/><rect x="3" y="12" width="1" height="1" fill="#3E8EC2"/>
<rect x="5" y="11" width="3" height="3" fill="#1C2B33"/><rect x="6" y="12" width="1" height="1" fill="#3E8EC2"/>
<rect x="10" y="0" width="2" height="1" fill="#E0405E"/><rect x="13" y="0" width="2" height="1" fill="#E0405E"/>
<rect x="9" y="1" width="7" height="2" fill="#E0405E"/><rect x="10" y="3" width="5" height="1" fill="#E0405E"/>
<rect x="11" y="4" width="3" height="1" fill="#E0405E"/><rect x="12" y="5" width="1" height="1" fill="#E0405E"/>
<rect x="10" y="1" width="1" height="1" fill="#FF8FA3"/>
</svg>
"""

DOCTOR_SVG = """
<svg width="{w}" height="{h}" viewBox="0 0 16 20" shape-rendering="crispEdges" role="img" aria-label="Dr. Azmi">
<rect x="6" y="0" width="4" height="1" fill="#C9D3D0"/><rect x="7" y="0" width="2" height="1" fill="#E36F52"/>
<rect x="3" y="1" width="10" height="1" fill="#1C2B33"/>
<rect x="3" y="2" width="1" height="5" fill="#1C2B33"/><rect x="12" y="2" width="1" height="5" fill="#1C2B33"/>
<rect x="4" y="1" width="8" height="2" fill="#4A2E22"/>
<rect x="4" y="3" width="8" height="4" fill="#F2C29B"/>
<rect x="6" y="4" width="1" height="2" fill="#1C2B33"/><rect x="9" y="4" width="1" height="2" fill="#1C2B33"/>
<rect x="5" y="5" width="1" height="1" fill="#E36F52"/><rect x="10" y="5" width="1" height="1" fill="#E36F52"/>
<rect x="4" y="7" width="8" height="1" fill="#1C2B33"/><rect x="7" y="6" width="2" height="1" fill="#1C2B33"/>
<rect x="7" y="8" width="2" height="1" fill="#F2C29B"/>
<rect x="3" y="8" width="10" height="11" fill="#1C2B33"/>
<rect x="4" y="9" width="8" height="9" fill="#FFFFFF"/>
<rect x="5" y="8" width="6" height="4" fill="#1C2B33"/><rect x="6" y="9" width="4" height="3" fill="#2D6A5C"/>
<rect x="7" y="9" width="2" height="1" fill="#F2C29B"/>
<rect x="7" y="12" width="2" height="2" fill="#E36F52"/>
<rect x="10" y="12" width="2" height="1" fill="#2D6A5C"/>
</svg>
"""

# Small square face used next to Dr. Azmi's chat messages.
MINI_DOCTOR_SVG = """
<svg width="34" height="34" viewBox="0 0 8 8" shape-rendering="crispEdges" aria-hidden="true">
<rect x="1" y="0" width="6" height="2" fill="#4A2E22"/><rect x="1" y="2" width="6" height="3" fill="#F2C29B"/>
<rect x="2" y="3" width="1" height="1" fill="#1C2B33"/><rect x="5" y="3" width="1" height="1" fill="#1C2B33"/>
<rect x="0" y="5" width="8" height="3" fill="#FFFFFF"/><rect x="3" y="5" width="2" height="3" fill="#2D6A5C"/>
</svg>
"""


def svg_url(svg):
    """Turn an SVG string into something CSS can use as a background image."""
    return "url(\"data:image/svg+xml," + quote(" ".join(svg.split())) + "\")"


# ---------------------------------------------------------------------------
# 4. Session state (remembers things between clicks)
# ---------------------------------------------------------------------------
DEFAULTS = {
    "page": "home",
    "theme": "bright",
    "messages": [{"role": "bot", "text": WELCOME}],
    "read_aloud": False,
    "speak": None,
    "quiz_i": 0, "quiz_pick": None, "quiz_score": 0, "quiz_done": False,
    "video_i": 0, "video_seen": set(), "video_playing": False,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, (list, set)) else value

S = st.session_state
C = THEMES[S.theme]


def go(page):
    S.page = page


def set_theme(name):
    S.theme = name


# ---------------------------------------------------------------------------
# 5. Retro "AiJaga TV" styling
# ---------------------------------------------------------------------------
def inject_css():
    play_icon = svg_url(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='120' height='90' viewBox='0 0 12 9' shape-rendering='crispEdges'>"
        f"<rect width='12' height='9' fill='{C['ink']}'/><rect x='1' y='1' width='10' height='7' fill='{C['chip']}'/>"
        f"<rect x='4' y='2' width='1' height='5' fill='{C['coral']}'/><rect x='5' y='3' width='1' height='3' fill='{C['coral']}'/>"
        f"<rect x='6' y='4' width='1' height='1' fill='{C['coral']}'/></svg>")
    quiz_icon = svg_url(
        f"<svg xmlns='http://www.w3.org/2000/svg' width='130' height='70' viewBox='0 0 13 7' shape-rendering='crispEdges'>"
        f"<rect x='1' y='0' width='1' height='1' fill='{C['coral']}'/><rect x='0' y='1' width='1' height='5' fill='{C['coral']}'/>"
        f"<rect x='1' y='6' width='1' height='1' fill='{C['coral']}'/>"
        f"<rect x='11' y='0' width='1' height='1' fill='{C['coral']}'/><rect x='12' y='1' width='1' height='5' fill='{C['coral']}'/>"
        f"<rect x='11' y='6' width='1' height='1' fill='{C['coral']}'/>"
        f"<rect x='5' y='0' width='3' height='1' fill='{C['ink']}'/><rect x='4' y='1' width='1' height='1' fill='{C['ink']}'/>"
        f"<rect x='8' y='1' width='1' height='2' fill='{C['ink']}'/><rect x='7' y='3' width='1' height='1' fill='{C['ink']}'/>"
        f"<rect x='6' y='4' width='1' height='1' fill='{C['ink']}'/><rect x='6' y='6' width='1' height='1' fill='{C['ink']}'/></svg>")

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Nunito:wght@500;600;700&display=swap');

#MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0; }}
.stApp {{ background: {C['page']}; }}
html, body, .stApp, p, label, li, input, textarea, .stMarkdown {{ font-family: 'Nunito', sans-serif; color: {C['ink']}; }}
.stApp [data-testid="stCaptionContainer"] p {{ color: {C['sub']}; }}

/* The TV body and screen */
.block-container {{
  max-width: 1240px; margin: 30px auto 0; padding: 26px 30px 30px !important;
  background-color: {C['screen']};
  background-image: repeating-linear-gradient(0deg, {C['scan']} 0 2px, transparent 2px 5px);
  border: 8px solid {C['frame_edge']}; border-radius: 28px;
  box-shadow: 0 0 0 26px {C['frame']}, 0 26px 0 26px {C['frame']};
}}

.pixel {{ font-family: 'Silkscreen', monospace; font-weight: 700; letter-spacing: 1px; }}
.sub {{ color: {C['sub']}; }}
h1, h2, h3 {{ font-family: 'Silkscreen', monospace !important; color: {C['ink']} !important; letter-spacing: 1px; }}

.card {{ background: {C['card']}; border: 4px solid {C['ink']}; box-shadow: 8px 8px 0 {C['ink']};
         padding: 20px 22px; margin-bottom: 18px; color: {C['ink']}; }}
.tag {{ display: inline-block; padding: 4px 12px; background: {C['coral']}; border: 3px solid {C['ink']};
        color: #1C2B33; font-family: 'Silkscreen', monospace; font-weight: 700; font-size: 13px; letter-spacing: 1px; }}
.logo {{ display: flex; align-items: center; gap: 12px; }}

/* Buttons: chunky pixel style */
.stButton > button, .stFormSubmitButton > button, [data-testid="stPopover"] button {{
  border: 3px solid {C['ink']} !important; border-radius: 0 !important;
  background: {C['chip']} !important; color: {C['ink']} !important;
  box-shadow: 4px 4px 0 {C['ink']}; font-weight: 700; min-height: 46px;
}}
.stButton > button:hover, [data-testid="stPopover"] button:hover {{ transform: translate(-2px, -2px); box-shadow: 6px 6px 0 {C['ink']}; }}
.stButton > button[kind="primary"], .stFormSubmitButton > button {{
  background: {C['teal']} !important; color: {C['btn_text']} !important;
  font-family: 'Silkscreen', monospace; letter-spacing: 1px;
}}
.stButton > button p, .stFormSubmitButton > button p, [data-testid="stPopover"] button p {{ color: inherit !important; white-space: normal; }}

/* Text boxes */
.stTextInput input {{ border-radius: 0 !important; background: {C['card']} !important; color: {C['ink']} !important; font-size: 17px; }}
.stTextInput input::placeholder {{ color: {C['sub']}; opacity: .8; }}
.stTextInput > div > div {{ border: 3px solid {C['ink']} !important; border-radius: 0 !important; }}

/* Speech bubble */
.bubble-hello {{ position: relative; background: {C['card']}; border: 4px solid {C['ink']};
                 box-shadow: 8px 8px 0 {C['ink']}; padding: 16px 22px; max-width: 520px; }}
.bubble-hello::before {{ content: ""; position: absolute; left: -22px; top: 14px; border: 11px solid transparent;
                         border-right-color: {C['ink']}; border-top-color: {C['ink']}; }}
.dots span {{ display: inline-block; width: 7px; height: 7px; margin-right: 6px; background: {C['coral']};
              animation: blink 1.2s infinite; }}
.dots span:nth-child(2) {{ animation-delay: .2s; }} .dots span:nth-child(3) {{ animation-delay: .4s; }}
@keyframes blink {{ 0%, 80%, 100% {{ opacity: .2; }} 40% {{ opacity: 1; }} }}

/* Chat panel */
.st-key-chat_panel {{ background: {C['card']}; border: 4px solid {C['ink']}; box-shadow: 8px 8px 0 {C['ink']};
                      padding: 0 16px 14px; gap: 10px; }}
.chat-head {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
              margin: 0 -16px; padding: 12px 16px; border-bottom: 3px solid {C['ink']}; }}
.st-key-chat_log {{ margin-top: 18px; background: {C['chat_bg']}; border: 3px solid {C['ink']} !important; border-radius: 0 !important; }}
.msg {{ display: flex; gap: 10px; align-items: flex-start; margin: 4px 0 2px; }}
.msg.user {{ justify-content: flex-end; }}
.avatar {{ flex: none; width: 42px; height: 42px; border: 3px solid {C['ink']}; background: {C['chip']};
           display: flex; align-items: center; justify-content: center; }}
.bubble {{ border: 3px solid {C['ink']}; box-shadow: 4px 4px 0 {C['ink']}; padding: 10px 14px;
           max-width: 78%; white-space: pre-line; line-height: 1.5; font-size: 16px; }}
.bubble.bot {{ background: {C['card']}; color: {C['ink']}; }}
.bubble.user {{ background: {C['teal']}; color: {C['btn_text']}; }}
.who {{ display: block; font-family: 'Silkscreen', monospace; font-size: 10px; letter-spacing: 2px; margin-bottom: 3px; opacity: .85; }}
.st-key-chat_log .stButton > button {{ min-height: 34px; padding: 2px 12px; margin-left: 52px; box-shadow: 3px 3px 0 {C['ink']}; font-size: 14px; }}
.st-key-chat_panel [data-testid="InputInstructions"] {{ display: none; }}
.st-key-chat_panel .stTextInput input {{ min-height: 48px; padding: 10px 14px; }}
.st-key-chat_panel .stFormSubmitButton > button,
.st-key-chat_panel [data-testid="stPopover"] button {{ min-height: 54px; }}
[data-testid="stPopover"] button {{ font-size: 24px; padding: 0; justify-content: center; }}
[data-testid="stPopover"] button p {{ font-size: 24px; font-weight: 700; }}
[data-testid="stPopover"] button [data-testid="stIconMaterial"] {{ display: none; }}
[data-testid="stPopoverBody"] {{ background: {C['card']}; border: 3px solid {C['ink']}; border-radius: 0; }}
[class*="st-key-opt_"] button p {{ font-size: 18px; }}
[class*="st-key-quick_"] button {{ min-height: 38px; font-size: 14px; box-shadow: 3px 3px 0 {C['ink']}; }}

/* Big VIDEO and QUIZ buttons on the main page */
.st-key-open_video button, .st-key-open_quiz button {{
  height: 230px; width: 100%; flex-direction: column; gap: 14px; background: {C['card']} !important;
  border: 4px solid {C['ink']} !important; box-shadow: 8px 8px 0 {C['ink']};
  font-family: 'Silkscreen', monospace; font-size: 26px; letter-spacing: 3px;
}}
.st-key-open_video button::before, .st-key-open_quiz button::before {{
  content: ""; display: block; width: 120px; height: 90px; background-repeat: no-repeat; background-position: center;
  background-size: contain; image-rendering: pixelated;
}}
.st-key-open_video button::before {{ background-image: {play_icon}; }}
.st-key-open_quiz button::before {{ background-image: {quiz_icon}; height: 70px; width: 130px; }}
.st-key-open_video button:hover, .st-key-open_quiz button:hover {{
  transform: translate(-3px, -3px); box-shadow: 11px 11px 0 {C['coral']}; }}
.st-key-open_video button p, .st-key-open_quiz button p {{ font-size: 26px; color: {C['ink']} !important; }}

.video-screen {{ aspect-ratio: 16/9; background: #1C2B33; border: 4px solid {C['ink']};
                 display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 12px;
                 background-image: repeating-linear-gradient(0deg, rgba(255,255,255,.05) 0 2px, transparent 2px 5px); }}
.play {{ width: 76px; height: 76px; background: #E36F52; border: 4px solid #fff; display: flex;
         align-items: center; justify-content: center; color: #fff; font-size: 30px; }}
.score-bar {{ height: 18px; border: 3px solid {C['ink']}; background: {C['card']}; margin: 6px 0 4px; }}
.score-fill {{ height: 100%; background: {C['coral']}; }}

.tv-footer {{ display: flex; justify-content: space-between; align-items: center;
              margin: 40px -30px -30px; padding: 22px 36px; background: {C['frame']}; }}
.grille span {{ display: inline-block; width: 8px; height: 36px; margin-right: 8px; border-radius: 3px; background: {C['frame_edge']}; }}
.knob {{ display: inline-block; width: 40px; height: 40px; border-radius: 50%; background: {C['frame_edge']}; margin-left: 14px; }}
.led {{ display: inline-block; width: 13px; height: 13px; border-radius: 50%; background: {C['coral']}; margin-left: 14px; }}
.disclaimer {{ text-align: center; font-size: 14px; color: {C['sub']}; margin-top: 18px; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 6. Shared pieces
# ---------------------------------------------------------------------------
def top_bar():
    left, _, right = st.columns([2.4, 2, 1.6], vertical_alignment="center")
    with left:
        if S.page != "home":
            home, logo = st.columns([1, 2.6], vertical_alignment="center")
            home.button("◂ HOME", on_click=go, args=("home",), key=f"home_{S.page}")
        else:
            logo = st.container()
        logo.markdown(f"<div class='logo'>{LOGO_SVG.format(w=58, h=51)}"
                      f"<span class='pixel' style='font-size:28px;letter-spacing:4px'>AIJAGA</span></div>",
                      unsafe_allow_html=True)
    with right:
        b, d = st.columns(2)
        b.button("BRIGHT", key=f"bright_{S.page}", use_container_width=True,
                 type="primary" if S.theme == "bright" else "secondary", on_click=set_theme, args=("bright",))
        d.button("DARK", key=f"dark_{S.page}", use_container_width=True,
                 type="primary" if S.theme == "dark" else "secondary", on_click=set_theme, args=("dark",))


def tv_footer():
    st.markdown(f"<p class='disclaimer'>{DISCLAIMER}</p>"
                "<div class='tv-footer'>"
                "<div class='grille'><span></span><span></span><span></span><span></span><span></span></div>"
                f"<span class='pixel' style='color:{C['frame_text']};font-size:20px;letter-spacing:4px'>AIJAGA TV</span>"
                "<div><span class='knob'></span><span class='knob'></span><span class='led'></span></div>"
                "</div>", unsafe_allow_html=True)


def speak_if_needed():
    """Read text aloud in the browser using its built-in speech voice."""
    if S.speak:
        spoken_text = json.dumps(S.speak).replace("<", r"\u003c")
        components.html(
            "<script>try{const s=window.parent.speechSynthesis||window.speechSynthesis;"
            f"s.cancel();s.speak(new SpeechSynthesisUtterance({spoken_text}));}}catch(e){{}}</script>",
            height=0)
        S.speak = None


# ---------------------------------------------------------------------------
# 7. Chat helpers
# ---------------------------------------------------------------------------
def bot_reply(text):
    S.messages.append({"role": "bot", "text": text})
    if S.read_aloud:
        S.speak = text


def ask(question):
    question = (question or "").strip()
    if not question:
        return
    S.chat_error = None
    try:
        key = st.secrets["AGNES_API_KEY"].strip()
    except (FileNotFoundError, KeyError):
        key = ""
    if not key:
        S.chat_error = "Add AGNES_API_KEY to .streamlit/secrets.toml and restart the app."
        return
    history = [{"role": "assistant" if m["role"] == "bot" else "user", "content": m["text"]}
               for m in S.messages if m.get("agnes_turn")][-20:]
    payload = {"model": "agnes-2.5-flash", "messages": [
        {"role": "system", "content": CHAT_INSTRUCTIONS}, *history,
        {"role": "user", "content": question}]}
    request = Request("https://apihub.agnes-ai.com/v1/chat/completions",
                      data=json.dumps(payload).encode(),
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with st.spinner("Dr. Azmi is replying..."), urlopen(request, timeout=45) as response:
            reply = json.load(response)["choices"][0]["message"]["content"]
            if not isinstance(reply, str) or not reply.strip():
                raise ValueError("Empty reply")
    except HTTPError as exc:
        if exc.code in (401, 403):
            S.chat_error = "Check your Agnes API key and model access, then send again."
        elif exc.code == 429:
            S.chat_error = "Agnes AI's usage limit was reached. Please try again later."
        else:
            S.chat_error = f"Agnes AI returned HTTP {exc.code}. Please try again later."
        return
    except (OSError, URLError, ValueError, KeyError, IndexError, TypeError):
        S.chat_error = "Could not get a reply from Agnes AI. Please send your question again."
        return
    S.messages.append({"role": "user", "text": question, "agnes_turn": True})
    bot_reply(reply.strip())
    S.messages[-1]["agnes_turn"] = True


def chat_box():
    with st.container(key="chat_panel"):
        st.markdown("<div class='chat-head'>"
                    "<span class='pixel' style='font-size:15px'>CHAT WITH DR. AZMI</span>"
                    "<span class='pixel sub' style='font-size:12px'>"
                    f"<span style='display:inline-block;width:10px;height:10px;background:{C['online']};margin-right:8px'></span>"
                    "AI ASSISTANT</span></div>", unsafe_allow_html=True)
        if S.get("chat_error"):
            st.error(S.chat_error)

        # Message history (scrolls when it gets long)
        with st.container(height=330, key="chat_log"):
            for i, msg in enumerate(S.messages):
                text = html.escape(msg["text"])
                if msg["role"] == "bot":
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    reply = "<br>".join("• " + line[2:] if line.startswith(("- ", "* ")) else line
                                         for line in lines)
                    st.html(f"<div class='msg'><div class='avatar'>{MINI_DOCTOR_SVG}</div>"
                            f"<div class='bubble bot'><span class='who'>DR. AZMI</span>{reply}</div></div>")
                    st.button("🔊 Listen", key=f"listen_{i}", on_click=lambda t=msg["text"]: S.update(speak=t))
                else:
                    if msg.get("image") is not None:
                        _, img = st.columns([2, 1])
                        img.image(msg["image"], use_container_width=True)
                    st.markdown(f"<div class='msg user'><div class='bubble user'>"
                                f"<span class='who'>YOU</span>{text}</div></div>", unsafe_allow_html=True)

        # # Quick questions
        # q_cols = st.columns(len(QUICK_QUESTIONS))
        # for col, q in zip(q_cols, QUICK_QUESTIONS):
        #     col.button(q, key=f"quick_{q}", on_click=ask, args=(q,), use_container_width=True)

        # "+" attach button, typing box and SEND
        plus, rest = st.columns([1, 9], vertical_alignment="bottom")
        with plus.popover("+", help="Add a photo or voice note", use_container_width=True):
            photo = st.file_uploader("Send a photo", type=["png", "jpg", "jpeg"], key="photo")
            if photo is not None and st.button("Send photo", key="send_photo", type="primary"):
                S.messages.append({"role": "user", "text": "(Photo sent)", "image": photo.getvalue()})
                bot_reply("Thanks for the photo! Photo checking is coming soon. "
                          "For now, please also describe what you see in words.")
                st.rerun()
            voice = st.audio_input("Record a voice note", key="voice")
            if voice is not None and st.button("Send voice note", key="send_voice", type="primary"):
                S.messages.append({"role": "user", "text": "(Voice note sent)"})
                bot_reply("Thanks for the voice note! Voice support is coming soon. "
                          "For now, please type your question.")
                st.rerun()
            st.checkbox("Read Dr. Azmi's replies aloud", key="read_aloud")
        with rest:
            with st.form("ask_form", clear_on_submit=True, border=False):
                box, send = st.columns([5, 1], vertical_alignment="bottom")
                question = box.text_input("Your healthcare question", label_visibility="collapsed",
                                          placeholder="Type your healthcare question here...")
                if send.form_submit_button("SEND", use_container_width=True):
                    ask(question)
                    st.rerun()


# ---------------------------------------------------------------------------
# 8. Pages
# ---------------------------------------------------------------------------
def home_page():
    top_bar()
    main, side = st.columns([2.3, 1], gap="large")

    with main:
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:34px;margin:18px 0 26px'>"
            f"<div style='text-align:center'>{DOCTOR_SVG.format(w=88, h=110)}<br><span class='tag'>DR. AZMI</span></div>"
            "<div class='bubble-hello'>"
            "<div class='pixel sub' style='font-size:12px'>DR. AZMI</div>"
            "<p style='font-size:20px;font-weight:700;margin:6px 0 8px'>Hi, I am Dr. Azmi!</p>"
            "<p style='font-size:16px;margin:0 0 10px'>Ask me a health question below, or press "
            "<b>Video</b> or <b>Quiz</b> to learn and play.</p>"
            "<div class='dots' aria-hidden='true'><span></span><span></span><span></span></div>"
            "</div></div>", unsafe_allow_html=True)
        chat_box()

    with side:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.button("VIDEO", key="open_video", on_click=go, args=("video",), use_container_width=True,
                  help="Watch short health and first-aid videos")
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        st.button("QUIZ", key="open_quiz", on_click=go, args=("quiz",), use_container_width=True,
                  help="Test your health knowledge")

    speak_if_needed()
    tv_footer()


def quiz_page():
    top_bar()
    total = len(QUIZ)
    i, pick = S.quiz_i, S.quiz_pick
    answered = pick is not None
    done_count = total if S.quiz_done else i + (1 if answered else 0)

    st.markdown("<h1 style='text-align:center;font-size:38px;margin-top:20px'>( ? ) HEALTH QUIZ</h1>",
                unsafe_allow_html=True)
    _, mid, _ = st.columns([0.6, 2, 0.6])

    with mid:
        st.markdown(f"<div class='pixel sub' style='font-size:12px;letter-spacing:2px'>SCORE {S.quiz_score} / {total}"
                    f" · QUESTION {min(i + 1, total)} OF {total}</div>"
                    f"<div class='score-bar'><div class='score-fill' style='width:{round(done_count / total * 100)}%'>"
                    "</div></div>", unsafe_allow_html=True)
        if S.quiz_done:
            score = S.quiz_score
            msg = ("Perfect score — you are a true Health Hero!" if score == total
                   else "Great job! A little more practice and you’ll ace it." if score >= 3
                   else "Good start! Try again to level up.")
            st.markdown(f"<div class='card' style='text-align:center;margin-top:18px'><span class='tag'>LEVEL COMPLETE!</span>"
                        f"<p class='pixel' style='font-size:44px;margin:16px 0'>{score} / {total}</p>"
                        f"<p class='sub' style='font-size:19px;font-weight:600'>{msg}</p></div>",
                        unsafe_allow_html=True)
            a, b = st.columns(2)
            a.button("PLAY AGAIN", type="primary", use_container_width=True,
                     on_click=lambda: S.update(quiz_i=0, quiz_pick=None, quiz_score=0, quiz_done=False))
            b.button("ASK DR. AZMI", use_container_width=True, on_click=go, args=("home",))
        else:
            item = QUIZ[i]
            st.markdown(f"<div class='card' style='margin-top:18px'><span class='tag'>QUESTION {i + 1}</span>"
                        f"<p style='font-size:24px;font-weight:700;line-height:1.35;"
                        f"margin:14px 0 0'>{item['q']}</p></div>", unsafe_allow_html=True)

            def choose(k):
                if S.quiz_pick is None:
                    S.quiz_pick = k
                    if k == QUIZ[S.quiz_i]["answer"]:
                        S.quiz_score += 1

            for k, option in enumerate(item["options"]):
                label = option
                if answered and k == item["answer"]:
                    label = "✓ " + option
                elif answered and k == pick:
                    label = "✕ " + option
                st.button(label, key=f"opt_{i}_{k}", on_click=choose, args=(k,),
                          disabled=answered, use_container_width=True)

            if answered:
                if pick == item["answer"]:
                    st.success("★ CORRECT! +1 XP — " + item["explain"])
                else:
                    st.error("✕ NOT QUITE — " + item["explain"])
                last = i == total - 1
                st.button("SEE SCORE ▸" if last else "NEXT ▸", type="primary",
                          on_click=(lambda: S.update(quiz_done=True)) if last
                          else (lambda: S.update(quiz_i=S.quiz_i + 1, quiz_pick=None)))
    tv_footer()


def video_page():
    top_bar()
    n = len(VIDEOS)
    watched = len(S.video_seen)
    current = VIDEOS[S.video_i]

    def select(k):
        S.video_i = k % n
        S.video_playing = False

    def play():
        S.video_playing = True
        S.video_seen.add(S.video_i)

    player, playlist = st.columns([2.2, 1], gap="large")

    with player:
        st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-top:14px'>"
                    f"<h2 style='font-size:20px;margin:0'>NOW PLAYING</h2><span class='tag'>{current['tag']}</span></div>",
                    unsafe_allow_html=True)
        if S.video_playing and current["url"]:
            st.video(current["url"])
        else:
            text = "[ YOUR VIDEO PLAYS HERE ]" if S.video_playing else "PRESS PLAY"
            st.markdown(f"<div class='video-screen'><div class='play'>▶</div>"
                        f"<span class='pixel' style='color:#D3EAE2;font-size:14px'>{text}</span></div>",
                        unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:24px;font-weight:700;margin:16px 0 4px'>"
                    f"{current['title']}</p><p class='sub' style='font-size:17px'>{current['desc']}</p>",
                    unsafe_allow_html=True)
        a, b, c, d = st.columns(4)
        a.button("▶ PLAY", type="primary", use_container_width=True, on_click=play)
        b.button("◂ PREV", use_container_width=True, on_click=select, args=(S.video_i - 1,))
        c.button("NEXT ▸", use_container_width=True, on_click=select, args=(S.video_i + 1,))
        d.button("TAKE THE QUIZ", use_container_width=True, on_click=go, args=("quiz",))

    with playlist:
        st.markdown(f"<h2 style='font-size:16px;margin:14px 0 4px'>PLAYLIST</h2>"
                    f"<div class='pixel sub' style='font-size:11px'>WATCHED {watched} OF {n}</div>"
                    f"<div class='score-bar'><div class='score-fill' style='width:{round(watched / n * 100)}%'></div></div>",
                    unsafe_allow_html=True)
        for k, v in enumerate(VIDEOS):
            mark = "▶ " if k == S.video_i else ("✓ " if k in S.video_seen else "")
            st.button(f"{k + 1:02d} · {mark}{v['title']}", key=f"vid_{k}", on_click=select, args=(k,),
                      type="primary" if k == S.video_i else "secondary", use_container_width=True)
    tv_footer()


# ---------------------------------------------------------------------------
# 9. Show the right page
# ---------------------------------------------------------------------------
inject_css()
{"home": home_page, "quiz": quiz_page, "video": video_page}.get(S.page, home_page)()
