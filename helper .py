import os
import json
import asyncio
import sys
from datetime import datetime
from typing import Dict, List, Any

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ModuleNotFoundError:
    STREAMLIT_AVAILABLE = False

# Check platform compatibility for grp module
if sys.platform.startswith("linux") or sys.platform == "darwin":
    try:
        import grp
        GRP_AVAILABLE = True
    except ModuleNotFoundError:
        GRP_AVAILABLE = False
else:
    GRP_AVAILABLE = False

# Handle missing helper module gracefully
try:
    from helper import ChatBot, current_year, save_to_audio
    HELPER_AVAILABLE = True
except ImportError:
    HELPER_AVAILABLE = False

# Dummy search function to replace DuckDuckGo news search
def fetch_search_results(query: str, location: str, num: int, time_filter: str) -> Dict[str, Any]:
    """
    Mock function to simulate search results.
    """
    return {
        "status": "success",
        "results": [
            {
                "title": f"Sample news about {query}",
                "link": "https://example.com/news",
                "summary": f"Summary of the latest {query} news.",
                "rating": "4.5"
            }
            for _ in range(num)
        ]
    }

if STREAMLIT_AVAILABLE:
    # Set Streamlit layout
    st.set_page_config(layout="wide")
    st.title("SearchBot 🤖")

    # Sidebar for settings
    with st.sidebar:
        num: int = st.number_input("📊 Number of results", value=3, step=1, min_value=1, max_value=10)
        location: str = st.text_input("🌍 Location (e.g., us-en, in-en)", value="us-en")
        time_filter: str = st.selectbox("⏳ Time filter", ["Past Day", "Past Week", "Past Month", "Past Year"], index=1)
        
        time_mapping = {"Past Day": "d", "Past Week": "w", "Past Month": "m", "Past Year": "y"}
        time_filter = time_mapping[time_filter]
        only_use_chatbot: bool = st.checkbox("💬 Only use chatbot (Disable Search)")
        
        if st.button("🧹 Clear Session"):
            st.session_state.messages = []
            st.rerun()
        
        if HELPER_AVAILABLE:
            st.markdown(f"<h6>📅 Copyright © 2010-{current_year()} Present</h6>", unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything!"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        ref_table_string = "**No references found.**"
        search_results = {"status": "failure", "results": []}
        
        try:
            with st.spinner("Searching..."):
                if not only_use_chatbot:
                    search_results = fetch_search_results(query=prompt, location=location, num=num, time_filter=time_filter)
                    
                response = """Here are your search results:
                """
                
                if search_results["status"] == "success":
                    md_data = search_results["results"]
                    ref_table_string = "| Num | Title | Rating | Context |\n|---|------|--------|---------|\n"
                    
                    for idx, res in enumerate(md_data, start=1):
                        title = f"[{res['title']}]({res['link']})"
                        stars = "⭐" * int(float(res.get('rating', '0')))
                        summary = res.get('summary', '')[:100] + "..."
                        ref_table_string += f"| {idx} | {title} | {stars} | {summary} |\n"
                    
                if HELPER_AVAILABLE:
                    bot = ChatBot()
                    bot.history = st.session_state.messages.copy()
                    response = bot.generate_response(f"User prompt: {prompt}\n\nContext: {', '.join(res.get('summary', '') for res in search_results['results'])}")
                else:
                    response = "Chatbot functionality is unavailable. Please check the helper module installation."
        
        except Exception as e:
            st.warning(f"Error fetching data: {e}")
            response = "We encountered an issue. Please try again later."
        
        if HELPER_AVAILABLE:
            save_to_audio(response)
        
        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)
            if HELPER_AVAILABLE:
                st.audio("output.mp3", format="audio/mpeg", loop=True)
            with st.expander("References:", expanded=True):
                st.markdown(ref_table_string, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": f"{response}\n\n{ref_table_string}"})
else:
    print("Streamlit is not installed. Please install it using `pip install streamlit` to run this application.")

if not GRP_AVAILABLE:
    print("The 'grp' module is not available in this environment. Skipping grp-related functionality.")

if not HELPER_AVAILABLE:
    print("The 'helper' module is not available. Chatbot features will be disabled.")
