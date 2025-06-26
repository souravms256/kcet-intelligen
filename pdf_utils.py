# pdf_utils.py
from fpdf import FPDF
import tempfile
import streamlit as st

def sanitize_for_pdf(text):
    """Sanitize text for PDF output"""
    # Replace problematic characters with safe alternatives
    text = text.encode('latin-1', 'replace').decode('latin-1')
    # Replace the replacement character with something readable
    text = text.replace('?', '(symbol)')
    return text

def create_pdf(questions, subject, include_answers=True):
    """Create a PDF with questions and optionally answers"""
    try:
        class CustomPDF(FPDF):
            def header(self):
                # Set font for the header
                self.set_font('Arial', 'B', 12)
                # Title
                self.cell(0, 10, f'KCET {subject} Questions', 0, 1, 'C')
                # Line break
                self.ln(4)

            def footer(self):
                # Go to 1.5 cm from bottom
                self.set_y(-15)
                # Select Arial italic 8
                self.set_font('Arial', 'I', 8)
                # Print centered page number
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = CustomPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for i, item in enumerate(questions, 1):
            question = sanitize_for_pdf(item[0])
            options = [sanitize_for_pdf(opt) for opt in item[1]]
            answer = item[2] if len(item) > 2 and include_answers else None

            # Add the question
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 8, f"{i}. {question}")

            # Add options
            pdf.set_font("Arial", "", 12)
            for idx, opt in enumerate(options, 1):
                pdf.multi_cell(0, 6, f"({idx}) {opt}")

            # Add answer if available
            if answer and include_answers:
                pdf.set_font("Arial", "B", 12)
                pdf.set_text_color(0, 100, 0)  # Dark green for answers
                pdf.multi_cell(0, 8, f"Answer: Option {answer}")
                pdf.set_text_color(0, 0, 0)  # Reset to black

            pdf.ln(4)  # Space between questions

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            tmp_file_path = tmp_file.name

        return tmp_file_path

    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def create_answer_key_pdf(questions, subject):
    """Create a separate answer key PDF"""
    try:
        class CustomPDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, f'KCET {subject} Answer Key', 0, 1, 'C')
                self.ln(4)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = CustomPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Create a table for answer key
        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 10, "Question No.", 1, 0, 'C')
        pdf.cell(0, 10, "Correct Answer (Option)", 1, 1, 'C')

        pdf.set_font("Arial", "", 12)
        for i, item in enumerate(questions, 1):
            answer = item[2] if len(item) > 2 else "N/A"
            pdf.cell(30, 8, f"{i}", 1, 0, 'C')
            pdf.cell(0, 8, f"{answer}", 1, 1, 'C')

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            tmp_file_path = tmp_file.name

        return tmp_file_path

    except Exception as e:
        st.error(f"Error creating answer key PDF: {str(e)}")
        return None
