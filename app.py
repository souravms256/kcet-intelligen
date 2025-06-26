import streamlit as st
import os
import base64
from functools import partial
import tempfile
from datetime import datetime
import pandas as pd
import random

# Import custom modules
from api_utils import call_openai_api
from question_utils import (
    parse_markdown_files, save_questions_to_markdown,
    generate_questions_batch, predict_answer,
    predict_next_year_questions
)
from pdf_utils import create_pdf, create_answer_key_pdf
from ui_components import (
    setup_page_config, apply_custom_css, display_question,
    init_session_state
)
from constants import API_KEY, PHYSICS_CHAPTERS, CHEMISTRY_CHAPTERS, MATHEMATICS_CHAPTERS

# Set up page configuration
setup_page_config()
apply_custom_css()

# Initialize session state
init_session_state()

# Title and description
st.title("KCET Question Generator & Answer Predictor")
st.markdown("Generate new KCET-style questions, predict answers, and download the results.")

# Create an API caller function with the API key already included
api_caller = partial(call_openai_api, api_key=API_KEY)

# Sidebar for subject selection and number of questions
subject = st.sidebar.selectbox(
    "Select Subject:",
    ["Physics", "Chemistry", "Mathematics"]
)
subject_folder = subject.lower()

# Display chapter selection based on selected subject
if subject == "Physics":
    chapter = st.sidebar.selectbox("Select Chapter:", list(PHYSICS_CHAPTERS.keys()))
    chapter_value = PHYSICS_CHAPTERS[chapter]
elif subject == "Chemistry":
    chapter = st.sidebar.selectbox("Select Chapter:", list(CHEMISTRY_CHAPTERS.keys()))
    chapter_value = CHEMISTRY_CHAPTERS[chapter]
else:  # Mathematics
    chapter = st.sidebar.selectbox("Select Chapter:", list(MATHEMATICS_CHAPTERS.keys()))
    chapter_value = MATHEMATICS_CHAPTERS[chapter]

# Number of questions to generate in sidebar
num_questions_to_generate = st.sidebar.number_input(
    "Number of questions to generate:",
    min_value=1,
    max_value=50,
    value=10,
    step=1
)

# Function to report a question with unique keys per tab
def report_question(idx, tab_name):
    unique_idx = f"{tab_name}_{idx}"
    st.session_state.reported_questions.add(idx)
    st.session_state.reported_reasons[idx] = st.text_input(
        f"Reason for reporting question {idx+1}:",
        key=f"reason_{unique_idx}"
    )
    st.session_state.reported_answers[idx] = st.text_input(
        f"Correct answer for question {idx+1}:",
        key=f"answer_{unique_idx}"
    )
    st.success(f"Question {idx+1} has been reported for review.")

# Progress bar for generation
def run_generation_process(num_questions):
    with st.spinner("Generating questions..."):
        progress_bar = st.progress(0)

        # Choose source questions
        if not st.session_state.source_questions:
            st.session_state.source_questions = parse_markdown_files(subject_folder)

        source_questions = st.session_state.source_questions
        if not source_questions:
            st.error("No questions found in the selected subject folder. Please ensure there are Markdown files with questions.")
            return False

        # Generate new questions
        new_questions = []
        for i in range(num_questions):
            # Generate new question
            if len(source_questions) > 0:
                idx = random.randint(0, len(source_questions)-1)
                question, options = source_questions[idx]
                response = generate_questions_batch([source_questions[idx]], 1, subject, chapter_value, api_caller)
                if response:
                    new_questions.extend(response)

            # Update progress bar
            progress_bar.progress((i + 1) / num_questions)

        # Save the generated questions
        st.session_state.new_questions = new_questions
        st.session_state.generated = True if new_questions else False

        # Save to markdown file
        output_file = save_questions_to_markdown(new_questions, subject_folder)
        if output_file:
            st.session_state.output_file = output_file

        return True if new_questions else False

