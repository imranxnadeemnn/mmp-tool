import streamlit as st

from result_view import show_result


st.set_page_config(page_title="MMP Result Viewer", layout="wide")
st.title("MMP Result Viewer")
st.caption(
    "Latest SE test postbacks from the last 7 days. "
    "Use this on a macOS machine connected to office VPN."
)

st.button("Refresh", type="primary")

with st.spinner("Fetching latest postbacks from Redash..."):
    result = show_result()

if result is None:
    st.warning("No postbacks found in the last 7 days.")
elif isinstance(result, str):
    st.error(result)
else:
    st.success(f"Showing {len(result)} postback(s) from the last 7 days.")
    st.dataframe(result, use_container_width=True)
