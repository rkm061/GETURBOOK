import streamlit as st
import pandas as pd
from io import BytesIO

# ---------- Page Config ----------
st.set_page_config(page_title="📚 Book Catalogue", layout="wide")

# ---------- Load Data ----------
@st.cache_data
def load_data():
    return pd.read_csv("goodreads_data_updated.csv")

df = load_data()

# ---------- Session State ----------
if "end_row" not in st.session_state:
    st.session_state.end_row = 100


# ---------- Sidebar Filters ----------
st.sidebar.header("🔍 Filter Books")

# Rating filter
selected_rating = st.sidebar.radio("Minimum Rating", options=[0, 1, 2, 3, 4, 5], horizontal=True)

# Dynamic Genre filter
all_genres = sorted({genre.strip() for sublist in df["Genres List"].dropna().str.split(',') for genre in sublist})
# genre_query = st.sidebar.text_input("🎭 Genre", help="Start typing to filter genres")
# filtered_genres = [g for g in all_genres if all_genres.lower() in g.lower()]
selected_genres = st.sidebar.multiselect(
    "Genre",
    options=all_genres,
    default=[],
    # help="Start typing to filter genres"
)




# Dynamic Author filter
all_authors = sorted(df["Author Name"].dropna().unique())
# author_query = st.sidebar.text_input("✍️ Author")
# filtered_authors = [a for a in all_authors if all_authors.lower() in a.lower()]
selected_authors = st.sidebar.multiselect(
    "Author",
    options=all_authors,
    default=[],
    # help="Start typing to filter authors"
)
sort_col = st.sidebar.selectbox("Sort By", options=[
   "No Of Rating", "Rating", "Author Name", "Book Title", "No Of Pages"
], placeholder = "Choose an option")
sort_order = st.sidebar.radio("Sort Order", ["Descending", "Ascending"])

# ---------- Apply Filters ----------
filtered_df = df.copy()

if selected_genres:
    filtered_df = filtered_df[filtered_df["Genres List"].apply(
        lambda x: any(g in x for g in selected_genres) if pd.notna(x) else False
    )]

if selected_authors:
    filtered_df = filtered_df[filtered_df["Author Name"].isin(selected_authors)]

filtered_df = filtered_df[filtered_df["Rating"] >= selected_rating]

filtered_df = filtered_df.sort_values(
    by=sort_col,
    ascending=(sort_order == "Ascending")
)


