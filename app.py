import csv
import os
import time
from datetime import datetime

import streamlit as st
from questions import QUESTIONS, CONFIG

st.set_page_config(
    page_title=f"{CONFIG['game_title']} — {CONFIG['event_name']}",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

RESULTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.csv")
RESULTS_FIELDS = ["timestamp", "team_name", "score", "correct", "skipped", "wrong_attempts", "time_taken"]

# --------------------------------------------------------------------------
# GLOBAL STYLE — full-bleed dark theme, no boxed/centered card, big type
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu, footer, header {visibility: hidden;}

        .stApp {
            background: radial-gradient(circle at 20% 20%, #10233d 0%, #060b16 55%, #020409 100%);
            background-attachment: fixed;
        }

        .block-container {
            max-width: 100% !important;
            padding: 2rem 4vw 3rem 4vw !important;
        }

        /* Force bright, readable text everywhere — overrides Streamlit's
           own low-contrast defaults for markdown / metrics / labels */
        .stApp, .stApp p, .stApp span, .stApp label,
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] p {
            color: #eaf2ff !important;
        }

        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #8ea3c4 !important;
            font-weight: 700 !important;
        }

        .eyebrow {
            letter-spacing: 0.35em;
            font-size: 1rem;
            color: #4fd1ff !important;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.2rem;
        }

        .event-title {
            font-size: clamp(2.6rem, 7vw, 5.5rem);
            font-weight: 900;
            text-align: center;
            line-height: 1.05;
            margin: 0.2rem 0 0.3rem 0;
            background: linear-gradient(90deg, #4fd1ff, #a78bfa 55%, #ff8fd8);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
        }

        .game-subtitle {
            text-align: center;
            font-size: clamp(1.1rem, 2.2vw, 1.6rem);
            color: #cfe3ff !important;
            font-weight: 600;
            margin-bottom: 0.1rem;
        }

        .tagline {
            text-align: center;
            color: #8ea3c4 !important;
            font-size: 1.05rem;
            margin-bottom: 2rem;
        }

        .stage-label {
            text-align: center;
            color: #8ea3c4 !important;
            letter-spacing: 0.15em;
            font-size: 0.85rem;
            font-weight: 700;
            margin-top: 1.2rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 20px !important;
            border-color: rgba(79, 209, 255, 0.3) !important;
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
        }

        .qtitle {
            font-size: clamp(1.3rem, 2.4vw, 1.9rem);
            font-weight: 800;
            color: #4fd1ff !important;
            margin-bottom: 0.6rem;
        }

        .qprompt {
            font-size: clamp(1.05rem, 1.7vw, 1.35rem);
            line-height: 1.7;
            color: #eaf2ff !important;
            margin-bottom: 1rem;
        }

        .qsnippet {
            background: #050a14;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1rem 1.2rem;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.95rem;
            white-space: pre;
            overflow-x: auto;
            color: #b9e6ff !important;
            margin-bottom: 1rem;
            display: block;
        }

        .feedback-correct {
            background: rgba(46, 213, 115, 0.12);
            border: 1px solid rgba(46, 213, 115, 0.5);
            color: #7CFFB2 !important;
            padding: 0.9rem 1.1rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.05rem;
        }

        .feedback-wrong {
            background: rgba(255, 99, 99, 0.12);
            border: 1px solid rgba(255, 99, 99, 0.5);
            color: #FF9A9A !important;
            padding: 0.9rem 1.1rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.05rem;
        }

        .feedback-skip {
            background: rgba(255, 196, 79, 0.12);
            border: 1px solid rgba(255, 196, 79, 0.5);
            color: #FFD98A !important;
            padding: 0.9rem 1.1rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.05rem;
        }

        div.stButton > button {
            border-radius: 12px;
            font-weight: 700;
            padding: 0.6rem 1.4rem;
            border: 1px solid rgba(79, 209, 255, 0.4);
            color: #eaf2ff;
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #4fd1ff, #a78bfa);
            color: #06111f !important;
            border: none;
        }

        .stTextInput input {
            border-radius: 12px !important;
            font-size: 1.1rem !important;
            text-align: center;
        }

        .trophy { text-align:center; font-size: 4rem; margin-bottom: 0.2rem; }

        .trail-dot {
            display: inline-block;
            width: 14px; height: 14px;
            border-radius: 50%;
            margin: 0 6px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# RESULTS LOGGING — appends every completed attempt to results.csv so the
# organizer can download the whole event's scores to their laptop.
# --------------------------------------------------------------------------
def save_result(name, score, correct, skipped, wrong, time_taken_str):
    file_exists = os.path.isfile(RESULTS_FILE)
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULTS_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "team_name": name,
            "score": score,
            "correct": correct,
            "skipped": skipped,
            "wrong_attempts": wrong,
            "time_taken": time_taken_str,
        })


