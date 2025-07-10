import streamlit as st
from urllib.parse import urlparse
from hybrid_search import search


st.title("Blog Mini-Search")

# compact CSS layout
st.markdown("""
<style>
div.row-widget.stMarkdown p { margin: 0.1rem 0; line-height: 1.1; }
.element-container > div > div > div > div { font-size: 0.9rem !important; }
</style>
""", unsafe_allow_html=True)


def shorten(url: str, max_len: int = 60) -> str:
    """Return domain + truncated path, e.g. paulgraham.com/this/is/…"""
    parsed = urlparse(url)
    text   = f"{parsed.netloc}{parsed.path}"
    return (text[: max_len - 1] + "…") if len(text) > max_len else text


query = st.text_input("Search blogs…")
if query:
    hits = search(query)
    for rank, hit in enumerate(hits, 1):
        col1, col2 = st.columns([8, 1])
        with col1:
            link_text = shorten(hit["url"])
            st.markdown(
                f"{rank}. <a href='{hit['url']}' target='_blank'>{link_text}</a>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(f"`{hit['score']:.4f}`")