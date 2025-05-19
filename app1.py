import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import requests
import json

# Configure Google AI API (Ensure API Key is correct)
genai.configure(api_key="AIzaSyCc9XkSgKLFXa9U4yw6VnPJ7H29be4qc90")

# Function to get AI tool recommendations
def get_ai_tools(query):
    prompt = (
        f"Suggest AI tools for the following requirement: {query}. "
        "Categorize them into Video, Image, Text, Audio, and General AI tools. "
        "Provide tool names, descriptions, links (if available), and user ratings."
    )
    
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Change if needed
        response = model.generate_content(prompt)
        return response.text if hasattr(response, "text") else "No response received."
    except Exception as e:
        return f"Error: {e}"

# Function to generate PDF
def generate_pdf(content, filename="ai_tool_recommendations.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(filename)
    return filename

# Function to fetch AI news
def get_ai_news():
    try:
        response = requests.get("https://newsapi.org/v2/everything?q=AI&apiKey=8973697c2ba2489984bb0315150d8560")
        news_data = response.json()
        articles = news_data.get("articles", [])[:5]  # Get top 5 news articles
        news_list = "\n\n".join([f"🔹 {article['title']} - {article['url']}" for article in articles])
        return news_list if news_list else "<span class='no-news'>No recent AI news found.</span>"
    except Exception as e:
        return f"Error fetching news: {e}"

# Streamlit UI with Dark Mode Toggle
st.set_page_config(layout="wide", page_title="AI Tool Recommender", page_icon="🤖")
st.title("🤖 AI Tool Recommender")
st.write("Find the best AI tools for your needs!")

# Dark Mode Toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if st.sidebar.button("🌙 Toggle Dark Mode" if not st.session_state.dark_mode else "☀️ Toggle Light Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

if st.session_state.dark_mode:
    st.markdown("""
        <style>
            body, .stApp { background-color: #121212; color: white !important; }
            .stTextInput, .stTextArea, .stSelectbox, .stButton { color: black !important; }
            .stSidebar { background-color: #1e1e1e !important; }
            .stMarkdown span.no-news, .stMarkdown span.query-text { color: white !important; }
            .stDownloadButton button { background-color: white !important; color: black !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .stMarkdown span.query-text { color: black !important; }
        </style>
    """, unsafe_allow_html=True)

# Sidebar for Search History and News
st.sidebar.header("📜 Search History")
if "history" not in st.session_state:
    st.session_state.history = []
for item in st.session_state.history:
    with st.sidebar.expander(f"🔍 {item['query']}"):
        st.write(item['response'])

# Download Search History Button (Moved Under Search History)
if st.sidebar.button("Download Search History as PDF"):
    if st.session_state.history:
        history_content = "\n\n".join([f"Query: {item['query']}\nResponse: {item['response']}" for item in st.session_state.history])
        history_pdf_filename = generate_pdf(history_content, "search_history.pdf")
        with open(history_pdf_filename, "rb") as pdf_file:
            st.sidebar.download_button(
                label="📄 Download Search History as PDF",
                data=pdf_file,
                file_name="search_history.pdf",
                mime="application/pdf"
            )
    else:
        st.sidebar.warning("No search history available to export.")

st.sidebar.header("📰 Latest AI News")
ai_news = get_ai_news()
st.sidebar.markdown(ai_news, unsafe_allow_html=True)

# User input
st.markdown("<span class='query-text'>Describe what you need AI for?</span>", unsafe_allow_html=True)
query = st.text_area("", placeholder="e.g., I need to create a video using AI")
predefined_queries = [
    "I need an AI tool for image editing",
    "Find an AI for text summarization",
    "What AI can generate music?",
    "Best AI for writing blog posts"
]
st.markdown("<span class='query-text'>Need help? Choose a suggested query:</span>", unsafe_allow_html=True)
selected_query = st.selectbox("", ["Select a query..."] + predefined_queries)
if selected_query != "Select a query...":
    query = selected_query

if st.button("Find AI Tools"):
    if query:
        with st.spinner("Searching for AI tools... 🔍"):
            recommendations = get_ai_tools(query)
            st.session_state.history.append({"query": query, "response": recommendations})
            
            st.subheader("🔧 Recommended AI Tools")
            st.markdown(recommendations, unsafe_allow_html=True)
            
            # Generate PDF and provide download option
            pdf_filename = generate_pdf(recommendations)
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="Download AI Tool Recommendations as PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
    else:
        st.warning("Please enter a query to find AI tools.")
