"""
AiJaga Videos
-------------
Adds the VIDEO feature to the existing quiz page.
Keep this file next to aijaga_quiz.py. It imports PAGE from there,
injects the video code, and exports a new PAGE.

Chain:  aijaga_quiz.py  ->  aijaga_video.py  ->  streamlit_app.py
"""

import json
from aijaga_quiz import PAGE as QUIZ_PAGE, FIELDS


def V(f, title, vid, quiz):
    return {"f": f, "title": title, "id": vid, "quiz": quiz}


# f    = index of the field in aijaga_quiz.py (0 = Body Systems, 1 = Nutrition, ...)
# id   = the YouTube video id (the part after watch?v=)
# quiz = the exact quiz title in aijaga_quiz.py (used for the "Take the quiz" button)
VIDEOS = [
    # 0 Body Systems & Organs
    V(0, "Immune System", "azE3rv5l28Y", "Immune System"),
    V(0, "Digestive System", "ZBZWgrfZFbU", "Digestive System"),
    V(0, "Gut", "4zLU2UE90jM", "Gut"),
    V(0, "Liver Function", "IMzFgyrUXnE", "Liver Function"),
    V(0, "Respiratory System", "mOKmjYwfDGU", "Respiratory System"),
    V(0, "Urinary Function", "dZREDWD_5bA", "Urinary System"),
    V(0, "How the Brain Works", "ndDpjT0_IM0", "Brain"),
    V(0, "Hormones", "_nyvBUmIwhI", "Hormones"),
    V(0, "Body Parts", "jd3bWUAa9qM", "Body Parts"),
    V(0, "How Muscles Grow", "Vnj9Ay6xmOk", "Muscles"),
    # 1 Nutrition & Healthy Habits
    V(1, "Drink Water", "31F0laJjyy8", "Drink Water"),
    V(1, "Food Pyramid", "tsgyWIsYvxs", "Food Pyramid"),
    V(1, "Urine Color", "ka85yQcA524", "Urine Color"),
    V(1, "Constipation", "TK0ZF7FNxsU", "Constipation"),
    V(1, "Holding Urine", "BrCIcqS1yEg", "Holding Urine"),
    V(1, "Cavities", "3ZHYQ6f1BhU", "Cavities"),
    # 2 Infections & Common Illnesses
    V(2, "Fever", "BqOaG9VuP_I", "Fever"),
    V(2, "What is a Virus?", "YS7vsBgWszI", "Virus?"),
    V(2, "Chickenpox", "xNc4kEt4pN0", "Chickenpox"),
    V(2, "Dengue", "Oy1eQQZQZvs", "Dengue"),
    V(2, "Tetanus", "S6rogdxMGww", "Tetanus"),
    V(2, "Rabies", "EAhqjbWpLSI", "Rabies"),
    V(2, "Mouth Ulcer", "ScAq1VgTml0", "Mouth Ulcer"),
    # 3 Heart & Circulation
    V(3, "Why We Faint", "2-Dv9P6gLYY", "Fainting"),
    V(3, "Cardiac Arrest", "41kcmMJQ2ds", "Cardiac Arrest"),
    V(3, "Heart Attack", "jP0qT6GpBVY", "Heart Attack"),
    V(3, "Blood Pressure", "2HTZs51OYwo", "Blood Pressure"),
    # 4 Health Conditions & Body Changes
    V(4, "Asthma", "s1R0dL1VB0I", "Asthma"),
    V(4, "Allergies", "sM3FDsMAMdc", "Allergies"),
    V(4, "Migraine", "wRGxUc-AuUM", "Migraine"),
    V(4, "Epilepsy", "AaBgkBEA9eM", "Epilepsy"),
    V(4, "Diabetes", "d86DofYpkrY", "Diabetes"),
    V(4, "Kidney Stones", "xmbpPWIV0VU", "Kidney Stones"),
    V(4, "Pimples", "SPQt5v5Xsg8", "Pimples"),
    V(4, "Period", "PeL_XtBrOxw", "Period"),
    # 5 Mental Health & Learning
    V(5, "Depression", "0hxFR6tezAc", "Depression"),
    V(5, "Autism Spectrum (ASD)", "d2mlWUzA0B4", "Autism Spectrum (ASD)"),
    V(5, "Alzheimer's", "5dmqaH-MlA0", "Alzheimer's"),
    V(5, "Dyslexia", "65psPXWzNic", "Dyslexia"),
    V(5, "Stuttering", "juMxqemIlpU", "Stuttering"),
    V(5, "Anger", "clwt7iXF1Mg", "Anger"),
    # 6 First Aid & Emergencies
    V(6, "First Aid: Finger Cuts", "Z3XN4GWANRM", "Finger Cuts"),
    V(6, "How a Broken Bone Heals", "yovH2-Uw7i8", "Broken Bone"),
    V(6, "Choking", "oSZG9JHdngM", "Choking"),
    V(6, "Drowning", "WKu7_Fwf3PI", "Drowning"),
    V(6, "Bee Sting", "H_wj50ox8OY", "Bee Sting"),
    V(6, "Wasp Sting", "8Fz3qvNvLO8", "Wasp Sting"),
    V(6, "Heat Wave", "ARB6R51iQ_k", "Heat Wave"),
    V(6, "Stampede", "MSiw9ZGdtSQ", "Stampede"),
]


