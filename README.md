# 📄 Resume Review Assistant

An AI-powered **Resume Review Assistant** built with **Streamlit** and an **OpenRouter-compatible LLM**. The application analyzes PDF or TXT resumes against a target job role or job description, evaluates ATS compatibility, identifies missing keywords, reviews formatting and grammar, and generates an optimized professional summary with actionable improvement suggestions.

---

## ✨ Features

- 📄 Upload resumes in **PDF** or **TXT** format
- 🎯 Analyze resumes against a target job role
- 📋 Upload or paste a Job Description (JD) for ATS comparison
- 📊 ATS compatibility scoring
- 🔍 Missing technical keyword detection
- ✍️ Resume formatting and grammar analysis
- 📝 AI-generated professional summary
- 💼 Achievement-oriented bullet point suggestions
- 💬 AI-powered follow-up resume coaching
- ⚡ Powered by OpenRouter-compatible Large Language Models
- 🎨 Clean and responsive Streamlit interface

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **OpenRouter API**
- **Large Language Models (LLMs)**
- **PyPDF**
- **python-dotenv**

---

## 📂 Project Structure

```text
.
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
├── .env.example
├── README.md
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/resume-review-assistant.git
cd resume-review-assistant
```

Create and activate a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_openrouter_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1/chat/completions
LLM_MODEL=your_model_name
```

> **Note:** If no API key is configured, the application will still provide rule-based resume analysis and ATS feedback.

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The application will automatically open in your default browser.

## 🎯 How It Works

1. Upload your resume in **PDF** or **TXT** format.
2. Enter your target job role.
3. Optionally upload or paste a Job Description.
4. The application extracts resume content.
5. It analyzes:
   - ATS compatibility
   - Formatting
   - Grammar
   - Missing keywords
   - Resume strengths and weaknesses
6. Receive:
   - ATS score
   - Improvement suggestions
   - Professional summary
   - Achievement-oriented bullet points
7. Chat with the AI for personalized resume optimization.

---

## 🌟 Future Enhancements

- 📈 Resume comparison against multiple JDs
- 📊 ATS score visualization
- 📄 Resume PDF export
- 🎯 Skill gap analysis
- 🌐 LinkedIn profile optimization
- 📧 Cover letter generation
- 🤖 Interview preparation based on resume
- 📱 Mobile-friendly interface

---

## ⚠️ Disclaimer

The ATS score and recommendations are generated using heuristic analysis and AI assistance. Results may vary depending on the applicant tracking system used by individual employers and should be considered as guidance rather than an official ATS evaluation.

---

⭐ If you found this project useful, consider giving it a **Star** on GitHub!

---
