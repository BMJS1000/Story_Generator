
import os
import re
import html
from pathlib import Path

import streamlit as st
from groq import Groq
from dotenv import load_dotenv


# ============================================================
# 1. PAGE AND API SETUP
# ============================================================

st.set_page_config(
    page_title="The Story Room",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Groq API key not found. Check your .env file.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

MODEL = "openai/gpt-oss-20b"


# ============================================================
# 2. GENRE TEMPERATURE SETTINGS
# ============================================================

genre_temperature = {
    "Horror": 0.90,
    "Romance": 0.80,
    "Thriller": 0.75,
    "Science Fiction": 0.85,
    "Comedy": 0.95,
    "Fantasy": 0.90,
    "Mystery": 0.65,
    "Adventure": 0.85,
    "Drama": 0.70,
    "Historical Fiction": 0.65
}


# ============================================================
# 3. STORY LENGTH SETTINGS
# ============================================================

story_lengths = {
    "Low": 300,
    "Medium": 600,
    "High": 1000
}


# ============================================================
# 4. SESSION STATE
# ============================================================

if "generated_story" not in st.session_state:
    st.session_state.generated_story = None

if "story_details" not in st.session_state:
    st.session_state.story_details = None


# ============================================================
# 5. CUSTOM CSS
# ============================================================

st.html("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600;700;800&display=swap');

.stApp {
    background: #F4F0E8;
    color: #293B32;
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1160px;
    padding-top: 2rem;
    padding-bottom: 3.5rem;
}

[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}


/* BRAND */

.brand-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 31px;
    font-weight: 800;
    letter-spacing: .5px;
    color: #293B32;
}

.brand-subtitle {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    color: #98754F;
    margin-top: 7px;
}


/* HERO */

.hero-panel {
    background: linear-gradient(135deg, #294538, #486650);
    border-radius: 20px;
    padding: 42px 38px;
    min-height: 330px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
}

.hero-kicker {
    color: #E5C99F;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.5px;
    margin-bottom: 20px;
}

.hero-title {
    color: #FFF8EB;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(34px, 4vw, 49px);
    line-height: 1.13;
    font-weight: 700;
    margin: 0 0 17px 0;
}

.hero-copy {
    color: #E4E9E0;
    font-size: 16px;
    line-height: 1.75;
    margin-bottom: 22px;
}

.hero-signoff {
    color: #E5C99F;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
}


/* SECTION HEADINGS */

.section-title {
    color: #293B32;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 31px;
    font-weight: 700;
    margin: 1.4rem 0 .3rem 0;
}

.section-copy {
    color: #817461;
    font-size: 15px;
    margin-bottom: 1rem;
}

.field-kicker {
    color: #98754F;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    margin: 4px 0 8px 0;
}


/* FORM */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFCF6;
    border: 1px solid #E5DCCC;
    border-radius: 16px;
}

label,
[data-testid="stWidgetLabel"] p {
    color: #344B3E !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

input,
[data-baseweb="select"] {
    font-size: 15px !important;
}


/* BUTTONS */

.stButton > button,
.stFormSubmitButton > button,
.stDownloadButton > button {
    background: #304A3D;
    color: #FFFFFF;
    border: 1px solid #304A3D;
    border-radius: 10px;
    min-height: 48px;
    font-size: 14px;
    font-weight: 700;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover,
.stDownloadButton > button:hover {
    background: #52745B;
    color: #FFFFFF;
    border-color: #52745B;
}


/* GENERATED STORY */

.story-paper {
    background: #FFFCF6;
    border: 1px solid #E5DCCC;
    border-radius: 17px;
    padding: 34px 38px;
    margin-top: 10px;
}

.story-overline {
    color: #98754F;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.story-heading {
    color: #304A3D;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 32px;
    line-height: 1.2;
    margin-bottom: 20px;
}

.story-body {
    color: #514B40;
    font-family: 'DM Sans', sans-serif;
    font-size: 16px;
    line-height: 1.95;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.empty-title {
    color: #304A3D;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 26px;
    margin-bottom: 8px;
}

.empty-copy {
    color: #817461;
    font-size: 15px;
    line-height: 1.8;
}


/* FOOTER */

.footer-note {
    color: #927F6A;
    font-size: 12px;
    text-align: center;
    padding: 28px 0 8px 0;
}

</style>
""")


# ============================================================
# 6. HEADER
# ============================================================

header_left, header_right = st.columns([3, 1])

with header_left:

    st.html("""
    <div>
        <div class="brand-title">THE STORY ROOM.</div>
        <div class="brand-subtitle">
            A SPACE FOR IMAGINATION
        </div>
    </div>
    """)

with header_right:

    st.html("""
    <div style="text-align:right; color:#98754F;
                font-size:12px; padding-top:12px;">
        ✦ POWERED BY GROQ AI
    </div>
    """)

st.divider()


# ============================================================
# 7. HERO SECTION AND BOOK IMAGE
# ============================================================

hero_left, hero_right = st.columns(
    [1.15, 1],
    gap="large"
)

with hero_left:

    st.html("""
    <section class="hero-panel">

        <div class="hero-kicker">
            YOUR CREATIVE WRITING COMPANION
        </div>

        <h1 class="hero-title">
            Every story begins with an idea.
        </h1>

        <p class="hero-copy">
            From mysterious adventures to beautiful love stories,
            turn your imagination into words.
        </p>

        <div class="hero-signoff">
            DREAM IT. WRITE IT. READ IT.
        </div>

    </section>
    """)

with hero_right:

    book_image_url = (
        "https://images.unsplash.com/"
        "photo-1512820790803-83ca734da794"
        "?auto=format&fit=crop&w=1200&q=85"
    )

    st.image(
        book_image_url,
        caption="A quiet place for big ideas.",
        use_container_width=True
    )


# ============================================================
# 8. STORY INPUT FORM
# ============================================================

st.html("""
<div class="section-title">Create your story.</div>

<div class="section-copy">
    Choose your ingredients. We'll take care of the storytelling.
</div>
""")

with st.container(border=True):

    with st.form("story_generator_form"):

        st.html(
            '<div class="field-kicker">01 — STORY IDEA</div>'
        )

        story_name = st.text_input(
            "ENTER STORY NAME",
            placeholder="E.g. The Last Human, A Forgotten Promise...",
            max_chars=150
        )

        genre_col, length_col = st.columns(2)

        with genre_col:

            st.html(
                '<div class="field-kicker">02 — SELECT GENRE</div>'
            )

            genre = st.selectbox(
                "Choose your genre",
                options=list(genre_temperature.keys())
            )

        with length_col:

            st.html(
                '<div class="field-kicker">03 — STORY LENGTH</div>'
            )

            story_length = st.selectbox(
                "Choose story length",
                options=["Low", "Medium", "High"],
                format_func=lambda item:
                f"{item} · about {story_lengths[item]} words"
            )

        selected_temperature = genre_temperature[genre]

        st.caption(
            f"Creativity setting: {selected_temperature:.2f} "
            f"· Automatically selected for {genre}."
        )

        generate_button = st.form_submit_button(
            "✦  GENERATE MY STORY",
            use_container_width=True
        )


# ============================================================
# 9. STORY GENERATION FUNCTION
# ============================================================

def generate_story(story_topic, genre, story_length):

    target_words = story_lengths[story_length]

    temperature = genre_temperature[genre]

    prompt = f"""
You are a professional creative fiction writer.

Write an original and engaging fictional story.

STORY NAME OR TOPIC: {story_topic}

GENRE: {genre}

TARGET LENGTH: Approximately {target_words} words.

WRITING INSTRUCTIONS:

1. Build the story around the given topic.
2. Follow the selected genre carefully.
3. Include interesting and believable characters.
4. Create a clear setting.
5. Give the story a proper beginning, middle and ending.
6. Use descriptive and engaging language.
7. Maintain consistency throughout the story.
8. Aim for approximately {target_words} words.
9. Give the story an appropriate title.
10. Return only the completed story.

Do not explain the prompt or your writing process.
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a skilled creative fiction writer. "
                    "Write original, coherent stories with engaging "
                    "characters, clear pacing and satisfying endings."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=temperature,

        max_completion_tokens=4000

    )

    story_text = response.choices[0].message.content

    if not story_text or not story_text.strip():

        raise ValueError(
            "The model returned an empty story. Please try again."
        )

    return story_text.strip()


# ============================================================
# 10. HANDLE STORY GENERATION
# ============================================================

if generate_button:

    if not story_name.strip():

        st.warning(
            "Please enter a story name or topic before generating."
        )

    else:

        st.session_state.generated_story = None
        st.session_state.story_details = None

        try:

            with st.spinner(
                "Writing your story... please give your imagination a moment."
            ):

                new_story = generate_story(
                    story_topic=story_name.strip(),
                    genre=genre,
                    story_length=story_length
                )

            st.session_state.generated_story = new_story

            st.session_state.story_details = {
                "name": story_name.strip(),
                "genre": genre,
                "length": story_length,
                "temperature": genre_temperature[genre],
                "word_target": story_lengths[story_length]
            }

        except Exception as error:

            st.error(
                f"Story generation failed: {error}"
            )


# ============================================================
# 11. COMPLETE STORY DISPLAY SECTION
# ============================================================

st.divider()

if (
    st.session_state.generated_story
    and st.session_state.story_details
):

    story = st.session_state.generated_story

    details = st.session_state.story_details

    word_count = len(story.split())

    st.html("""
    <div class="section-title">
        Your story awaits.
    </div>

    <div class="section-copy">
        A fresh page from The Story Room. Happy reading!
    </div>
    """)

    # STORY INFORMATION

    metric_genre, metric_length, metric_words = st.columns(3)

    metric_genre.metric(
        "GENRE",
        details["genre"]
    )

    metric_length.metric(
        "LENGTH",
        details["length"]
    )

    metric_words.metric(
        "WORD COUNT",
        f"{word_count:,}"
    )

    # SAFELY ESCAPE GENERATED CONTENT

    safe_title = html.escape(details["name"])

    safe_story = html.escape(story)

    safe_genre = html.escape(details["genre"])

    # DISPLAY STORY

    st.html(f"""
    <article class="story-paper">

        <div class="story-overline">
            THE STORY ROOM · {safe_genre}
        </div>

        <h2 class="story-heading">
            {safe_title}
        </h2>

        <div class="story-body">{safe_story}</div>

    </article>
    """)

    st.write("")

    # DOWNLOAD STORY

    safe_filename = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        details["name"]
    ).strip("_")

    if not safe_filename:
        safe_filename = "my_story"

    download_col, regenerate_col = st.columns(2)

    with download_col:

        st.download_button(
            label="↓ DOWNLOAD MY STORY",
            data=story.encode("utf-8"),
            file_name=f"{safe_filename}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with regenerate_col:

        regenerate_button = st.button(
            "↻ GENERATE ANOTHER VERSION",
            use_container_width=True
        )

    # REGENERATE STORY

    if regenerate_button:

        try:

            with st.spinner(
                "Creating another version of your story..."
            ):

                new_story = generate_story(
                    story_topic=details["name"],
                    genre=details["genre"],
                    story_length=details["length"]
                )

            st.session_state.generated_story = new_story

            st.rerun()

        except Exception as error:

            st.error(
                f"Could not regenerate the story: {error}"
            )


else:

    # EMPTY STORY SECTION

    st.html("""
    <section class="story-paper">

        <div class="story-overline">
            YOUR READING CORNER
        </div>

        <h2 class="empty-title">
            A blank page awaits...
        </h2>

        <p class="empty-copy">
            Your next favourite story hasn't been written yet.
            Enter an idea, choose a genre and length, and let
            your imagination take over.
        </p>

        <p class="empty-copy"
           style="color:#98754F; font-weight:700;">
            Every great book begins with a single idea. ✨
        </p>

    </section>
    """)


# ============================================================
# 12. FOOTER
# ============================================================

st.html("""
<div class="footer-note">

    THE STORY ROOM

    <br><br>

    Every great book started with a blank page. ♡

</div>
""")
