# question_utils.py
import os
import re
import random
from datetime import datetime
import tempfile

def parse_markdown_files(folder):
    """Parse Markdown files in the selected subject folder"""
    questions = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    questions.extend(parse_uploaded_questions(content))
    return questions

def parse_uploaded_questions(file_content):
    """Parse uploaded question file content"""
    questions = []
    lines = file_content.strip().split('\n')

    i = 0
    while i < len(lines):
        # Skip empty lines
        if not lines[i].strip():
            i += 1
            continue

        # Check for question pattern (e.g., "1. Question text" or just "Question text")
        question_text = lines[i].strip()
        # Remove any numbering at the beginning
        question_text = re.sub(r'^\d+[\.\)]\s*', '', question_text)

        options = []
        i += 1

        # Collect options until we hit an empty line or another question
        while i < len(lines) and lines[i].strip() and not re.match(r'^\d+[\.\)]', lines[i]):
            option_match = re.search(r'(\(|^)[1-4a-d](\)|\.|:)?\s*(.+)', lines[i].strip(), re.IGNORECASE)
            if option_match:
                options.append(option_match.group(3).strip())
            i += 1

        # If we found a question and at least some options, add it
        if question_text and len(options) > 0:
            # If we don't have 4 options, fill in with placeholders
            while len(options) < 4:
                options.append(f"Option {len(options)+1}")

            questions.append((question_text, options))

    return questions

def generate_new_questions(question, options, subject, chapter, api_caller):
    """Generate new KCET-style questions based on existing ones"""
    option_text = "\n".join([f"({i+1}) {opt}" for i, opt in enumerate(options)])

    chapter_text = "" if chapter == "all" else f" focused on the {chapter} chapter"

    prompt = f"""Generate a new KCET-style {subject} question{chapter_text} similar to the following:

{question}
{option_text}

Provide the new question along with four options. Format exactly like:
<question>
(1) <option 1>
(2) <option 2>
(3) <option 3>
(4) <option 4>"""

    return api_caller(prompt, temperature=0.7)

def parse_generated_question(response):
    """Parse the generated question response"""
    if not response:
        return None, None

    # Try different regex patterns to handle various response formats
    patterns = [
        r"(.+?)[\n\r][\s]*\(1\)[\s]*(.+?)[\n\r][\s]*\(2\)[\s]*(.+?)[\n\r][\s]*\(3\)[\s]*(.+?)[\n\r][\s]*\(4\)[\s]*(.+)",
        r"(.+?)[\n\r][\s]*1\.[\s]*(.+?)[\n\r][\s]*2\.[\s]*(.+?)[\n\r][\s]*3\.[\s]*(.+?)[\n\r][\s]*4\.[\s]*(.+)",
        r"<question>\s*(.+?)[\n\r][\s]*\(1\)[\s]*(.+?)[\n\r][\s]*\(2\)[\s]*(.+?)[\n\r][\s]*\(3\)[\s]*(.+?)[\n\r][\s]*\(4\)[\s]*(.+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL)
        if match:
            question = match.group(1).strip()
            options = [match.group(i).strip() for i in range(2, 6)]
            return question, options

    # If no pattern matches, try to extract manually
    lines = response.strip().split('\n')
    if len(lines) >= 5:
        question = lines[0].replace("<question>", "").strip()
        options = []
        for line in lines[1:]:
            option_match = re.search(r'(\(|^)[1-4](\)|\.|:)?\s*(.+)', line)
            if option_match and len(options) < 4:
                options.append(option_match.group(3).strip())

        if len(options) == 4:
            return question, options

    return None, None

def predict_answer(question, options, api_caller):
    """Predict answers for the generated questions"""
    option_text = "\n".join([f"({i+1}) {opt}" for i, opt in enumerate(options)])
    prompt = f"""KCET-style Question:

{question}
{option_text}

Which option is correct? Reply with the option number (1, 2, 3, or 4) only."""

    response = api_caller(prompt, temperature=0)
    if not response:
        return "Error"

    # Extract just the number from the response
    number_match = re.search(r'[1-4]', response)
    if number_match:
        return number_match.group(0)
    return response

def save_questions_to_markdown(questions, subject_folder):
    """Save new questions to a Markdown file"""
    # Use temp directory for file operations
    temp_dir = tempfile.gettempdir()
    output_file = os.path.join(temp_dir, f"new_{subject_folder}_questions_{datetime.now().strftime('%Y%m%d%H%M%S')}.md")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, (question, options) in enumerate(questions, 1):
                f.write(f"{i}. {question}\n")
                for idx, opt in enumerate(options, 1):
                    f.write(f"({idx}) {opt}\n")
                f.write("\n")
        return output_file
    except Exception as e:
        print(f"Error saving markdown file: {str(e)}")
        return None

def predict_next_year_questions(questions, subject, api_caller):
    """Predict next year's questions based on current questions"""
    next_year_questions = []
    
    for question, options in questions:
        # Format options for prompt
        options_text = "\n".join([f"({i+1}) {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""Based on the following KCET-style {subject} question, predict a similar question that might be asked next year:

{question}
{options_text}

Provide the new question along with four options. Format exactly like:
<question>
(1) <option 1>
(2) <option 2>
(3) <option 3>
(4) <option 4>"""

        response = api_caller(prompt, temperature=0.7)
        new_question, new_options = parse_generated_question(response)

        if new_question and new_options:
            next_year_questions.append((new_question, new_options))
            
    return next_year_questions

def generate_questions_batch(source_questions, num_questions, subject, chapter, api_caller):
    """Generate a batch of new questions based on source questions"""
    new_questions = []
    
    for i in range(num_questions):
        # Pick a random question from source questions as inspiration
        idx = random.randint(0, len(source_questions)-1)
        question, options = source_questions[idx]

        # Generate a new question based on it
        response = generate_new_questions(question, options, subject, chapter, api_caller)
        new_question, new_options = parse_generated_question(response)

        if new_question and new_options:
            new_questions.append((new_question, new_options))
            
    return new_questions