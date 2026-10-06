import streamlit as st
import sqlite3
from datetime import datetime

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Personal Diary",
    page_icon="📖",
    layout="wide"
)

# -----------------------------
# Database
# -----------------------------
conn = sqlite3.connect("diary.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    mood TEXT NOT NULL,
    date TEXT NOT NULL
)
""")

conn.commit()


# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>

.main {
    background-color: #faf7ff;
}

.title {
    font-size: 42px;
    font-weight: bold;
    color: #6a3dad;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #666666;
    margin-bottom: 25px;
}

.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    border: 1px solid #eeeeee;
}

.mood {
    font-size: 25px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# Header
# -----------------------------
st.markdown(
    '<div class="title">📖 AI Personal Diary</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your private space to write, reflect and remember.</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Menu")

menu = st.sidebar.radio(
    "Choose an option",
    [
        "✍️ New Entry",
        "📚 My Diary",
        "🔍 Search",
        "📊 Mood Summary"
    ]
)


# ==========================================================
# NEW ENTRY
# ==========================================================

if menu == "✍️ New Entry":

    st.header("Write a New Diary Entry")

    title = st.text_input(
        "Diary Title",
        placeholder="Give your diary entry a title..."
    )

    mood = st.selectbox(
        "How are you feeling today?",
        [
            "😊 Happy",
            "😌 Calm",
            "😄 Excited",
            "🥰 Loved",
            "😐 Normal",
            "😔 Sad",
            "😡 Angry",
            "😰 Stressed"
        ]
    )

    content = st.text_area(
        "Your thoughts",
        height=300,
        placeholder="Write whatever is on your mind..."
    )

    if st.button("💾 Save Entry", use_container_width=True):

        if title.strip() == "":
            st.warning("Please enter a diary title.")

        elif content.strip() == "":
            st.warning("Please write something in your diary.")

        else:

            current_date = datetime.now().strftime(
                "%d %B %Y, %I:%M %p"
            )

            cursor.execute(
                """
                INSERT INTO entries
                (title, content, mood, date)
                VALUES (?, ?, ?, ?)
                """,
                (
                    title,
                    content,
                    mood,
                    current_date
                )
            )

            conn.commit()

            st.success("Your diary entry has been saved! 💜")


# ==========================================================
# MY DIARY
# ==========================================================

elif menu == "📚 My Diary":

    st.header("📚 My Diary")

    cursor.execute(
        """
        SELECT id, title, content, mood, date
        FROM entries
        ORDER BY id DESC
        """
    )

    entries = cursor.fetchall()

    if not entries:

        st.info(
            "You don't have any diary entries yet. "
            "Create your first entry!"
        )

    else:

        for entry in entries:

            entry_id = entry[0]
            title = entry[1]
            content = entry[2]
            mood = entry[3]
            date = entry[4]

            with st.container():

                st.markdown(
                    '<div class="card">',
                    unsafe_allow_html=True
                )

                st.subheader(title)

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.caption(date)

                with col2:
                    st.write(mood)

                st.write(content)

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{entry_id}"
                ):

                    cursor.execute(
                        "DELETE FROM entries WHERE id = ?",
                        (entry_id,)
                    )

                    conn.commit()

                    st.success("Entry deleted.")

                    st.rerun()

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True
                )


# ==========================================================
# SEARCH
# ==========================================================

elif menu == "🔍 Search":

    st.header("🔍 Search Your Diary")

    search_text = st.text_input(
        "Search",
        placeholder="Search by title or words..."
    )

    if search_text:

        cursor.execute(
            """
            SELECT id, title, content, mood, date
            FROM entries
            WHERE title LIKE ?
               OR content LIKE ?
            ORDER BY id DESC
            """,
            (
                "%" + search_text + "%",
                "%" + search_text + "%"
            )
        )

        results = cursor.fetchall()

        if not results:

            st.warning("No matching entries found.")

        else:

            st.success(
                f"{len(results)} matching entry/entries found."
            )

            for entry in results:

                st.subheader(entry[1])

                st.caption(
                    f"{entry[4]}   |   {entry[3]}"
                )

                st.write(entry[2])

                st.divider()


# ==========================================================
# MOOD SUMMARY
# ==========================================================

elif menu == "📊 Mood Summary":

    st.header("📊 Mood Summary")

    cursor.execute(
        """
        SELECT mood, COUNT(*)
        FROM entries
        GROUP BY mood
        ORDER BY COUNT(*) DESC
        """
    )

    moods = cursor.fetchall()

    if not moods:

        st.info("Write some diary entries to see your mood summary.")

    else:

        st.subheader("Your Mood History")

        for mood, count in moods:

            st.write(f"**{mood}**")

            st.progress(
                min(count / max(1, sum(x[1] for x in moods)), 1.0)
            )

            st.caption(
                f"{count} entr{'y' if count == 1 else 'ies'}"
            )


# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption(
    "AI Personal Diary • Your thoughts, your memories, your space."
)