# ---------- Styling ----------
st.markdown("""
<style>
    section.main > div { padding: 0rem 0.5rem; }
    .block-container { padding-left: 0rem; padding-top: 3rem; padding-bottom: 0rem; }
    div[data-testid="column"] {
        /*padding-left: 0rem !important;
        padding-right: 0rem !important;
        margin-top: -4px !important;  /* Reduce vertical space between columns */
        column-gap: 0.25rem !important;  /* Reduce this value to tighten spacing */
        margin-bottom: -4px !important; */
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
        margin-top: -6px !important;
        margin-bottom: -6px !important;
        gap: 0.25rem !important; /* Ensures tight horizontal spacing */
    }
    .stMarkdown, .stImage, .stButton {
        margin: 0 !important;
        line-height: 1;  /* Reduce from 1.2 to 1 */
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .element-container {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin-top: 6px !important;  /* Reduced from 10px to 6px */
        margin-bottom: 6px !important;  /* Reduced from 10px to 6px */
    }
    .book-row hr {
        margin: 0;
    }
    /* Target paragraph elements */
    p {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    /* Target the row dividers */
    hr {
        margin: 10px 0 !important;
        padding: 0 !important;
    }
    /* Target vertical block containers */
    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    /* Increased font size for all text */
    .book-content {
        font-size: 1rem !important;  /* Increased from 0.9rem */
    }
    .book-title {
        font-size: 1.05rem !important;  /* Increased from 0.92rem */
        font-weight: 500;
    }
    /* Better star alignment */
    .rating-container {
        display: flex;
        align-items: center;
        line-height: 1;
    }
    .rating-stars {
        display: inline-flex;
        align-items: center;
        height: 18px;
    }
    .rating-stars span, .rating-stars svg {
        display: inline-block;
        height: 18px;
        line-height: 1;
        vertical-align: middle;
    }
    .rating-value {
        margin-left: 5px;
        font-size: 0.9rem;
        color: #555;
        line-height: 1;
    }
    /* Fix SVG alignment */
    svg {
        vertical-align: middle;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
# Adjusted column widths - reduced gap between ratings and genres
header = st.columns([2.5, 2.2, 1.8, 1.4, 2.3, 1, 1, 0.8])
header[0].markdown("**Book Title**")
header[1].markdown("**Author**")
header[2].markdown("**Rating**")
header[3].markdown("**# Ratings**")
header[4].markdown("**Genres**")
header[5].markdown("**Goodread Link**")
header[6].markdown("**Aamzon Link**")
header[7].markdown("**Pages**")

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
# ---------- Row Renderer ----------
visible_df = filtered_df.iloc[:st.session_state.end_row]

for _, row in visible_df.iterrows():
    # Adjusted column widths to match header
    cols = st.columns([2.5, 2.2, 1.8, 1.4, 2.3, 1, 1, 0.8])
    with cols[0]:
        st.markdown(f"<div class='book-title'>{row['Book Title']}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='book-content'>{row['Author Name']}</div>", unsafe_allow_html=True)
    with cols[2]:
        rating = row['Rating']
        if pd.notna(rating):
            # Convert rating to float and handle the decimal part more precisely
            rating_float = float(rating)
            full_stars = int(rating_float)
            decimal_part = rating_float - full_stars
            
            # Determine if we should show a half star or partial star
            half_star = 0.25 <= decimal_part < 0.75
            almost_full_star = decimal_part >= 0.75
            empty_stars = 5 - full_stars - int(half_star) - int(almost_full_star)

            # Start rating container div
            star_html = "<div class='rating-container'><div class='rating-stars'>"

            # Full stars
            for _ in range(full_stars):
                star_html += "<span style='color: gold; font-size: 18px; line-height: 1;'>★</span>"

            # Half star
            if half_star:
                star_html += """
                    <svg width="18" height="18" viewBox="0 0 24 24">
                        <defs>
                            <linearGradient id="half-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="50%" stop-color="gold"/>
                                <stop offset="50%" stop-color="#ddd"/>
                            </linearGradient>
                        </defs>
                        <path fill="url(#half-grad)" d="M12 .587l3.668 7.568L24 9.75l-6 5.847L19.335 24 12 20.01 4.665 24 6 15.597 0 9.75l8.332-1.595z"/>
                    </svg>
                """
            
            # Almost full star (for ratings like 3.9)
            elif almost_full_star:
                percentage = int(decimal_part * 100)
                star_html += f"""
                    <svg width="18" height="18" viewBox="0 0 24 24">
                        <defs>
                            <linearGradient id="partial-grad-{percentage}" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="{percentage}%" stop-color="gold"/>
                                <stop offset="{percentage}%" stop-color="#ddd"/>
                            </linearGradient>
                        </defs>
                        <path fill="url(#partial-grad-{percentage})" d="M12 .587l3.668 7.568L24 9.75l-6 5.847L19.335 24 12 20.01 4.665 24 6 15.597 0 9.75l8.332-1.595z"/>
                    </svg>
                """

            # Empty stars
            for _ in range(empty_stars):
                star_html += "<span style='color: #ddd; font-size: 18px; line-height: 1;'>★</span>"

            # Close stars div and add numeric rating
            star_html += f"</div><span class='rating-value'>{rating_float:.1f}</span></div>"

            st.markdown(star_html, unsafe_allow_html=True)
        else:
            st.text("N/A")

    with cols[3]:
        st.markdown(f"<div class='book-content'>{int(row['No Of Rating']):,}</div>", unsafe_allow_html=True)
    with cols[4]:
        genres = row['Genres List']
        if pd.notna(genres):
            genre_items = [g.strip() for g in genres.split(',')]
            preview = ', '.join(genre_items[:2])
            needs_more = len(genre_items) > 2
            unique_id = f"genre-details-{_}"

            if needs_more:
                st.markdown(
                    f"""
                    <div class='book-content' style='white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>
                        {preview},
                        <details id="{unique_id}" style="display:inline;">
                            <summary style="color:#0066cc; display:inline; font-weight:bold; cursor:pointer;">more</summary>
                            <div style='margin-top:2px; white-space: normal;'>{genres}</div>
                        </details>
                    </div>

                    <script>
                        const detailsElem = document.getElementById("{unique_id}");
                        if (detailsElem) {{
                            detailsElem.addEventListener("toggle", function() {{
                                if (this.open) {{
                                    const summary = this.querySelector("summary");
                                    if (summary) {{
                                        summary.style.display = "none";
                                    }}
                                }}
                            }});
                        }}
                    </script>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(f"<div class='book-content' style='white-space: nowrap;'>{genres}</div>", unsafe_allow_html=True)

    with cols[5]:
        st.markdown(
            f'''<div style="text-align: center;">
                    <a href="{row["Detail Url"]}">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/4/4b/Goodreads_%27g%27_logo.png" width="20" height="20">
                    </a>
                </div>''',
            unsafe_allow_html=True
        )

    with cols[6]:
        st.markdown(
            f'''<div style="text-align: center;">
                    <a href="{row["Amazon Link"]}">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/d/de/Amazon_icon.png" width="20" height="20">
                    </a>
                </div>''',
            unsafe_allow_html=True)

    with cols[7]:
        st.markdown(f"<div class='book-content'>{str(row['No Of Pages'])}</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

# ---------- Infinite Scroll ----------
if st.session_state.end_row < len(filtered_df):
    if st.button("Load More", use_container_width=True):
        st.session_state.end_row += 100
        st.rerun()
else:
    st.success("You've reached the end!")