# Function to predict answers for all questions
def predict_answers():
    with st.spinner("Predicting answers..."):
        progress_bar = st.progress(0)

        predicted_questions = []
        for i, (question, options) in enumerate(st.session_state.new_questions):
            # Predict answer
            answer = predict_answer(question, options, api_caller)
            predicted_questions.append((question, options, answer))

            # Update progress bar
            progress_bar.progress((i + 1) / len(st.session_state.new_questions))

        st.session_state.predicted_questions = predicted_questions
        st.session_state.answers_predicted = True

# Main interface with tabs
tabs = st.tabs(["Generate Questions", "Predict Answers", "Predict Next Year's Questions", "Download Results"])

# Tab 1: Generate Questions
with tabs[0]:
    st.header("Generate New Questions")

    # Display the number of available source questions
    if not st.session_state.source_questions:
        st.session_state.source_questions = parse_markdown_files(subject_folder)

    total_source_questions = len(st.session_state.source_questions)
    # st.info(f"Number of available source questions: {total_source_questions}")

    # Generation button
    if st.button("Generate Questions", key="gen_btn"):
        success = run_generation_process(num_questions_to_generate)
        if success:
            st.success(f"Successfully generated {len(st.session_state.new_questions)} questions!")

    # Refresh button to generate new questions while staying on the same tab
    if st.session_state.generated:
        if st.button("Refresh with New Questions", key="refresh_btn"):
            success = run_generation_process(num_questions_to_generate)
            if success:
                st.success(f"Generated {len(st.session_state.new_questions)} new questions!")

    # Display generated questions
    if st.session_state.generated:
        with st.expander("Generated Questions", expanded=True):
            for i, (question, options) in enumerate(st.session_state.new_questions):
                # Override the index to make keys unique
                gen_index = i + 1000  # Add 1000 to create unique indices for this tab
                st.markdown(f"**Question {i+1}**: {question}")
                for j, opt in enumerate(options):
                    st.markdown(f"({j+1}) {opt}")
                if st.button("Report", key=f"report_gen_{i}", help="Report this question as incorrect"):
                    report_question(i, "gen")
                st.write("---")

# Tab 2: Predict Answers
with tabs[1]:
    st.header("Predict Answers")

    if not st.session_state.generated:
        st.warning("Please generate questions first in the 'Generate Questions' tab.")
    else:
        if st.button("Predict Answers for All Questions"):
            predict_answers()

        if st.session_state.answers_predicted:
            with st.expander("Questions with Predicted Answers", expanded=True):
                for i, (question, options, answer) in enumerate(st.session_state.predicted_questions):
                    st.markdown(f"**Question {i+1}**: {question}")
                    for j, opt in enumerate(options):
                        st.markdown(f"({j+1}) {opt}")
                    try:
                        answer_index = int(answer) - 1
                        st.success(f"**Predicted Answer**: {options[answer_index]}")
                    except:
                        st.warning(f"Could not display predicted answer properly. Raw: {answer}")
                    if st.button("Report", key=f"report_pred_{i}", help="Report this question as incorrect"):
                        report_question(i, "pred")
                    st.write("---")

# Tab 3: Predict Next Year's Questions
with tabs[2]:
    st.header("Predict Next Year's Questions")

    if not st.session_state.generated:
        st.warning("Please generate questions first in the 'Generate Questions' tab.")
    else:
        if st.button("Predict Next Year's Questions"):
            with st.spinner("Predicting next year's questions..."):
                progress_bar = st.progress(0)

                next_year_questions = predict_next_year_questions(
                    st.session_state.new_questions,
                    subject,
                    api_caller
                )

                progress_bar.progress(1.0)
                st.session_state.next_year_questions = next_year_questions
                st.session_state.next_year_predicted = True

                if next_year_questions:
                    st.success(f"Successfully predicted {len(next_year_questions)} questions for next year!")

        if st.session_state.next_year_predicted:
            with st.expander("Predicted Next Year's Questions", expanded=True):
                for i, (question, options) in enumerate(st.session_state.next_year_questions):
                    st.markdown(f"**Question {i+1}**: {question}")
                    for j, opt in enumerate(options):
                        st.markdown(f"({j+1}) {opt}")
                    if st.button("Report", key=f"report_next_{i}", help="Report this question as incorrect"):
                        report_question(i, "next")
                    st.write("---")

