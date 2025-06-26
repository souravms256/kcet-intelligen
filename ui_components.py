# ui_components.py
import streamlit as st

def setup_page_config():
    """Set up the page configuration"""
    st.set_page_config(
        page_title="KCET Question Generator & Answer Predictor",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    """Apply custom CSS styling to the app"""
    st.markdown("""
    <style>
        .stApp {
            background-color: #121212;
            color: white;
        }
        .stButton>button {
            background-color: #444;
            color: white;
        }
        .stProgress>div>div {
            background-color: #e74c3c;
        }
        h1, h2, h3 {
            color: white;
        }
        .stTab {
            background-color: #333;
            color: white;
        }
        .stTab[data-baseweb="tab"][aria-selected="true"] {
            background-color: #e74c3c;
            color: white;
        }
        .report-btn {
            background-color: transparent;
            color: #ff4d4d;
            border: none;
            cursor: pointer;
            text-decoration: underline;
            font-size: 0.8rem;
            padding: 0;
        }
        .download-btn {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #2ecc71;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        .download-btn:hover {
            background-color: #27ae60;
        }
        .question-box {
            background-color: #1e1e1e;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            border-left: 3px solid #e74c3c;
        }
        .answer-highlight {
            color: #2ecc71;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

def display_question(question, options, index, answer=None, with_report_button=True):
    """Display a question with options and optionally answer"""
    question_container = st.container()
    with question_container:
        st.markdown(f"<div class='question-box'>", unsafe_allow_html=True)
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.write(f"*Q{index+1}:* {question}")
            for j, opt in enumerate(options):
                st.write(f"({j+1}) {opt}")
            if answer:
                st.markdown(f"*Predicted Answer:* <span class='answer-highlight'>Option {answer}</span>", unsafe_allow_html=True)
        
        if with_report_button:
            with col2:
                if st.button("Report", key=f"report_{index}", help="Report this question as incorrect"):
                    return True  # User clicked report
        st.markdown("</div>", unsafe_allow_html=True)
    return False  # User did not click report

def init_session_state():
    """Initialize session state variables"""
    if 'generated' not in st.session_state:
        st.session_state.generated = False
    if 'answers_predicted' not in st.session_state:
        st.session_state.answers_predicted = False
    if 'output_file' not in st.session_state:
        st.session_state.output_file = None
    if 'new_questions' not in st.session_state:
        st.session_state.new_questions = []
    if 'predicted_questions' not in st.session_state:
        st.session_state.predicted_questions = []
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Generate Questions"
    if 'uploaded_questions' not in st.session_state:
        st.session_state.uploaded_questions = []
    if 'reported_questions' not in st.session_state:
        st.session_state.reported_questions = set()
    if 'reported_reasons' not in st.session_state:
        st.session_state.reported_reasons = {}
    if 'reported_answers' not in st.session_state:
        st.session_state.reported_answers = {}
    if 'source_questions' not in st.session_state:
        st.session_state.source_questions = []
    if 'next_year_questions' not in st.session_state:
        st.session_state.next_year_questions = []
    if 'next_year_predicted' not in st.session_state:
        st.session_state.next_year_predicted = False