import streamlit as st

from result_view import show_result


st.set_page_config(page_title="MMP Result Viewer", layout="wide")
st.title("MMP Result Viewer")
st.caption(
    "Latest SE test postbacks from the last 7 days. "
    "Use this on a macOS machine connected to office VPN."
)

search = st.text_input(
    "Search Advertising ID",
    placeholder="Type an advertising_id to filter (leave blank to show all)",
)
st.button("Refresh", type="primary")

with st.spinner("Fetching latest postbacks from Redash..."):
    result = show_result()

if result is None:
    st.warning("No postbacks found in the last 7 days.")
elif isinstance(result, str):
    st.error(result)
else:
    total = len(result)
    query = (search or "").strip()

    if query:
        if "advertising_id" in result.columns:
            result = result[
                result["advertising_id"]
                .astype(str)
                .str.contains(query, case=False, na=False)
            ]
            st.success(
                f"Showing {len(result)} of {total} postback(s) "
                f"matching '{query}'."
            )
        else:
            st.warning("No advertising_id column in the result set.")
    else:
        st.success(f"Showing {total} postback(s) from the last 7 days.")

    st.dataframe(result, use_container_width=True)
