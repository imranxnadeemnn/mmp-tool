import streamlit as st

from result_view import show_result


st.set_page_config(page_title="MMP Result Viewer", layout="wide")
st.title("MMP Result Viewer")
st.caption("Use this on a macOS machine connected to office VPN.")

advertising_id = st.text_input("Advertising ID", placeholder="Enter GAID / IDFA")

if st.button("Check Result", type="primary") or advertising_id:
    if not advertising_id:
        st.warning("Advertising ID is required.")
    else:
        with st.spinner("Fetching result from Redash..."):
            result = show_result(advertising_id.strip())

        if result is None:
            st.warning("No result found.")
        elif isinstance(result, str):
            st.error(result)
        else:
            st.success(f"Fetched {len(result)} row(s).")
            st.dataframe(result, use_container_width=True)
