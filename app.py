import base64
import html
import json
from pathlib import Path

import streamlit as st
from ai_engine import (
    QUESTIONS,
    build_agent_plan,
    generate_learning_tasks,
    generate_quiz_from_chat,
    get_quiz_questions_for_topic,
    resolve_active_topic,
    stream_reply,
    transcribe_audio,
)

st.set_page_config(page_title="AiJaga", page_icon="🩺", layout="wide")
CORRECT_ANSWER_SOUND = Path(__file__).parent / "assets" / "correct-answer.mp3"

GREETINGS = {
    "English": "Hi, welcome to AiJaga! I'm Dr. Aijaga. Ask me a health question by typing, adding a photo, or recording a voice note.",
    "Bahasa Melayu": "Hai, selamat datang ke AiJaga! Saya Dr. Aijaga. Tanya soalan kesihatan dengan menaip, menambah gambar atau merakam nota suara.",
    "Mix of both (Manglish)": "Hi, welcome to AiJaga! Saya Dr. Aijaga. Ask me a health question by typing, adding a photo, atau record voice note.",
}

QUICK_QUESTIONS = [
    "Why do I get headaches?",
    "How to lower blood pressure?",
    "First aid for burns",
    "Tips for better sleep",
]

QUIZ_QUESTIONS = [
    {
        "question": "How long should you scrub your hands with soap when washing them?",
        "options": ["About 5 seconds", "At least 20 seconds", "Exactly 2 minutes"],
        "answer": 1,
        "explanation": "Scrub with soap for at least 20 seconds, including the backs of your hands and between your fingers.",
    },
    {
        "question": "What should you do first for a small burn?",
        "options": ["Cool it under cool running water", "Put ice directly on it", "Cover it with butter"],
        "answer": 0,
        "explanation": "Cool the burn under cool running water for 20 minutes. Tell an adult and get medical help for a serious burn.",
    },
    {
        "question": "How much sleep do most teenagers need each night?",
        "options": ["5–6 hours", "8–10 hours", "12–14 hours"],
        "answer": 1,
        "explanation": "Most teenagers need 8–10 hours of sleep each night to support their health and learning.",
    },
    {
        "question": "For a balanced plate, what should fill about half the plate?",
        "options": ["Fruit and vegetables", "Rice and bread", "Meat and fish"],
        "answer": 0,
        "explanation": "A balanced plate includes plenty of fruit and vegetables, alongside grains and protein.",
    },
    {
        "question": "Which can be a sign that you need more fluids?",
        "options": ["Dark urine and feeling thirsty", "Clear vision", "Feeling hungry after a meal"],
        "answer": 0,
        "explanation": "Thirst and darker urine can be signs to drink water. If someone feels very unwell, tell an adult.",
    },
]