# ----------------------------------------------------------------------------
# Safety check: warn in the terminal if a video points at a quiz title that
# does not exist (the "Take the quiz" button is hidden for that video).
# ----------------------------------------------------------------------------
_known = {(fi, z["title"]) for fi, f in enumerate(FIELDS) for z in f["quizzes"]}
for _v in VIDEOS:
    if (_v["f"], _v["quiz"]) not in _known:
        print("[aijaga_video] WARNING: no quiz titled %r in field %d (video %r)" % (_v["quiz"], _v["f"], _v["title"]))


# ----------------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------------
VIDEO_CSS = r"""
/* ---- VIDEO MODE ---- */
.vgrid{grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}
.tile.vtile{padding:10px 10px 14px; gap:10px; align-items:stretch}
.thumb{
  position:relative; display:block; width:100%; aspect-ratio:16/9; overflow:hidden;
  background:var(--opt); border:3px solid var(--ink);
}
.thumb img{width:100%; height:100%; object-fit:cover; display:block}
.thumb .play{
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  color:#fff; font-size:26px; font-weight:800; background:rgba(27,42,53,.28);
}
.vwrap{width:100%; max-width:720px; display:flex; flex-direction:column; align-items:center; gap:14px}
.vframe{
  width:100%; aspect-ratio:16/9; background:#000; border:4px solid var(--ink); box-shadow:6px 6px 0 var(--ink);
}
.vframe iframe{width:100%; height:100%; border:0; display:block}
.vhint{margin:0; font-size:14px; color:var(--muted); text-align:center}
.vhint a{color:var(--green); text-decoration:underline; font-weight:800}
"""


