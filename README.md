# KCET INTELLIGEN
Here is a well-structured **README.md** file based on your project description. It’s formatted in Markdown and suitable for GitHub or documentation purposes.

---

# KCET IntelliGen: AI-Powered KCET Question Analysis and Generation

**KCET IntelliGen** is an intelligent, modular system designed to automate the parsing, analysis, and generation of KCET-style multiple-choice questions using Generative AI. It leverages OpenAI’s GPT-3.5 Turbo API and the LlamaIndex framework to process historical question papers and produce high-quality, syllabus-aligned practice content.

---

## 🔧 Tech Stack

* **Programming Language:** Python 3.11+
* **AI Model:** OpenAI GPT-3.5 Turbo (fine-tuned using supervised learning)
* **Frameworks & Libraries:**

  * `openai` – Model API and fine-tuning
  * `llama-index` – PDF parsing and content structuring
  * `pandas`, `re`, `json` – Data formatting and processing
  * `fpdf` – PDF generation
  * `streamlit` – Web interface for question generation and prediction
* **Development Environment:** Visual Studio Code, Google Colab, OpenAI platform
* **Data Formats:** Markdown (human-readable content), JSONL (fine-tuning data)

---

## 🧠 Key Features

* **Automated PDF Parsing:** Extracts and cleans KCET question papers (2004–2024) into structured Markdown using LlamaIndex.
* **Question Dataset Creation:** Transforms questions into prompt-completion pairs for fine-tuning language models.
* **Custom Model Fine-Tuning:** Uses OpenAI's `fine_tune.create` endpoint with \~1,200 training samples and 200 test prompts.
* **AI-Based Question Generation:** Produces subject-specific, syllabus-aligned questions with answer prediction.
* **Interactive Streamlit App:** Enables real-time generation, prediction, and export of custom KCET question sets in PDF format.

---

## 🔁 Pipeline Workflow

### **1. PDF Parsing (LlamaIndex)**

* Extracts text from KCET papers
* Organizes content by subject: Physics, Chemistry, Mathematics, Biology
* Preserves original formatting for accuracy

### **2. Dataset Formatting**

* Creates JSONL prompt-completion pairs like:

  ```json
  {
    "prompt": "Generate a Biology question similar to the 2020 KCET paper on human digestion.",
    "completion": "Which enzyme is responsible for protein digestion in the stomach? A) Amylase B) Lipase C) Pepsin D) Trypsin"
  }
  ```

### **3. Fine-Tuning**

* Model trained using OpenAI API with key configurations:

  * Temperature: 0.7
  * Max Tokens: 150
  * Dataset Size: 1,200 training / 200 testing pairs

### **4. Question Generation**

* Generates syllabus-aligned MCQs using zero-shot/few-shot prompting
* Outputs question + answer, e.g.:

  ```
  Q: A coil is moved through a magnetic field. Which law explains the electric current generation?
  A) Faraday’s Law of Induction
  B) Newton’s Law
  C) Ampere’s Law
  D) Lenz’s Law
  → Answer: A
  ```

---

## 🖥️ Streamlit App Modules

* **Question Parsing:** Extracts questions from Markdown using regex-based cleaning
* **Question Generation:** Randomly selects prompts and produces new questions via OpenAI API
* **Answer Prediction:** Predicts answers for generated questions
* **PDF Export:** Converts generated questions and answers into clean, printable PDFs with customized headers/footers

---

## 📂 Folder Structure

```
kcet-intelligen/
├── data/
│   └── markdown/           # Parsed question sets
├── app/
│   ├── parse.py            # Markdown parsing scripts
│   ├── generate.py         # Question generation logic
│   ├── predict.py          # Answer prediction logic
│   └── pdf_creator.py      # PDF generation
├── fine_tuning/
│   ├── train.jsonl         # Fine-tuning dataset
│   └── test.jsonl
├── streamlit_app.py        # UI entry point
└── README.md
```

---

## 🚀 How to Run

### Requirements

```bash
pip install openai llama-index streamlit pandas fpdf
```

### Run the Streamlit App

```bash
streamlit run streamlit_app.py
```

---

## 📈 Future Enhancements

* Add multilingual support (Kannada & English)
* Integrate analytics for student performance tracking
* Expand to other competitive exams (NEET, JEE, etc.)
* Improve difficulty-level estimation using Bloom’s taxonomy

---

## 🤖 Authors and Contributors

* **Lead Developer:** \Samarth Uday, Suhas M
* **Model Integration:** \Sourav Mantesh Shet
* **Content & Syllabus Mapping:** \T Sai Shravan