VIDEO_LESSONS = [
    {"title": "Fever", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/@Peekaboo_Kidz", "kind": "channel"},
    {"title": "Immune system", "category": "BODY SYSTEMS", "url": "https://www.youtube.com/watch?v=azE3rv5l28Y"},
    {"title": "Drink water", "category": "HYDRATION", "url": "https://www.youtube.com/watch?v=31F0laJjyy8"},
    {"title": "Food pyramid", "category": "FOOD & DIGESTION", "url": "https://www.youtube.com/watch?v=tsgyWIsYvxs"},
    {"title": "Urine color", "category": "HYDRATION", "url": "https://www.youtube.com/watch?v=ka85yQcA524"},
    {"title": "Constipation", "category": "FOOD & DIGESTION", "url": "https://www.youtube.com/watch?v=TK0ZF7FNxsU"},
    {"title": "Period", "category": "BODY SYSTEMS", "url": "https://www.youtube.com/watch?v=PeL_XtBrOxw"},
    {"title": "Liver function", "category": "BODY SYSTEMS", "url": "https://www.youtube.com/watch?v=IMzFgyrUXnE"},
    {"title": "Gut", "category": "FOOD & DIGESTION", "url": "https://www.youtube.com/watch?v=4zLU2UE90jM"},
    {"title": "Digestive system", "category": "FOOD & DIGESTION", "url": "https://www.youtube.com/watch?v=ZBZWgrfZFbU"},
    {"title": "Asthma", "category": "BREATHING & HEART", "url": "https://www.youtube.com/watch?v=s1R0dL1VB0I"},
    {"title": "Allergies", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=sM3FDsMAMdc"},
    {"title": "What is a virus", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=ndDpjT0_IM0"},
    {"title": "Hold urine", "category": "BODY SYSTEMS", "url": "https://www.youtube.com/watch?v=BrCIcqS1yEg"},
    {"title": "How brain works", "category": "BODY SYSTEMS", "url": "https://www.youtube.com/watch?v=ndDpjT0_IM0"},
    {"title": "Cavities", "category": "EVERYDAY HEALTH", "url": "https://www.youtube.com/watch?v=3ZHYQ6f1BhU"},
    {"title": "Respiratory system", "category": "BREATHING & HEART", "url": "https://www.youtube.com/watch?v=mOKmjYwfDGU"},
    {"title": "Urinary function", "category": "BODY SYSTEMS", "url": "https://www.youtube.com/watch?v=dZREDWD_5bA"},
    {"title": "First aid for finger cuts", "category": "FIRST AID", "url": "https://youtu.be/Z3XN4GWANRM"},
    {"title": "Migraine", "category": "COMMON CONDITIONS", "url": "https://youtu.be/wRGxUc-AuUM"},
    {"title": "Depression", "category": "MENTAL HEALTH & LEARNING", "url": "https://youtu.be/0hxFR6tezAc"},
    {"title": "Autism spectrum disorder (ASD)", "category": "MENTAL HEALTH & LEARNING", "url": "https://youtu.be/d2mlWUzA0B4"},
    {"title": "Chickenpox", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=xNc4kEt4pN0"},
    {"title": "Body parts", "category": "BODY SYSTEMS", "url": "https://youtu.be/jd3bWUAa9qM"},
    {"title": "Epilepsy", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=AaBgkBEA9eM"},
    {"title": "Alzheimer's disease", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=5dmqaH-MlA0"},
    {"title": "Dyslexia", "category": "MENTAL HEALTH & LEARNING", "url": "https://www.youtube.com/watch?v=65psPXWzNic"},
    {"title": "Diabetes", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=d86DofYpkrY"},
    {"title": "Pimples", "category": "EVERYDAY HEALTH", "url": "https://www.youtube.com/watch?v=SPQt5v5Xsg8"},
    {"title": "Anger", "category": "MENTAL HEALTH & LEARNING", "url": "https://www.youtube.com/watch?v=clwt7iXF1Mg"},
    {"title": "Spending too much time on your phone", "category": "MENTAL HEALTH & LEARNING", "url": "https://www.youtube.com/watch?v=4v_ybv_U-Dg"},
    {"title": "Stuttering", "category": "MENTAL HEALTH & LEARNING", "url": "https://www.youtube.com/watch?v=juMxqemIlpU"},
    {"title": "How broken bones heal", "category": "FIRST AID", "url": "https://youtu.be/yovH2-Uw7i8"},
    {"title": "Choking", "category": "FIRST AID", "url": "https://www.youtube.com/watch?v=oSZG9JHdngM"},
    {"title": "House fire", "category": "SAFETY", "url": "https://www.youtube.com/watch?v=Xgc90CoJbDI"},
    {"title": "Earthquake", "category": "SAFETY", "url": "https://www.youtube.com/watch?v=MllUVQM3KVk"},
    {"title": "Why people faint", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=2-Dv9P6gLYY"},
    {"title": "Cardiac arrest", "category": "BREATHING & HEART", "url": "https://www.youtube.com/watch?v=41kcmMJQ2ds"},
    {"title": "Heart attack", "category": "BREATHING & HEART", "url": "https://www.youtube.com/watch?v=jP0qT6GpBVY"},
    {"title": "Blood pressure", "category": "BREATHING & HEART", "url": "https://www.youtube.com/watch?v=2HTZs51OYwo"},
    {"title": "Hormones", "category": "BODY SYSTEMS", "url": "https://www.youtube.com/watch?v=_nyvBUmIwhI"},
    {"title": "Kidney stones", "category": "BODY SYSTEMS", "url": "https://youtu.be/xmbpPWIV0VU"},
    {"title": "How muscles grow", "category": "BODY SYSTEMS", "url": "https://www.youtube.com/watch?v=Vnj9Ay6xmOk"},
    {"title": "Flood safety", "category": "SAFETY", "url": "https://www.youtube.com/watch?v=pi_nUPcQz_A"},
    {"title": "Drowning", "category": "FIRST AID", "url": "https://www.youtube.com/watch?v=WKu7_Fwf3PI"},
    {"title": "Wasp sting", "category": "FIRST AID", "url": "https://www.youtube.com/watch?v=8Fz3qvNvLO8"},
    {"title": "Bee sting", "category": "FIRST AID", "url": "https://www.youtube.com/watch?v=H_wj50ox8OY"},
    {"title": "Dengue", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=Oy1eQQZQZvs"},
    {"title": "Tetanus", "category": "COMMON CONDITIONS", "url": "https://www.youtube.com/watch?v=S6rogdxMGww"},
    {"title": "Mouth ulcer", "category": "EVERYDAY HEALTH", "url": "https://www.youtube.com/watch?v=ScAq1VgTml0"},
    {"title": "Rabies", "category": "COMMON CONDITIONS", "url": "https://youtu.be/EAhqjbWpLSI"},
    {"title": "Heat wave safety", "category": "SAFETY", "url": "https://youtu.be/ARB6R51iQ_k"},
    {"title": "Stampede safety", "category": "SAFETY", "url": "https://youtu.be/MSiw9ZGdtSQ"},
]

PROFILE_DEFAULTS = {
    "age_group": "14-15",
    "language": "English",
    "interest": "Everything / not sure yet",
    "knowledge": "Just starting",
    "considerations": "Nothing special",
}

PALETTES = {
    "Bright": {
        "page": "#f2d4a3",
        "screen": "#e9f1ed",
        "panel": "#ffffff",
        "text": "#1c3035",
        "muted": "#597079",
        "line": "#1c3035",
        "accent": "#17685e",
        "accent_text": "#ffffff",
        "soft": "#d8ece8",
        "coral": "#f07b57",
        "frame": "#d7ad72",
    },
    "Dark": {
        "page": "#192c2c",
        "screen": "#203535",
        "panel": "#294242",
        "text": "#eef4ef",
        "muted": "#bdd0cb",
        "line": "#b3c9c4",
        "accent": "#69b6a4",
        "accent_text": "#102b28",
        "soft": "#355653",
        "coral": "#f58b68",
        "frame": "#c99e63",
    },
}


def init_state():
    st.session_state.setdefault("mode", "home")
    st.session_state.setdefault("quiz_index", 0)
    st.session_state.setdefault("quiz_score", 0)
    st.session_state.setdefault("quiz_answered", None)
    st.session_state.setdefault("video_index", 0)
    st.session_state.setdefault("video_category", "ALL")
    st.session_state.setdefault("watched_videos", [])
    st.session_state.setdefault("profile", dict(PROFILE_DEFAULTS))
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("theme", "Bright")
    st.session_state.setdefault("font_scale", 1.0)
    st.session_state.setdefault("read_aloud", False)
    st.session_state.setdefault("auto_start_learning", True)
    st.session_state.setdefault("quiz_questions", get_quiz_questions_for_topic("general health"))
    st.session_state.setdefault(
        "agent_memory",
        {
            "last_topic": "general health",
            "last_goal": "learn",
            "next_mode": "chat",
            "summary": "AI Coach is ready to help you learn.",
            "suggestions": [],
        },
    )
    if not st.session_state.messages:
        language = st.session_state.profile.get("language", "English")
        st.session_state.messages = [{"role": "assistant", "content": GREETINGS[language]}]


def refresh_quiz_from_topic(topic: str | None = None):
    if topic is None:
        topic = resolve_active_topic(
            st.session_state.messages,
            st.session_state.profile,
            st.session_state.mode,
            st.session_state.agent_memory.get("last_topic", "general health"),
        )
    topic_questions = get_quiz_questions_for_topic(topic)
    if topic_questions:
        st.session_state.quiz_questions = topic_questions
    else:
        st.session_state.quiz_questions = QUIZ_QUESTIONS
    st.session_state.agent_memory["last_topic"] = topic
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answered = None


def prepare_quiz_from_chat(topic: str | None = None) -> bool:
    if topic is None:
        topic = st.session_state.agent_memory.get("last_topic", "general health")

    has_conversation = any(
        message.get("role") == "user" for message in st.session_state.messages
    ) and any(message.get("role") == "assistant" for message in st.session_state.messages)

    if has_conversation:
        try:
            questions = generate_quiz_from_chat(
                st.session_state.profile,
                st.session_state.messages,
                topic,
            )
        except (RuntimeError, ValueError) as error:
            st.session_state.quiz_generation_error = str(error)
            return False
    else:
        questions = get_quiz_questions_for_topic(topic) or QUIZ_QUESTIONS

    st.session_state.quiz_questions = questions
    st.session_state.agent_memory["last_topic"] = topic
    st.session_state.quiz_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answered = None
    st.session_state.pop("quiz_generation_error", None)
    return True


def render_quiz_generation_error():
    error = st.session_state.pop("quiz_generation_error", None)
    if error:
        st.error(error)


def sync_agent_memory_from_latest_user_message():
    if not st.session_state.messages:
        return
    last_user_message = ""
    for message in reversed(st.session_state.messages):
        if message.get("role") == "user":
            last_user_message = message.get("content", "")
            break
    if not last_user_message:
        return
    plan = build_agent_plan(st.session_state.profile, st.session_state.messages, st.session_state.mode)
    st.session_state.agent_memory.update(plan)
    st.session_state.agent_memory["last_topic"] = resolve_active_topic(
        st.session_state.messages,
        st.session_state.profile,
        st.session_state.mode,
        plan["topic"],
    )
    refresh_quiz_from_topic(st.session_state.agent_memory["last_topic"])


def apply_styles():
    colors = PALETTES[st.session_state.theme]
    variables = "".join(f"--{name}:{value};" for name, value in colors.items())
    st.markdown(f"<style>:root{{{variables}--text-scale:{st.session_state.font_scale};}}</style>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] { background: var(--page); color: var(--text); }
        [data-testid="stHeader"] { background: transparent; }
        .stMainBlockContainer { max-width: 1500px; padding-top: 1.2rem; padding-bottom: 2rem; }
        .st-key-tv_shell {
            background: var(--screen); border: 8px solid var(--frame); border-radius: 26px;
            padding: 1.1rem 1.25rem 1.35rem; box-shadow: 0 8px 0 rgba(68, 51, 30, .12);
        }
        .st-key-chat_panel { background: var(--panel); border: 3px solid var(--line); padding: 1rem; }
        .brand-title, .section-title, .eyebrow {
            color: var(--text); font-family: "Courier New", monospace; font-weight: 900;
        }
        .brand-title { font-size: 1.6rem; margin: 0; }
        .eyebrow { font-size: .75rem; text-transform: uppercase; }
        .assistant-card, .access-card { background: var(--panel); border: 3px solid var(--line); padding: 1rem; margin-bottom: 1rem; color: var(--text); }
        .assistant-card { text-align: center; }
        .doctor-avatar { font-size: 4.2rem; line-height: 1.2; }
        .doctor-label { display: inline-block; background: var(--coral); border: 2px solid var(--line); padding: .35rem .7rem; font-family: "Courier New", monospace; font-weight: 900; }
        .home-title, .mode-page-title { text-align: center; color: var(--text); font-family: "Courier New", monospace; font-weight: 900; }
        .home-title { font-size: 2rem; margin: 1.2rem 0 .4rem; }
        .mode-page-title { font-size: 1.6rem; margin: 1.2rem 0; }
        .mode-heading { text-align: center; color: var(--muted); font: 900 1rem "Courier New", monospace; margin: .5rem 0 1.5rem; }
        .mode-icon { color: var(--coral); text-align: center; font: 900 3.2rem "Courier New", monospace; padding: .7rem; }
        .mode-title { color: var(--accent); text-align: center; font: 900 1.25rem "Courier New", monospace; margin: .4rem 0; }
        .quiz-card { background: var(--panel); border: 3px solid var(--line); color: var(--text); padding: 1.2rem; margin: 1rem auto; max-width: 900px; }
        .quiz-card h2 { color: var(--text); font-size: 1.35rem; }
        .quiz-score { color: var(--accent); text-align: center; }
        .lesson-player { min-height: 300px; background: #1c3035; border: 3px solid var(--line); color: #eef4ef; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 2rem; }
        .lesson-player .lesson-icon { font-size: 4rem; }
        .lesson-player h2 { color: #eef4ef; }
        .lesson-player p { color: #d3e2dd; max-width: 650px; }
        .lesson-heading { color: var(--text); font: 900 1.1rem "Courier New", monospace; }
        .tv-footer { color: var(--muted); text-align: center; font: 900 .9rem "Courier New", monospace; letter-spacing: .18rem; padding: .5rem 0; }
        .status-online { color: var(--muted); font-size: .75rem; font-weight: 700; }
        .status-online::before { content: ""; display: inline-block; width: .55rem; height: .55rem; margin-right: .4rem; background: #35b86b; }
        .quick-label { color: var(--muted); font-family: "Courier New", monospace; font-size: .72rem; font-weight: 700; }
        [data-testid="stChatMessage"] { background: transparent; }
        [data-testid="stChatMessageContent"] { font-size: calc(1rem * var(--text-scale)); color: var(--text); }
        [data-testid="stChatMessageContent"] p { color: var(--text); }
        button[data-testid="stBaseButton-secondary"] {
            border: 2px solid var(--line) !important; border-radius: 2px !important;
            color: var(--text) !important; background: var(--soft) !important; font-weight: 700;
        }
        button[data-testid="stBaseButton-primary"] {
            border: 2px solid var(--line) !important; border-radius: 2px !important;
            color: var(--accent_text) !important; background: var(--accent) !important;
        }
        [data-testid="stChatInput"] { border: 2px solid var(--line); background: var(--panel) !important; }
        [data-testid="stChatInput"] [data-baseweb="textarea"] { background: var(--panel) !important; }
        [data-testid="stChatInput"] textarea { color: var(--text) !important; background: transparent !important; }
        [data-testid="stChatInput"] button { color: var(--text) !important; background: var(--soft) !important; }
        [role="progressbar"] [data-testid="stProgressBarTrack"] { background: var(--panel) !important; }
        [role="progressbar"] [data-testid="stProgressBarTrack"] > div { background: var(--coral) !important; }
        [data-testid="stCaptionContainer"] p, .stMarkdown p { color: var(--muted); }
        @media (max-width: 700px) {
            .st-key-tv_shell { border-width: 5px; border-radius: 16px; padding: .65rem; }
            .stMainBlockContainer { padding-left: .5rem; padding-right: .5rem; }
            .brand-title { font-size: 1.2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def listen_button(text: str, auto_play: bool, key: int, label: str = "🔊 Listen"):
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    autoplay = "true" if auto_play else "false"
    st.iframe(
        f"""
        <button id="listen-{key}" data-text="{encoded}" style="border:2px solid #597079;background:#d8ece8;padding:8px 14px;font-weight:700;cursor:pointer;">
            {label}
        </button>
        <script>
        const button = document.getElementById("listen-{key}");
        const speak = () => {{
            const bytes = Uint8Array.from(atob(button.dataset.text), character => character.charCodeAt(0));
            const utterance = new SpeechSynthesisUtterance(new TextDecoder().decode(bytes));
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        }};
        button.addEventListener("click", speak);
        if ({autoplay} && "speechSynthesis" in window) speak();
        </script>
        """,
        height=42,
        alt="Listen to this response",
    )


def render_message(message: dict, index: int, latest_assistant: bool):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("image"):
            st.image(message["image"]["data"], width=260)
        if message["role"] == "assistant":
            listen_button(message["content"], st.session_state.read_aloud and latest_assistant, index)


def update_profile():
    profile = st.session_state.profile
    st.markdown(
        """
        <div class="assistant-card">
            <div class="doctor-avatar">🧑🏻‍⚕️</div>
            <div class="doctor-label">DR. AIJAGA</div>
            <p>Your friendly medical assistant.<br>Ask about health, first aid, food, or exercise.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Personalize your assistant"):
        for question in QUESTIONS:
            current = profile.get(question["key"], question["options"][0])
            selected = st.selectbox(
                question["question"],
                question["options"],
                index=question["options"].index(current),
                key=f"profile_{question['key']}",
            )
            profile[question["key"]] = selected
        if not any(message["role"] == "user" for message in st.session_state.messages):
            st.session_state.messages[0]["content"] = GREETINGS[profile["language"]]

    st.markdown('<div class="access-card"><div class="eyebrow">Accessibility</div></div>', unsafe_allow_html=True)
    font_scales = [0.9, 1.0, 1.15]
    scale_index = min(range(len(font_scales)), key=lambda index: abs(font_scales[index] - st.session_state.font_scale))
    st.write(f"Text size: {['Small', 'Normal', 'Large'][scale_index]}")
    smaller, larger = st.columns(2)
    if smaller.button("A−", use_container_width=True, help="Decrease text size"):
        st.session_state.font_scale = font_scales[max(0, scale_index - 1)]
        st.rerun()
    if larger.button("A+", use_container_width=True, help="Increase text size"):
        st.session_state.font_scale = font_scales[min(len(font_scales) - 1, scale_index + 1)]
        st.rerun()
    st.checkbox("Read replies aloud", key="read_aloud")
    st.caption("Press Enter to send. Use Tab to move between controls.")


def render_agent_panel():
    plan = build_agent_plan(st.session_state.profile, st.session_state.messages, st.session_state.mode)
    st.session_state.agent_memory.update(plan)
    st.session_state.agent_memory["last_topic"] = plan["topic"]

    st.markdown(
        f"""
        <div class="assistant-card">
            <div class="eyebrow">AI COACH</div>
            <div class="doctor-label">{plan['topic'].title()}</div>
            <p>{plan['summary']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.checkbox("Auto-start a quiz when I ask to practise", key="auto_start_learning")
    st.caption("Learning requests stay in chat. Quizzes only start when you explicitly ask to practise.")

    suggestions = plan["suggestions"]
    if suggestions:
        columns = st.columns(min(3, len(suggestions)))
        for index, suggestion in enumerate(suggestions):
            if columns[index].button(suggestion["label"], use_container_width=True):
                if suggestion["target"] == "quiz":
                    if not prepare_quiz_from_chat(plan["topic"]):
                        break
                st.session_state.mode = suggestion["target"]
                if suggestion["target"] == "video":
                    st.session_state.video_index = 0
                st.rerun()
    render_quiz_generation_error()


def render_agent_status():
    topic = st.session_state.agent_memory.get("last_topic", "general health")
    st.caption(f"AI Coach focus: {topic.title()}")


def render_todo_tab_link():
    st.html(
        """
        <div style="text-align:right;margin:0.25rem 0 0.75rem;">
          <a id="todo-popup-link" href="?view=todo" target="_blank" rel="noopener noreferrer"
             style="display:inline-block;padding:7px 12px;border:1px solid #1c3035;background:#d8ece8;color:#1c3035;font-weight:700;text-decoration:none;">
            📝 Open learning To-do list ↗
          </a>
        </div>
        <script>
        (() => {
          const link = document.getElementById("todo-popup-link");
          if (!link) return;
          link.addEventListener("click", (event) => {
            const width = Math.min(520, screen.availWidth || 520);
            const height = Math.min(700, screen.availHeight || 700);
            const popup = window.open(
              link.href,
              "aijagaLearningTodo",
              `popup=yes,width=${width},height=${height},resizable=yes,scrollbars=yes`
            );
            if (popup) {
              event.preventDefault();
              popup.opener = null;
            }
          });
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_todo_suggestion_sync(tasks: list[str]):
    if not tasks:
        return
    encoded_tasks = (
        json.dumps(tasks, ensure_ascii=True)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    st.html(
        f"""
        <script>
        (() => {{
          const storageKey = "aijaga:learning-todos:v1";
          const suggestions = {encoded_tasks};
          try {{
            const stored = localStorage.getItem(storageKey);
            const todos = stored ? JSON.parse(stored) : [];
            if (!Array.isArray(todos)) throw new Error("Saved to-do list is not a list.");
            const existing = new Set(todos.map((todo) => String(todo.text || "").trim().toLowerCase()));
            const now = new Date().toISOString();
            suggestions.forEach((text) => {{
              const normalized = text.trim().toLowerCase();
              if (!normalized || existing.has(normalized)) return;
              todos.push({{
                id: `suggested-${{Date.now()}}-${{Math.random().toString(36).slice(2)}}`,
                text,
                done: false,
                createdAt: now,
                source: "AiJaga"
              }});
              existing.add(normalized);
            }});
            localStorage.setItem(storageKey, JSON.stringify(todos));
          }} catch (error) {{
            console.error("Could not save AiJaga learning tasks:", error);
          }}
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_todo_page():
    st.title("📝 AiJaga Learning To-do List")
    st.caption(
        "Suggested tasks use your latest chat question and AiJaga's reply. "
        "You can add, complete, or remove tasks."
    )
    st.caption("Saved only in this browser on this device. Tasks are not synced across devices.")
    st.html(
        """
        <div id="todo-root" style="max-width:480px;margin:0 auto;">
          <div style="display:flex;gap:8px;margin:16px 0;">
            <input id="todo-input" aria-label="New learning task" maxlength="120"
              placeholder="Add your own learning task…" required
              style="flex:1;min-width:0;padding:10px;border:1px solid #597079;border-radius:4px;background:#fff;color:#1c3035;color-scheme:light;box-sizing:border-box;">
            <button id="todo-add" type="button"
              style="padding:10px 16px;border:1px solid #1c3035;background:#d8ece8;color:#1c3035;font-weight:700;cursor:pointer;">
              Add task
            </button>
          </div>
          <p id="todo-status" role="status" aria-live="polite"></p>
          <div id="todo-list"></div>
          <p style="font-size:12px;color:#597079;margin-top:18px;">
            Suggestions are for health learning only, not medical care or treatment advice.
          </p>
          <a href="/" style="color:#17685e;font-weight:700;">Return to AiJaga</a>
        </div>
        <script>
        (() => {
          const storageKey = "aijaga:learning-todos:v1";
          const list = document.getElementById("todo-list");
          const status = document.getElementById("todo-status");
          const input = document.getElementById("todo-input");
          const addButton = document.getElementById("todo-add");
          let todos = [];

          const save = () => {
            try {
              localStorage.setItem(storageKey, JSON.stringify(todos));
              status.textContent = "";
              return true;
            } catch (error) {
              console.error("Could not save the learning to-do list:", error);
              status.textContent = "Could not save changes in this browser. Check storage permissions or available space.";
              return false;
            }
          };

          const load = () => {
            try {
              const stored = localStorage.getItem(storageKey);
              const parsed = stored ? JSON.parse(stored) : [];
              if (!Array.isArray(parsed)) throw new Error("Saved to-do list is not a list.");
              todos = parsed.filter((todo) =>
                todo && typeof todo.id === "string" && typeof todo.text === "string"
              );
              return true;
            } catch (error) {
              console.error("Could not read the learning to-do list:", error);
              status.textContent = "Could not read saved tasks in this browser. The saved data was left unchanged.";
              return false;
            }
          };

          const render = () => {
            list.replaceChildren();
            if (!todos.length) {
              const empty = document.createElement("p");
              empty.textContent = "No tasks yet. Ask AiJaga to explain a health topic, or add your own task.";
              list.append(empty);
              return;
            }
            todos.forEach((todo) => {
              const row = document.createElement("div");
              row.style.cssText = "display:flex;align-items:center;gap:10px;padding:12px;margin:8px 0;border:1px solid #597079;border-radius:4px;";
              const checkbox = document.createElement("input");
              checkbox.type = "checkbox";
              checkbox.checked = Boolean(todo.done);
              checkbox.setAttribute("aria-label", `Mark ${todo.text} complete`);
              checkbox.addEventListener("change", () => {
                todo.done = checkbox.checked;
                save();
                render();
              });
              const text = document.createElement("span");
              text.textContent = todo.text;
              text.style.cssText = "flex:1;overflow-wrap:anywhere;";
              if (todo.done) text.style.textDecoration = "line-through";
              const remove = document.createElement("button");
              remove.type = "button";
              remove.textContent = "Remove";
              remove.addEventListener("click", () => {
                todos = todos.filter((item) => item.id !== todo.id);
                save();
                render();
              });
              remove.style.cssText = "padding:6px 9px;border:1px solid #597079;background:#fff;color:#1c3035;font-weight:700;cursor:pointer;";
              row.append(checkbox, text, remove);
              list.append(row);
            });
          };

          const addTask = () => {
            const text = input.value.trim();
            if (!text) return;
            todos.push({
              id: `user-${Date.now()}-${Math.random().toString(36).slice(2)}`,
              text: text.slice(0, 120),
              done: false,
              createdAt: new Date().toISOString(),
              source: "User"
            });
            if (save()) {
              input.value = "";
              render();
            }
          };
          addButton.addEventListener("click", addTask);
          input.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              addTask();
            }
          });

          window.addEventListener("storage", (event) => {
            if (event.key === storageKey && load()) render();
          });
          window.addEventListener("focus", () => {
            if (load()) render();
          });
          if (load()) render();
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_nearby_hospital_finder():
    st.html(
        """
        <div style="font-family: sans-serif; color: #1c3035;">
          <button id="find-hospitals" style="width:100%;padding:10px;border:2px solid #1c3035;background:#d8ece8;font-weight:700;cursor:pointer;">
            Find nearby hospitals
          </button>
          <p id="hospital-status" role="status" style="font-size:13px;margin:8px 0;"></p>
          <div id="hospital-results" style="display:none;"></div>
          <p style="font-size:12px;color:#597079;margin:8px 0 0;">
            Location is requested only after you click. AiJaga does not receive or save it.
            OpenStreetMap receives your coordinates to find hospitals, and Google Maps receives them
            to show the map or directions. Hospital data may be incomplete. Emergencies: call 999.
          </p>
        </div>
        <script>
        (() => {
        const findButton = document.getElementById("find-hospitals");
        const status = document.getElementById("hospital-status");
        const results = document.getElementById("hospital-results");
        const distanceKm = (latitudeA, longitudeA, latitudeB, longitudeB) => {
          const radians = (degrees) => degrees * Math.PI / 180;
          const latitudeDifference = radians(latitudeB - latitudeA);
          const longitudeDifference = radians(longitudeB - longitudeA);
          const value = Math.sin(latitudeDifference / 2) ** 2
            + Math.cos(radians(latitudeA)) * Math.cos(radians(latitudeB))
            * Math.sin(longitudeDifference / 2) ** 2;
          return 6371 * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value));
        };
        const renderHospitalResults = (hospitals, latitude, longitude) => {
          const heading = document.createElement("h3");
          heading.textContent = "Nearest hospitals";
          heading.style.cssText = "font-size:16px;margin:12px 0 6px;";
          const note = document.createElement("p");
          note.textContent = "Sorted by straight-line distance; actual travel distance and availability may differ.";
          note.style.cssText = "font-size:12px;margin:0 0 8px;";
          const list = document.createElement("div");
          list.style.cssText = "display:grid;gap:8px;margin-bottom:12px;";
          hospitals.slice(0, 5).forEach((hospital, index) => {
            const result = document.createElement("a");
            const directions = new URL("https://www.google.com/maps/dir/");
            directions.searchParams.set("api", "1");
            directions.searchParams.set("origin", `${latitude},${longitude}`);
            directions.searchParams.set("destination", `${hospital.latitude},${hospital.longitude}`);
            directions.searchParams.set("travelmode", "driving");
            result.href = directions.toString();
            result.target = "_blank";
            result.rel = "noopener noreferrer";
            result.style.cssText = "display:block;padding:10px;border:1px solid #597079;border-radius:4px;color:#17685e;text-decoration:none;";
            const name = document.createElement("strong");
            name.textContent = `${index === 0 ? "Nearest: " : ""}${hospital.name}`;
            const distance = document.createElement("span");
            distance.textContent = ` · ${hospital.distance.toFixed(1)} km away`;
            result.append(name, distance);
            if (hospital.address) {
              const address = document.createElement("div");
              address.textContent = hospital.address;
              address.style.cssText = "font-size:12px;margin-top:4px;color:#597079;";
              result.append(address);
            }
            list.append(result);
          });
          const attribution = document.createElement("p");
          attribution.textContent = "Hospital locations: OpenStreetMap contributors.";
          attribution.style.cssText = "font-size:11px;color:#597079;margin:0 0 10px;";
          results.append(heading, note, list, attribution);
        };
        findButton.addEventListener("click", () => {
          results.style.display = "none";
          results.replaceChildren();
          if (!navigator.geolocation) {
            status.textContent = "Location is not supported by this browser. Search for hospitals in your maps app.";
            return;
          }
          findButton.disabled = true;
          status.textContent = "Requesting your location permission…";
          navigator.geolocation.getCurrentPosition(
            async (position) => {
              const { latitude, longitude } = position.coords;
              const location = `${latitude},${longitude}`;
              status.textContent = "Searching for nearby hospitals…";
              const map = document.createElement("iframe");
              map.title = "Nearby hospital search map";
              map.src = `https://www.google.com/maps?q=hospitals+near+${location}&output=embed`;
              map.loading = "lazy";
              map.referrerPolicy = "no-referrer-when-downgrade";
              map.allowFullscreen = true;
              map.style.cssText = "width:100%;height:360px;border:1px solid #597079;border-radius:4px;";
              results.append(map);
              results.style.display = "block";
              try {
                const query = `[out:json][timeout:20];(nwr["amenity"="hospital"](around:20000,${latitude},${longitude});nwr["healthcare"="hospital"](around:20000,${latitude},${longitude}););out center tags;`;
                const endpoint = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;
                const response = await fetch(endpoint);
                if (!response.ok) {
                  throw new Error(`Hospital search returned HTTP ${response.status}`);
                }
                const data = await response.json();
                const seen = new Set();
                const hospitals = (data.elements || []).flatMap((element) => {
                  const key = `${element.type}/${element.id}`;
                  if (seen.has(key)) return [];
                  seen.add(key);
                  const hospitalLatitude = element.lat ?? element.center?.lat;
                  const hospitalLongitude = element.lon ?? element.center?.lon;
                  if (!Number.isFinite(hospitalLatitude) || !Number.isFinite(hospitalLongitude)) return [];
                  const tags = element.tags || {};
                  const name = tags.name || tags["name:en"] || tags["name:ms"];
                  if (!name) return [];
                  const address = [tags["addr:street"], tags["addr:city"] || tags["addr:town"]]
                    .filter(Boolean)
                    .join(", ");
                  return [{
                    name,
                    address,
                    latitude: hospitalLatitude,
                    longitude: hospitalLongitude,
                    distance: distanceKm(latitude, longitude, hospitalLatitude, hospitalLongitude)
                  }];
                }).sort((hospitalA, hospitalB) => hospitalA.distance - hospitalB.distance);
                if (hospitals.length) {
                  renderHospitalResults(hospitals, latitude, longitude);
                  status.textContent = `Found ${hospitals.length} nearby hospitals. Showing the closest ${Math.min(hospitals.length, 5)}.`;
                } else {
                  status.textContent = "No named hospitals were found within 20 km. The map is still available; try searching there or widening your area.";
                }
              } catch (error) {
                console.error("Nearby hospital search failed:", error);
                status.textContent = "Could not load hospital names and distances. The map is still available; try again later.";
              } finally {
                findButton.disabled = false;
              }
            },
            (error) => {
              const messages = {
                1: "Location permission was denied. Allow location access in your browser, or search in your maps app.",
                2: "Your location could not be determined. Try again or search in your maps app.",
                3: "The location request timed out. Try again or search in your maps app."
              };
              status.textContent = messages[error.code] || "Could not get your location. Search in your maps app.";
              findButton.disabled = false;
            },
            { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
          );
        });
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def select_video_for_topic(topic: str):
    preferred_categories = {
        "first aid": ("FIRST AID",),
        "nutrition": ("FOOD & DIGESTION",),
        "hydration": ("HYDRATION",),
        "digestive health": ("FOOD & DIGESTION",),
        "heart & circulation": ("BREATHING & HEART",),
        "respiratory health": ("BREATHING & HEART",),
        "brain & nervous system": ("BODY SYSTEMS", "COMMON CONDITIONS"),
        "skin & allergies": ("COMMON CONDITIONS", "EVERYDAY HEALTH"),
        "infectious diseases": ("COMMON CONDITIONS",),
        "oral health": ("EVERYDAY HEALTH",),
        "mental health": ("MENTAL HEALTH & LEARNING",),
        "sleep": ("MENTAL HEALTH & LEARNING",),
        "fitness": ("BODY SYSTEMS",),
        "body systems": ("BODY SYSTEMS",),
        "everyday health": ("COMMON CONDITIONS", "EVERYDAY HEALTH"),
    }
    categories = preferred_categories.get(topic, ())
    for category in categories:
        for index, lesson in enumerate(VIDEO_LESSONS):
            if lesson["category"] == category:
                st.session_state.video_index = index
                st.session_state.video_category = "ALL"
                return
    st.session_state.video_index = 0
    st.session_state.video_category = "ALL"


def render_topbar(progress_label: str, progress_value: float, show_home: bool = False):
    if show_home:
        home, brand, progress, bright, dark = st.columns(
            [0.65, 1.0, 1.6, 0.55, 0.55], vertical_alignment="center"
        )
        if home.button("◂ HOME", use_container_width=True):
            st.session_state.mode = "home"
            st.rerun()
    else:
        brand, progress, bright, dark = st.columns(
            [1.1, 1.6, 0.55, 0.55], vertical_alignment="center"
        )

    with brand:
        st.markdown('<div class="brand-title">🩺 AIJAGA</div>', unsafe_allow_html=True)
    with progress:
        st.markdown(f'<div class="eyebrow">{progress_label}</div>', unsafe_allow_html=True)
        st.progress(max(0.0, min(progress_value, 1.0)))
    if bright.button("BRIGHT", use_container_width=True, type="primary" if st.session_state.theme == "Bright" else "secondary"):
        st.session_state.theme = "Bright"
        st.rerun()
    if dark.button("DARK", use_container_width=True, type="primary" if st.session_state.theme == "Dark" else "secondary"):
        st.session_state.theme = "Dark"
        st.rerun()
    render_todo_tab_link()


def home_screen():
    with st.container(key="tv_shell"):
        render_topbar("LEVEL 1 · HEALTH HERO", 0.3)

        doctor, welcome = st.columns([0.36, 0.64], gap="large", vertical_alignment="center")
        with doctor:
            st.markdown(
                """
                <div class="assistant-card">
                    <div class="doctor-avatar">🧑🏻‍⚕️</div>
                    <div class="doctor-label">DR. AIJAGA</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with welcome:
            st.markdown('<div class="section-title">DR. AIJAGA</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="access-card">I am Dr. AiJaga, ready to help you! Pick a mode below to press start.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<h1 class="home-title">HI, WELCOME TO AIJAGA</h1>', unsafe_allow_html=True)
        coach_plan = build_agent_plan(st.session_state.profile, st.session_state.messages, "home")
        st.session_state.agent_memory.update(coach_plan)
        st.session_state.agent_memory["last_topic"] = coach_plan["topic"]
        st.markdown(
            f'<div class="assistant-card"><div class="eyebrow">AI COACH</div><p>{coach_plan["summary"]}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="mode-heading">CHOOSE YOUR MODE...</div>', unsafe_allow_html=True)
        modes = [
            ("chat", "▣", "CHAT-BOX", "Ask Dr. AiJaga anything by text, photo or voice"),
            ("quiz", "?", "QUIZ", "Test your health knowledge and level up"),
            ("video", "▶", "VIDEO", "Watch short health and first-aid lessons"),
        ]
        columns = st.columns(3, gap="medium")
        for column, (mode, icon, title, description) in zip(columns, modes):
            with column:
                with st.container(border=True):
                    st.markdown(f'<div class="mode-icon">{icon}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="mode-title">{title}</div>', unsafe_allow_html=True)
                    st.caption(description)
                    if st.button("PRESS START", key=f"start_{mode}", use_container_width=True):
                        if mode == "quiz":
                            if not prepare_quiz_from_chat(st.session_state.agent_memory.get("last_topic", "general health")):
                                continue
                        st.session_state.mode = mode
                        if mode == "video":
                            st.session_state.video_index = 0
                        st.rerun()

        render_quiz_generation_error()
        render_nearby_hospital_finder()
        st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999.")
        st.markdown('<div class="tv-footer">AIJAGA TV</div>', unsafe_allow_html=True)


def quiz_screen():
    questions = st.session_state.get("quiz_questions", QUIZ_QUESTIONS)
    question_index = st.session_state.quiz_index
    score = st.session_state.quiz_score
    total_questions = len(questions)
    with st.container(key="tv_shell"):
        render_topbar(
            f"SCORE {score} / {total_questions} · QUESTION {min(question_index + 1, total_questions)} OF {total_questions}",
            question_index / total_questions if total_questions else 0.0,
            show_home=True,
        )
        st.markdown('<h1 class="mode-page-title">[ ? ] HEALTH QUIZ</h1>', unsafe_allow_html=True)
        render_agent_status()
        auto_started = st.session_state.pop("auto_started_activity", None)
        if auto_started:
            st.info(auto_started)

        if question_index >= total_questions:
            st.markdown('<div class="quiz-card">QUIZ COMPLETE</div>', unsafe_allow_html=True)
            st.markdown(f'<h2 class="quiz-score">Your score: {score} / {total_questions}</h2>', unsafe_allow_html=True)
            st.write("Every question is a chance to learn something useful. You can play again whenever you like.")
            replay, home = st.columns(2)
            if replay.button("PLAY AGAIN", use_container_width=True):
                if prepare_quiz_from_chat(st.session_state.agent_memory.get("last_topic", "general health")):
                    st.rerun()
            if home.button("HOME", use_container_width=True):
                st.session_state.mode = "home"
                st.rerun()
            render_quiz_generation_error()
        else:
            question = questions[question_index]
            st.markdown(
                f'<div class="quiz-card"><div class="doctor-label">QUESTION {question_index + 1} OF {total_questions}</div>'
                f'<h2>{html.escape(question["question"])}</h2></div>',
                unsafe_allow_html=True,
            )
            answered = st.session_state.quiz_answered
            locked = answered is not None and answered["index"] == question_index
            selected = st.radio(
                "Choose one answer",
                question["options"],
                index=answered["selected"] if locked else None,
                key=f"quiz_answer_{question_index}",
                label_visibility="collapsed",
                disabled=locked,
            )
            if not locked and st.button("CHECK ANSWER", disabled=selected is None, type="primary"):
                selected_index = question["options"].index(selected)
                correct = selected_index == question["answer"]
                st.session_state.quiz_answered = {
                    "index": question_index,
                    "selected": selected_index,
                    "correct": correct,
                }
                if correct:
                    st.session_state.quiz_score += 1
                st.rerun()

            if locked:
                if answered["correct"]:
                    st.success("Correct! " + question["explanation"])
                    st.audio(CORRECT_ANSWER_SOUND.read_bytes(), format="audio/mp3", autoplay=True)
                else:
                    st.info("Good try. " + question["explanation"])
                if st.button("SEE RESULTS" if question_index == total_questions - 1 else "NEXT QUESTION", type="primary"):
                    st.session_state.quiz_index += 1
                    st.session_state.quiz_answered = None
                    st.rerun()

        st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999.")
        st.markdown('<div class="tv-footer">AIJAGA TV</div>', unsafe_allow_html=True)


def video_screen():
    watched = st.session_state.watched_videos
    categories = ["ALL"] + sorted({item["category"] for item in VIDEO_LESSONS})
    category = st.session_state.video_category
    visible_indices = [
        index for index, item in enumerate(VIDEO_LESSONS)
        if category == "ALL" or item["category"] == category
    ]
    if st.session_state.video_index not in visible_indices:
        st.session_state.video_index = visible_indices[0]

    with st.container(key="tv_shell"):
        render_topbar(f"WATCHED {len(watched)} OF {len(VIDEO_LESSONS)} VIDEOS", len(watched) / len(VIDEO_LESSONS), show_home=True)
        render_agent_status()
        auto_started = st.session_state.pop("auto_started_activity", None)
        if auto_started:
            st.info(auto_started)
        player, playlist = st.columns([0.72, 0.28], gap="medium")
        with player:
            st.markdown('<div class="lesson-heading">NOW PLAYING</div>', unsafe_allow_html=True)
            lesson_index = st.session_state.video_index
            lesson = VIDEO_LESSONS[lesson_index]
            if lesson.get("kind") == "channel":
                st.markdown(
                    '<div class="lesson-player"><div class="lesson-icon">▶</div>'
                    '<h2>Fever videos</h2><p>Open the Peekaboo Kidz channel to choose a fever explainer.</p></div>',
                    unsafe_allow_html=True,
                )
                st.link_button("OPEN FEVER VIDEOS", lesson["url"], use_container_width=True)
            else:
                st.video(lesson["url"], autoplay=False)
                st.link_button("OPEN ON YOUTUBE", lesson["url"])
                st.caption("If playback fails in this browser, open the video directly on YouTube.")
            st.markdown(f"### {lesson['title']}")
            st.caption("This is a user-provided YouTube link and has not been medically reviewed by AiJaga. Use it for learning, and check important health advice with a trusted adult or health professional.")

            position = visible_indices.index(lesson_index)
            previous, next_video, complete = st.columns([0.9, 0.9, 1.3])
            if previous.button("◂ PREV", disabled=position == 0, use_container_width=True):
                st.session_state.video_index = visible_indices[position - 1]
                st.rerun()
            if next_video.button("NEXT ▸", disabled=position == len(visible_indices) - 1, use_container_width=True):
                st.session_state.video_index = visible_indices[position + 1]
                st.rerun()
            is_watched = lesson_index in watched
            if complete.button(
                "✓ WATCHED" if is_watched else "MARK WATCHED",
                disabled=is_watched,
                use_container_width=True,
            ):
                st.session_state.watched_videos.append(lesson_index)
                st.rerun()

            if st.button("TAKE THE QUIZ", type="primary"):
                if prepare_quiz_from_chat(st.session_state.agent_memory.get("last_topic", "general health")):
                    st.session_state.mode = "quiz"
                    st.rerun()
            render_quiz_generation_error()
        with playlist:
            st.markdown('<div class="lesson-heading">PLAYLIST</div>', unsafe_allow_html=True)
            st.selectbox("Filter playlist", categories, key="video_category")
            with st.container(height=500, border=False):
                for index in visible_indices:
                    item = VIDEO_LESSONS[index]
                    status = "✓" if index in watched else f"{index + 1:02}"
                    if st.button(
                        f"{status}  {item['title']}\n{item['category']}",
                        key=f"lesson_{index}",
                        use_container_width=True,
                        type="primary" if index == st.session_state.video_index else "secondary",
                    ):
                        st.session_state.video_index = index
                        st.rerun()

        st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999.")
        st.markdown('<div class="tv-footer">AIJAGA TV</div>', unsafe_allow_html=True)


def chat():
    with st.container(key="tv_shell"):
        turns = sum(message["role"] == "user" for message in st.session_state.messages)
        render_topbar(f"LEVEL {turns // 5 + 1} · HEALTH HERO", (turns % 5) / 5, show_home=True)

        left, right = st.columns([0.32, 0.68], gap="medium")
        with left:
            update_profile()
            render_agent_panel()
            render_nearby_hospital_finder()
            st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999 / 112.")

        with right:
            with st.container(key="chat_panel"):
                title, status = st.columns([0.75, 0.25], vertical_alignment="center")
                title.markdown('<div class="section-title">HI, WELCOME TO AIJAGA</div>', unsafe_allow_html=True)
                status.markdown('<div class="status-online">DR. AIJAGA IS ONLINE</div>', unsafe_allow_html=True)
                st.divider()

                with st.container(height=420, border=False):
                    messages = st.session_state.messages
                    for index, message in enumerate(messages):
                        render_message(
                            message,
                            index,
                            index == len(messages) - 1 and message["role"] == "assistant",
                        )
                    live_turn = st.empty()

                st.markdown('<div class="quick-label">QUICK QUESTIONS · SWIPE OR SCROLL SIDEWAYS →</div>', unsafe_allow_html=True)
                quick_cols = st.columns(4)
                quick_prompt = None
                for index, question in enumerate(QUICK_QUESTIONS):
                    if quick_cols[index].button(question, key=f"quick_{index}", use_container_width=True):
                        quick_prompt = question

                entry = st.chat_input(
                    "Type your healthcare question here...",
                    accept_file=True,
                    file_type=["png", "jpg", "jpeg", "webp"],
                    accept_audio=True,
                    max_upload_size=10,
                )

                prompt = quick_prompt
                image = None
                image_for_display = None
                if entry is not None:
                    prompt = entry.text.strip()
                    if entry.audio is not None:
                        try:
                            transcript = transcribe_audio(entry.audio.getvalue(), entry.audio.type or "audio/wav")
                            prompt = f"{prompt}\n{transcript}".strip()
                        except Exception:
                            st.error("I couldn't transcribe that voice note. Please try recording it again or type your question.")
                            prompt = None
                    if entry.files:
                        upload = entry.files[0]
                        image = (upload.getvalue(), upload.type or "image/jpeg")
                        image_for_display = {"data": image[0], "mime_type": image[1]}
                        if not prompt:
                            prompt = "Please describe this image and share general health information. Do not diagnose."

                if prompt:
                    user_message = {"role": "user", "content": prompt}
                    if image_for_display:
                        user_message["image"] = image_for_display
                    st.session_state.messages.append(user_message)
                    sync_agent_memory_from_latest_user_message()
                    with live_turn.container():
                        render_message(user_message, len(st.session_state.messages) - 1, False)
                        with st.chat_message("assistant"):
                            reply = st.write_stream(
                                stream_reply(st.session_state.profile, st.session_state.messages, image=image)
                            )
                            listen_button(reply, st.session_state.read_aloud, len(st.session_state.messages))
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    plan = st.session_state.agent_memory
                    if not reply.lstrip().startswith("⚠️"):
                        try:
                            suggestions = generate_learning_tasks(
                                st.session_state.profile,
                                st.session_state.messages,
                                prompt,
                                plan.get("topic", "general health"),
                            )
                            if suggestions:
                                st.session_state.pending_todo_suggestions = suggestions
                        except RuntimeError as error:
                            st.warning(str(error))
                    if (
                        st.session_state.auto_start_learning
                        and plan.get("auto_start")
                        and not reply.lstrip().startswith("⚠️")
                    ):
                        next_mode = plan["next_mode"]
                        if next_mode == "quiz":
                            if prepare_quiz_from_chat(plan["topic"]):
                                st.session_state.auto_started_activity = (
                                    f"AiJaga started a {plan['topic']} quiz based on your chat. "
                                    "Use HOME to return to chat or stop."
                                )
                                st.session_state.mode = next_mode
                        else:
                            select_video_for_topic(plan["topic"])
                            st.session_state.auto_started_activity = (
                                f"AiJaga selected a {plan['topic']} lesson based on your request. "
                                "Use HOME to return to chat or stop."
                            )
                            st.session_state.mode = next_mode
                    st.rerun()


init_state()
apply_styles()
pending_todo_suggestions = st.session_state.pop("pending_todo_suggestions", [])
if pending_todo_suggestions:
    render_todo_suggestion_sync(pending_todo_suggestions)

if st.query_params.get("view") == "todo":
    render_todo_page()
elif st.session_state.mode == "home":
    home_screen()
elif st.session_state.mode == "chat":
    chat()
elif st.session_state.mode == "quiz":
    quiz_screen()
elif st.session_state.mode == "video":
    video_screen()