# Tab 4: Download Results
with tabs[3]:
    st.header("Download Results")

    if not st.session_state.generated:
        st.warning("Please generate questions first in the 'Generate Questions' tab.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Questions Only")

            # Download questions as Markdown
            if st.session_state.output_file:
                with open(st.session_state.output_file, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()

                st.download_button(
                    label="Download Questions (Markdown)",
                    data=markdown_content,
                    file_name=f"KCET_{subject}_Questions.md",
                    mime="text/markdown"
                )

                # Create and download PDF without answers
                pdf_file_path = create_pdf(st.session_state.new_questions, subject, include_answers=False)
                if pdf_file_path:
                    with open(pdf_file_path, 'rb') as f:
                        pdf_content = f.read()
                    st.download_button(
                        label="Download Questions (PDF)",
                        data=pdf_content,
                        file_name=f"KCET_{subject}_Questions.pdf",
                        mime="application/pdf"
                    )
                    os.remove(pdf_file_path)  # Clean up the temporary file

        with col2:
            st.subheader("Questions with Answer Key")

            if st.session_state.answers_predicted:
                # Download with answers as Markdown
                answer_markdown = ""
                for i, (question, options, answer) in enumerate(st.session_state.predicted_questions):
                    answer_markdown += f"### Question {i+1}\n\n{question}\n\n"
                    for j, option in enumerate(options):
                        if j == answer:
                            answer_markdown += f"* **{option}** (Correct)\n"
                        else:
                            answer_markdown += f"* {option}\n"
                    answer_markdown += "\n---\n\n"

                st.download_button(
                    label="Download with Answers (Markdown)",
                    data=answer_markdown,
                    file_name=f"KCET_{subject}_Questions_Answers.md",
                    mime="text/markdown"
                )

                # Create and download PDF with answers
                pdf_with_answers_path = create_pdf(st.session_state.predicted_questions, subject, include_answers=True)
                if pdf_with_answers_path:
                    with open(pdf_with_answers_path, 'rb') as f:
                        pdf_with_answers_content = f.read()
                    st.download_button(
                        label="Download with Answers (PDF)",
                        data=pdf_with_answers_content,
                        file_name=f"KCET_{subject}_Questions_Answers.pdf",
                        mime="application/pdf"
                    )
                    os.remove(pdf_with_answers_path)  # Clean up the temporary file
            else:
                st.info("Please predict answers in the 'Predict Answers' tab first to download questions with answers.")

    # Reports section
    if st.session_state.reported_questions:
        st.header("Reported Questions")
        reported_data = {
            "Question Index": [],
            "Reason": [],
            "Correct Answer": []
        }

        for idx in st.session_state.reported_questions:
            reported_data["Question Index"].append(idx + 1)
            reported_data["Reason"].append(st.session_state.reported_reasons.get(idx, ""))
            reported_data["Correct Answer"].append(st.session_state.reported_answers.get(idx, ""))

        reported_df = pd.DataFrame(reported_data)
        st.dataframe(reported_df)

        # Export reports
        csv = reported_df.to_csv(index=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="Download Reports (CSV)",
            data=csv,
            file_name=f"KCET_Reports_{timestamp}.csv",
            mime="text/csv"
        )

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2024 KCET Question Generator")
st.sidebar.markdown("Made with ❤️ using Streamlit")

# Display any system messages or errors
if "system_message" in st.session_state and st.session_state.system_message:
    st.sidebar.error(st.session_state.system_message)