# ----------------------------------------------------------------------------
# JavaScript (runs inside the same script as the quiz, so it can reuse
# stage, esc, showHome, levelBar, clearTimers, startQuiz ...)
# ----------------------------------------------------------------------------
VIDEO_JS = r"""
/* ===== VIDEO MODE (added by aijaga_video.py) ===== */
const VIDEOS = __VIDEO_DATA__;

function videosInField(fi) { return VIDEOS.filter((v) => v.f === fi); }
function videoThumb(id) { return "https://i.ytimg.com/vi/" + encodeURIComponent(id) + "/mqdefault.jpg"; }

function goVideos() {
  clearTimers(); showHome(true); levelBar();
  let html = '<h1 class="title">\u25B6 PICK A FIELD</h1><p class="sub">WHAT DO YOU WANT TO WATCH?</p><div class="grid">';
  FIELDS.forEach((f, fi) => {
    const n = videosInField(fi).length;
    html += '<button class="tile field" data-f="' + fi + '"><h3>' + esc(f.name.toUpperCase()) + '</h3><span class="count">' + n + (n === 1 ? " video" : " videos") + "</span></button>";
  });
  html += "</div>";
  stage.innerHTML = html;
  stage.querySelectorAll(".tile").forEach((b) => b.addEventListener("click", () => goVideoList(+b.dataset.f)));
}

function goVideoList(fi) {
  clearTimers(); showHome(true); levelBar();
  const list = videosInField(fi);
  let html = '<h1 class="title">' + esc(FIELDS[fi].name.toUpperCase()) + '</h1><p class="sub">PICK A VIDEO</p><div class="grid vgrid">';
  list.forEach((v, i) => {
    html += '<button class="tile vtile" data-i="' + i + '">' +
      '<span class="thumb"><img src="' + videoThumb(v.id) + '" alt="" loading="lazy"><b class="play">\u25B6</b></span>' +
      '<h3>' + esc(v.title.toUpperCase()) + "</h3></button>";
  });
  html += '</div><div class="actions"><button class="btn small" id="backVF">\u25C2 BACK TO FIELDS</button></div>';
  stage.innerHTML = html;
  stage.querySelectorAll(".tile").forEach((b) => b.addEventListener("click", () => goWatch(fi, +b.dataset.i)));
  $("#backVF").addEventListener("click", goVideos);
}

function goWatch(fi, i) {
  clearTimers(); showHome(true); levelBar();
  const v = videosInField(fi)[i];
  const qi = FIELDS[fi].quizzes.findIndex((q) => q.title === v.quiz);
  const id = encodeURIComponent(v.id);
  stage.innerHTML =
    '<h1 class="title">' + esc(v.title.toUpperCase()) + '</h1>' +
    '<div class="vwrap">' +
      '<div class="vframe"><iframe src="https://www.youtube-nocookie.com/embed/' + id + '?rel=0" title="' + esc(v.title) + '" ' +
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture" allowfullscreen ' +
        'referrerpolicy="strict-origin-when-cross-origin"></iframe></div>' +
      '<p class="vhint">Video not playing? <a href="https://www.youtube.com/watch?v=' + id + '" target="_blank" rel="noopener noreferrer">Open it on YouTube</a></p>' +
      '<div class="actions">' +
        (qi >= 0 ? '<button class="btn big" id="vQuiz">TAKE THE QUIZ</button>' : "") +
        '<button class="btn big alt" id="vBack">BACK TO VIDEOS</button>' +
      "</div>" +
    "</div>";
  if (qi >= 0) $("#vQuiz").addEventListener("click", () => startQuiz(fi, qi));
  $("#vBack").addEventListener("click", () => goVideoList(fi));
}
"""


# ----------------------------------------------------------------------------
# Build the new PAGE
# ----------------------------------------------------------------------------
def _build():
    page = QUIZ_PAGE

    # 1) the VIDEO button on the home screen used to show "coming soon"
    old_hook = 'else toast("Videos are coming soon.");'
    if old_hook not in page:
        raise RuntimeError("aijaga_video.py: could not find the VIDEO button hook in aijaga_quiz.py. "
                           "Make sure aijaga_quiz.py is the latest version.")
    page = page.replace(old_hook, "else goVideos();", 1)

    # 2) add the CSS just before the closing </style>
    page = page.replace("</style>", VIDEO_CSS + "\n</style>", 1)

    # 3) add the JavaScript just before the final </script>
    js = VIDEO_JS.replace("__VIDEO_DATA__", json.dumps(VIDEOS))
    head, sep, tail = page.rpartition("</script>")
    return head + js + "\n" + sep + tail


PAGE = _build()
