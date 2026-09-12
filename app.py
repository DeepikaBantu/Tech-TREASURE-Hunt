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

FULL_TITLE = f"{CONFIG['game_title']} — {CONFIG['event_name']}"

# --------------------------------------------------------------------------
# CLUES — a short, always-visible nudge shown under every question, kept
# separate from the existing optional Hint (which costs points). Purely
# additive: does not touch scoring, validation, or any other game logic.
# --------------------------------------------------------------------------
CLUES = [
    "This structure never forgets what it saw last — think last-in, first-out.",
    "Add up only the values that genuinely cross the line, not the ones sitting on it.",
    "Third floor from the ground — where routers live and packets find their way.",
    "Only departments whose average genuinely clears the bar make the list.",
    "Every term here is just the sum of the two that came right before it.",
]

# --------------------------------------------------------------------------
# GLOBAL STYLE
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu, footer, header {visibility: hidden;}

        .stApp {
            background: radial-gradient(circle at 20% 20%, #10233d 0%, #060b16 55%, #020409 100%);
            background-attachment: fixed;
            overflow-x: hidden;
        }

        .block-container {
            max-width: 100% !important;
            padding: 1.6rem 4vw 3rem 4vw !important;
        }

        /* Force bright, readable text everywhere */
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

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes glowPulse {
            0%, 100% { box-shadow: 0 0 12px rgba(167,139,250,0.45); }
            50%      { box-shadow: 0 0 22px rgba(167,139,250,0.85); }
        }

        /* ---------- Top identity bar (compact, consistent everywhere) --- */
        .topbar-title {
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.03em;
            color: #cfe3ff !important;
        }
        .topbar-title .accent { color: #4fd1ff; }
        .topbar-score {
            text-align: right;
            font-size: 1.05rem;
            font-weight: 800;
            color: #ffd98a !important;
        }

        /* ---------- Landing hero ---------- */
        .eyebrow {
            letter-spacing: 0.35em;
            font-size: 1rem;
            color: #4fd1ff !important;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.2rem;
        }
        .event-title {
            font-size: clamp(2.2rem, 5.5vw, 4.2rem);
            font-weight: 900;
            text-align: center;
            line-height: 1.08;
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
            margin-bottom: 1.6rem;
        }
        .stage-label {
            text-align: center;
            color: #8ea3c4 !important;
            letter-spacing: 0.15em;
            font-size: 0.85rem;
            font-weight: 700;
            margin-top: 1.2rem;
        }

        /* ---------- Stage stepper ---------- */
        .stage-heading {
            text-align: center;
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            color: #a9c4ff !important;
            margin: 0.4rem 0 0.9rem 0;
        }
        .stepper {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.35rem;
            flex-wrap: wrap;
            margin-bottom: 1.6rem;
        }
        .step {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.4rem 0.85rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 800;
            white-space: nowrap;
        }
        .step--done {
            background: rgba(79, 209, 255, 0.15);
            color: #4fd1ff !important;
            border: 1px solid rgba(79, 209, 255, 0.45);
        }
        .step--current {
            background: linear-gradient(90deg, #4fd1ff, #a78bfa);
            color: #06111f !important;
            animation: glowPulse 1.8s ease-in-out infinite;
        }
        .step--locked {
            background: rgba(255, 255, 255, 0.04);
            color: #5c6c86 !important;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .step-arrow { color: #3c4a63; font-weight: 700; }

        /* ---------- Question card ---------- */
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
            margin-bottom: 0.8rem;
        }
        .qprompt {
            font-size: clamp(1.1rem, 1.8vw, 1.4rem);
            line-height: 1.75;
            color: #eaf2ff !important;
            margin-bottom: 1.1rem;
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
            margin-bottom: 1.2rem;
            display: block;
        }

        /* ---------- Clue card (always visible, distinct from Hint) ---- */
        .clue-card {
            background: rgba(255, 196, 79, 0.07);
            border: 1.5px solid rgba(255, 196, 79, 0.45);
            border-radius: 16px;
            padding: 1rem 1.3rem;
            margin: 0.2rem 0 1.4rem 0;
        }
        .clue-label {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            color: #ffd98a !important;
            font-weight: 900;
            letter-spacing: 0.14em;
            font-size: 1rem;
            margin-bottom: 0.4rem;
        }
        .clue-text {
            color: #fff2d9 !important;
            font-size: 1.05rem;
            line-height: 1.6;
        }

        /* ---------- Feedback banners ---------- */
        .feedback-correct, .feedback-wrong, .feedback-skip {
            animation: fadeInUp 0.35s ease;
            padding: 1rem 1.2rem;
            border-radius: 14px;
            font-weight: 800;
            font-size: 1.1rem;
        }
        .feedback-correct {
            background: rgba(46, 213, 115, 0.14);
            border: 1.5px solid rgba(46, 213, 115, 0.55);
            color: #7CFFB2 !important;
        }
        .feedback-wrong {
            background: rgba(255, 99, 99, 0.14);
            border: 1.5px solid rgba(255, 99, 99, 0.55);
            color: #FF9A9A !important;
        }
        .feedback-skip {
            background: rgba(255, 196, 79, 0.14);
            border: 1.5px solid rgba(255, 196, 79, 0.55);
            color: #FFD98A !important;
        }

        /* ---------- Buttons: bigger, clearer, well spaced ---------- */
        div.stButton > button {
            border-radius: 14px;
            font-weight: 800;
            font-size: 1.08rem;
            min-height: 3.3rem;
            padding: 0.7rem 1.6rem;
            border: 1.5px solid rgba(79, 209, 255, 0.4);
            color: #eaf2ff;
            transition: transform 0.12s ease;
        }
        div.stButton > button:hover { transform: translateY(-1px); }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #4fd1ff, #a78bfa);
            color: #06111f !important;
            border: none;
            font-size: 1.15rem;
        }

        /* Skip button — distinct amber, unmistakably a real action */
        .st-key-skip_wrap div.stButton > button {
            background: linear-gradient(90deg, #ffb347, #ff8f3c) !important;
            color: #241300 !important;
            border: none !important;
            font-weight: 900 !important;
            letter-spacing: 0.06em;
            font-size: 1.1rem !important;
        }

        /* Hint button — visually secondary/subtle */
        .st-key-hint_wrap div.stButton > button {
            background: rgba(255,255,255,0.03) !important;
            border: 1.5px dashed rgba(255,255,255,0.3) !important;
            font-weight: 700 !important;
        }

        .stTextInput input {
            border-radius: 12px !important;
            font-size: 1.15rem !important;
            text-align: center;
            min-height: 3rem;
        }

        /* ---------- Treasure / finish screen ---------- */
        .st-key-treasure_screen {
            background: radial-gradient(circle at 50% 0%, rgba(255,196,79,0.18), transparent 60%);
            border: 1.5px solid rgba(255, 196, 79, 0.35);
            border-radius: 24px;
            padding: clamp(1.6rem, 4vw, 3rem) 1rem;
        }
        .trophy { text-align:center; font-size: 4.5rem; margin-bottom: 0.3rem; }
        .treasure-title {
            font-size: clamp(2rem, 5vw, 3.6rem);
            font-weight: 900;
            text-align: center;
            line-height: 1.1;
            margin: 0.1rem 0 0.4rem 0;
            background: linear-gradient(90deg, #ffd98a, #ff8f3c 55%, #ffd98a);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
        }

        /* ---------- Responsive tweaks ---------- */
        @media (max-width: 640px) {
            .block-container { padding: 1.1rem 4vw 2.2rem 4vw !important; }
            .stepper { gap: 0.25rem; }
            .step { padding: 0.32rem 0.6rem; font-size: 0.72rem; }
            div.stButton > button { font-size: 1rem; min-height: 3rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# RESULTS LOGGING — appends every completed attempt to results.csv so the
# organizer can download the whole event's scores to their laptop.
# (unchanged)
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
# SESSION STATE (unchanged)
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
    "celebrated_this_q": False,
    "celebrated_finish": False,
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
    st.session_state.celebrated_this_q = False
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
        st.session_state.feedback_msg = f"Correct! +{pts} points — stage unlocked."
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
    st.markdown(f'<div class="event-title">{CONFIG["game_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="game-subtitle">{CONFIG["event_name"]}</div>', unsafe_allow_html=True)
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
        if st.button("🚀 Start Treasure Hunt", type="primary", use_container_width=True):
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
# STAGE STEPPER — "STAGE X / N" heading + Stage 1 → Stage 2 → ... → Treasure,
# with clearly locked / current / done visual states.
# --------------------------------------------------------------------------
def render_stage_stepper():
    current = st.session_state.stage_index
    total = len(QUESTIONS)

    st.markdown(
        f'<div class="stage-heading">STAGE {current + 1} / {total}</div>',
        unsafe_allow_html=True,
    )

    parts = []
    for i in range(total):
        if i < current:
            parts.append(f'<span class="step step--done">✔ Stage {i + 1}</span>')
        elif i == current:
            parts.append(f'<span class="step step--current">▶ Stage {i + 1}</span>')
        else:
            parts.append(f'<span class="step step--locked">🔒 Stage {i + 1}</span>')
        parts.append('<span class="step-arrow">→</span>')
    # final "Treasure" node
    if current >= total:
        parts.append('<span class="step step--done">🏆 Treasure</span>')
    else:
        parts.append('<span class="step step--locked">🏆 Treasure</span>')

    st.markdown(f'<div class="stepper">{"".join(parts)}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------
# GAME SCREEN
# --------------------------------------------------------------------------
def render_game():
    q_index = st.session_state.stage_index
    q = QUESTIONS[q_index]

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(
            f'<div class="topbar-title">🗺️ {CONFIG["game_title"]} '
            f'<span class="accent">— {CONFIG["event_name"]}</span> '
            f'&nbsp;·&nbsp; {st.session_state.player_name}</div>',
            unsafe_allow_html=True,
        )
    with top_r:
        st.markdown(
            f'<div class="topbar-score">✦ SCORE: {st.session_state.score}</div>',
            unsafe_allow_html=True,
        )

    render_stage_stepper()

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

        # ---- CLUE (always visible, distinct from the optional Hint) ----
        clue_text = CLUES[q_index] if q_index < len(CLUES) else ""
        if clue_text:
            st.markdown(
                f'<div class="clue-card">'
                f'<div class="clue-label">💡 CLUE</div>'
                f'<div class="clue-text">{clue_text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if not st.session_state.answer_locked:
            answer_key = f"answer_input_{q_index}"
            user_answer = st.text_input("Your answer", key=answer_key, placeholder="Type your answer here...")

            b1, b2, b3 = st.columns([1, 1, 1])
            with b1:
                if st.button("✅ SUBMIT ANSWER", type="primary", use_container_width=True):
                    if user_answer.strip():
                        check_answer(user_answer)
                        st.rerun()
                    else:
                        st.warning("Type an answer before submitting.")
            with b2:
                with st.container(key="skip_wrap"):
                    if st.button("⏭️ SKIP", use_container_width=True):
                        skip_question()
                        st.rerun()
            with b3:
                with st.container(key="hint_wrap"):
                    if q.get("hint") and st.button(
                        f"🧠 Hint (-{CONFIG['hint_penalty']} pts)",
                        use_container_width=True,
                        disabled=st.session_state.show_hint,
                    ):
                        st.session_state.show_hint = True
                        st.session_state.hint_used_this_q = True
                        st.rerun()

            if st.session_state.show_hint and q.get("hint"):
                st.info(f"🧠 Hint: {q['hint']}")

            if st.session_state.feedback == "wrong":
                st.markdown(f'<div class="feedback-wrong">{st.session_state.feedback_msg}</div>', unsafe_allow_html=True)

        else:
            css_class = "feedback-correct" if st.session_state.feedback == "correct" else "feedback-skip"
            st.markdown(f'<div class="{css_class}">{st.session_state.feedback_msg}</div>', unsafe_allow_html=True)

            if st.session_state.feedback == "correct" and not st.session_state.celebrated_this_q:
                st.balloons()
                st.session_state.celebrated_this_q = True

            st.write("")
            label = "NEXT STAGE ➜" if q_index < len(QUESTIONS) - 1 else "UNLOCK TREASURE 🏆"
            if st.button(label, type="primary", use_container_width=True):
                go_next_stage()
                st.rerun()


# --------------------------------------------------------------------------
# FINISH SCREEN — visually distinct "treasure unlocked" moment
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

    if not st.session_state.celebrated_finish:
        st.balloons()
        st.session_state.celebrated_finish = True

    with st.container(key="treasure_screen"):
        st.markdown('<div class="trophy">🏆</div>', unsafe_allow_html=True)
        st.markdown('<div class="treasure-title">TREASURE UNLOCKED!</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="game-subtitle">Congratulations, {st.session_state.player_name} — '
            f'you cracked the {CONFIG["event_name"]} Tech Treasure Hunt!</div>',
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
                '<div class="tagline">Your result has been recorded. '
                'Please hand the device back to the organizer.</div>',
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