def load_results():
    if not os.path.isfile(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------------------------
defaults = {
    "started": False,
    "finished": False,
    "player_name": "",
    "stage_index": 0,
    "score": 0,
    "correct_count": 0,
    "skipped_count": 0,
    "wrong_count": 0,
    "hint_used_this_q": False,
    "show_hint": False,
    "feedback": None,       # "correct" | "wrong" | "skip" | None
    "feedback_msg": "",
    "answer_locked": False,  # True once current question is resolved (correct/skip)
    "start_time": None,
    "end_time": None,
    "result_saved": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def start_game(name):
    for key, val in defaults.items():
        st.session_state[key] = val
    st.session_state.player_name = name.strip()
    st.session_state.started = True
    st.session_state.start_time = time.time()


def go_next_stage():
    st.session_state.stage_index += 1
    st.session_state.hint_used_this_q = False
    st.session_state.show_hint = False
    st.session_state.feedback = None
    st.session_state.feedback_msg = ""
    st.session_state.answer_locked = False
    if st.session_state.stage_index >= len(QUESTIONS):
        st.session_state.finished = True
        st.session_state.end_time = time.time()


def check_answer(user_answer):
    q = QUESTIONS[st.session_state.stage_index]
    normalized = user_answer.strip().lower()
    accepted = [a.strip().lower() for a in q["answers"]]
    if normalized in accepted:
        pts = q["points"]
        if st.session_state.hint_used_this_q:
            pts = max(0, pts - CONFIG["hint_penalty"])
        st.session_state.score += pts
        st.session_state.correct_count += 1
        st.session_state.feedback = "correct"
        st.session_state.feedback_msg = f"Correct! +{pts} points"
        st.session_state.answer_locked = True
    else:
        st.session_state.wrong_count += 1
        st.session_state.score = max(0, st.session_state.score - CONFIG["wrong_attempt_penalty"])
        st.session_state.feedback = "wrong"
        st.session_state.feedback_msg = "Not quite — try again."


def skip_question():
    st.session_state.skipped_count += 1
    st.session_state.feedback = "skip"
    st.session_state.feedback_msg = "Skipped — moving to the next question."
    st.session_state.answer_locked = True


# --------------------------------------------------------------------------
# LANDING SCREEN
# --------------------------------------------------------------------------
def render_landing():
    st.markdown(f'<div class="eyebrow">{CONFIG["event_name"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="event-title">{CONFIG["event_name"].split()[0]} {CONFIG["event_name"].split()[1]}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="game-subtitle">{CONFIG["game_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tagline">{CONFIG["tagline"]}</div>', unsafe_allow_html=True)

    left, mid, right = st.columns([1, 1.4, 1])
    with mid:
        m1, m2, m3 = st.columns(3)
        m1.metric("Questions", len(QUESTIONS))
        m2.metric("Rounds", "1")
        m3.metric("Skip allowed", "Yes")

        st.markdown('<div class="stage-label">YOUR NAME / TEAM NAME</div>', unsafe_allow_html=True)
        name = st.text_input(
            "Team name", key="name_input", label_visibility="collapsed",
            placeholder="e.g. Team Byte Bandits",
        )
        st.write("")
        if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
            if name.strip():
                start_game(name)
                st.rerun()
            else:
                st.error("Please enter a name or team name to start.")

    st.write("")
    st.write("")
    with st.expander("📥 Organizer: view & download results so far"):
        results = load_results()
        if results:
            st.dataframe(results, use_container_width=True, hide_index=True)
            with open(RESULTS_FILE, "rb") as f:
                st.download_button(
                    "⬇️ Download results.csv",
                    data=f,
                    file_name="engineering_day_quiz_results.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        else:
            st.caption("No completed attempts yet — results appear here once a team finishes.")


# --------------------------------------------------------------------------
# GAME SCREEN
# --------------------------------------------------------------------------
def render_trail():
    dots_html = ""
    for i in range(len(QUESTIONS)):
        if i < st.session_state.stage_index:
            color = "#4fd1ff"
        elif i == st.session_state.stage_index:
            color = "#a78bfa"
        else:
            color = "rgba(255,255,255,0.15)"
        dots_html += f'<span class="trail-dot" style="background:{color};"></span>'
    st.markdown(f'<div style="text-align:center; margin-bottom:1rem;">{dots_html}</div>', unsafe_allow_html=True)


def render_game():
    q_index = st.session_state.stage_index
    q = QUESTIONS[q_index]

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(
            f'<div class="stage-label" style="text-align:left;">'
            f'{CONFIG["game_title"].upper()} &nbsp;·&nbsp; {st.session_state.player_name}</div>',
            unsafe_allow_html=True,
        )
    with top_r:
        st.markdown(
            f'<div class="stage-label" style="text-align:right;">✦ SCORE: {st.session_state.score}</div>',
            unsafe_allow_html=True,
        )

    render_trail()

    # Everything below lives inside ONE bordered container, so widgets
    # (text input / buttons) visually sit inside the question card.
    card = st.container(border=True)
    with card:
        st.markdown(
            f'<div class="qtitle">Question {q_index + 1} of {len(QUESTIONS)} — {q["title"]}</div>',
            unsafe_allow_html=True,
        )
        prompt_html = q["prompt"].replace("\n", "<br>")
        st.markdown(f'<div class="qprompt">{prompt_html}</div>', unsafe_allow_html=True)
        if q["snippet"]:
            snippet_html = q["snippet"].replace("\n", "<br>")
            st.markdown(f'<div class="qsnippet">{snippet_html}</div>', unsafe_allow_html=True)

        if not st.session_state.answer_locked:
            answer_key = f"answer_input_{q_index}"
            user_answer = st.text_input("Your answer", key=answer_key, placeholder="Type your answer here...")

            b1, b2, b3 = st.columns([1, 1, 1])
            with b1:
                if st.button("✅ Submit", type="primary", use_container_width=True):
                    if user_answer.strip():
                        check_answer(user_answer)
                        st.rerun()
                    else:
                        st.warning("Type an answer before submitting.")
            with b2:
                if st.button("⏭️ Skip", use_container_width=True):
                    skip_question()
                    st.rerun()
            with b3:
                if q.get("hint") and st.button(
                    f"💡 Hint (-{CONFIG['hint_penalty']} pts)",
                    use_container_width=True,
                    disabled=st.session_state.show_hint,
                ):
                    st.session_state.show_hint = True
                    st.session_state.hint_used_this_q = True
                    st.rerun()

            if st.session_state.show_hint and q.get("hint"):
                st.info(f"💡 Hint: {q['hint']}")

            if st.session_state.feedback == "wrong":
                st.markdown(f'<div class="feedback-wrong">{st.session_state.feedback_msg}</div>', unsafe_allow_html=True)

        else:
            css_class = "feedback-correct" if st.session_state.feedback == "correct" else "feedback-skip"
            st.markdown(f'<div class="{css_class}">{st.session_state.feedback_msg}</div>', unsafe_allow_html=True)
            st.write("")
            label = "Next Question ➜" if q_index < len(QUESTIONS) - 1 else "Finish Quiz 🏆"
            if st.button(label, type="primary", use_container_width=True):
                go_next_stage()
                st.rerun()


# --------------------------------------------------------------------------
# FINISH SCREEN
# --------------------------------------------------------------------------
def render_finish():
    elapsed = int(st.session_state.end_time - st.session_state.start_time)
    mins, secs = divmod(elapsed, 60)
    time_str = f"{mins:02d}:{secs:02d}"

    if not st.session_state.result_saved:
        save_result(
            st.session_state.player_name,
            st.session_state.score,
            st.session_state.correct_count,
            st.session_state.skipped_count,
            st.session_state.wrong_count,
            time_str,
        )
        st.session_state.result_saved = True

    st.markdown('<div class="trophy">🏆</div>', unsafe_allow_html=True)
    st.markdown('<div class="event-title" style="font-size:clamp(2rem,5vw,3.5rem);">Quiz Complete!</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="game-subtitle">Well played, {st.session_state.player_name}!</div>',
        unsafe_allow_html=True,
    )

    left, mid, right = st.columns([1, 2, 1])
    with mid:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Score", st.session_state.score)
        c2.metric("Correct", f"{st.session_state.correct_count}/{len(QUESTIONS)}")
        c3.metric("Skipped", st.session_state.skipped_count)
        c4.metric("Time", time_str)

        st.write("")
        st.markdown(
            '<div class="tagline">Your result has been recorded. Please hand the device back to the organizer.</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# ROUTER
# --------------------------------------------------------------------------
if not st.session_state.started:
    render_landing()
elif st.session_state.finished:
    render_finish()
else:
    render_game()
