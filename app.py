import os
import re
from io import BytesIO
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILES = [os.path.join(BASE_DIR, ".env"), os.path.join(BASE_DIR, ".env.example")]
for env_file in ENV_FILES:
    if os.path.exists(env_file):
        load_dotenv(env_file, override=False)

st.set_page_config(page_title="Resume Review Assistant", page_icon="📄", layout="wide")

COMMON_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "machine learning",
    "ai",
    "data analysis",
    "excel",
    "powerbi",
    "tableau",
    "pytest",
    "fastapi",
    "flask",
    "django",
    "microservices",
    "api",
    "rest",
    "graphql",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "spark",
    "hadoop",
    "cloud",
    "cybersecurity",
    "devops",
    "testing",
    "automation",
    "jira",
    "stripe",
    "sql server",
    "c#",
    "c++",
    "linux",
    "gitlab",
    "github",
    "jira",
    "selenium",
    "jenkins",
    "terraform",
    "ansible",
    "helm",
    "docker-compose",
    "ci/cd",
}

TECH_PHRASES = {
    "machine learning",
    "deep learning",
    "data analysis",
    "data engineering",
    "natural language processing",
    "cloud computing",
    "rest api",
    "graphql api",
    "continuous integration",
    "continuous deployment",
    "unit testing",
    "integration testing",
    "performance testing",
    "automation testing",
    "containerization",
    "infrastructure as code",
    "distributed systems",
    "serverless",
    "frontend",
    "backend",
    "full stack",
    "full-stack",
}

TECH_HINTS = {
    "api",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "sql",
    "react",
    "node",
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "stripe",
    "graphql",
    "mongodb",
    "postgresql",
    "mysql",
    "spark",
    "hadoop",
    "tensorflow",
    "pytorch",
    "flask",
    "django",
    "fastapi",
    "pytest",
    "rest",
    "cloud",
    "devops",
    "microservices",
    "ci/cd",
    "terraform",
    "ansible",
    "helm",
    "docker-compose",
    "selenium",
    "jira",
    "powerbi",
    "tableau",
}


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    chunks = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        if extracted:
            chunks.append(extracted)
    return "\n".join(chunks)


def extract_text_from_upload(uploaded_file) -> str:
    filename = (uploaded_file.name or "").lower()
    file_bytes = uploaded_file.getvalue()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    return file_bytes.decode("utf-8", errors="ignore")


def tokenize(text: str):
    return re.findall(r"[a-zA-Z0-9+#.]+", text.lower())


def extract_keywords(job_role: str):
    words = [w for w in tokenize(job_role) if len(w) > 2]
    focused = []
    for word in words:
        if word in COMMON_SKILLS or word.isdigit():
            focused.append(word)
        elif len(word) > 4:
            focused.append(word)
    return sorted(set(focused))[:12]


def normalize_skill_token(token: str) -> str:
    token = token.lower().strip()
    aliases = {
        "js": "javascript",
        "py": "python",
        "nodejs": "node",
        "reactjs": "react",
        "awscloud": "aws",
        "azurecloud": "azure",
        "gcp": "google cloud",
        "css3": "css",
        "html5": "html",
        "dockercompose": "docker-compose",
        "k8s": "kubernetes",
        "ci/cd": "ci/cd",
        "restapi": "rest api",
        "graphqlapi": "graphql api",
    }
    return aliases.get(token, token)


def contains_exact_keyword(text: str, keyword: str) -> bool:
    return bool(re.search(rf"\b{re.escape(keyword)}\b", text))


def is_technical_token(token: str) -> bool:
    if token in COMMON_SKILLS or token in TECH_PHRASES or token in TECH_HINTS:
        return True
    for hint in TECH_HINTS:
        if token == hint:
            return True
        if token.startswith(hint) or token.endswith(hint):
            if len(token) <= len(hint) + 8:
                return True
    return False


def extract_keywords_from_jd(job_role: str, jd_text: str) -> list[str]:
    text = f"{job_role or ''} {jd_text or ''}".lower()
    normalized = re.sub(r"[\r\n]+", " ", text)
    raw_tokens = re.findall(r"[a-zA-Z0-9+#./-]+", normalized)
    tokens = [normalize_skill_token(t.strip('.,:;()[]')) for t in raw_tokens if len(t.strip('.,:;()[]')) > 2]

    NON_TECH_WORDS = {
        "and", "the", "with", "for", "that", "this", "from", "have", "has", "will", "be",
        "using", "including", "able", "work", "team", "role", "roles", "skills", "skill", "experience",
        "experiences", "responsibilities", "requirements", "requirement", "job", "jobs", "title", "entry",
        "level", "location", "hybrid", "remote", "onsite", "fulltime", "parttime", "years", "year", "yrs",
        "candidate", "candidates", "apply", "salary", "interview", "internship", "intern", "company", "companies",
        "clients", "client", "projects", "project", "manager", "managers", "lead", "leads", "business",
        "analysis", "analyst", "team", "teams", "office", "workplace", "training", "education", "degree",
        "bengaluru", "bangalore", "hyderabad", "mumbai", "delhi", "chennai", "pune", "noida", "gurgaon",
        "must", "should", "good", "strong", "excellent", "easy", "comfortable", "understanding",
    }
    tokens = [t for t in tokens if t not in NON_TECH_WORDS and not t.isdigit()]

    freq: dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1

    keywords: list[str] = []
    seen: set[str] = set()

    for phrase in TECH_PHRASES:
        if contains_exact_keyword(normalized, phrase) and phrase not in seen:
            keywords.append(phrase)
            seen.add(phrase)

    for skill in COMMON_SKILLS:
        if contains_exact_keyword(normalized, skill) and skill not in seen:
            keywords.append(skill)
            seen.add(skill)

    for token, _ in sorted(freq.items(), key=lambda item: (-item[1], item[0])):
        if token in seen or token in NON_TECH_WORDS:
            continue
        if token in COMMON_SKILLS or token in TECH_PHRASES:
            keywords.append(token)
            seen.add(token)
            continue
        if is_technical_token(token):
            keywords.append(token)
            seen.add(token)
        if len(keywords) >= 30:
            break

    return keywords[:30]


def score_formatting(text: str) -> dict[str, Any]:
    total_words = len(tokenize(text))
    has_contact = bool(re.search(r"\b(?:phone|email|linkedin|github)\b", text.lower()))
    has_summary = bool(re.search(r"\b(summary|professional summary|about)\b", text.lower()))
    has_skills = bool(re.search(r"\b(skills|technical skills|core skills)\b", text.lower()))
    has_experience = bool(re.search(r"\b(experience|work experience|employment)\b", text.lower()))
    has_education = bool(re.search(r"\b(education|academics|degree)\b", text.lower()))
    bullet_count = len(re.findall(r"^\s*[-•*]\s", text, flags=re.MULTILINE))

    score = 0
    score += 25 if has_contact else 0
    score += 15 if has_summary else 0
    score += 15 if has_skills else 0
    score += 20 if has_experience else 0
    score += 15 if has_education else 0
    score += 10 if bullet_count >= 3 else 0
    score = min(score, 100)

    suggestions = []
    if not has_summary:
        suggestions.append("Add a concise professional summary near the top of the resume.")
    if not has_skills:
        suggestions.append("Create a dedicated skills section with role-relevant tools and technologies.")
    if not has_experience:
        suggestions.append("Add clear work experience entries with measurable results.")
    if total_words < 180:
        suggestions.append("Expand the resume with more quantified achievements and details.")

    return {
        "score": score,
        "summary": "Structure is generally solid" if score >= 70 else "Structure needs improvement",
        "suggestions": suggestions,
    }


def score_grammar(text: str) -> dict[str, Any]:
    text_clean = normalize_text(text)
    issues = []
    if re.search(r"\bteh\b", text_clean.lower()):
        issues.append("Typo detected: 'teh'.")
    if re.search(r"\s{2,}", text_clean):
        issues.append("Double spaces or inconsistent spacing detected.")
    if re.search(r"[,;:]\s{2,}", text_clean):
        issues.append("Punctuation spacing looks inconsistent.")
    words = re.findall(r"\b[a-zA-Z]+\b", text_clean.lower())
    if any(words[i] == words[i - 1] for i in range(1, len(words))):
        issues.append("Possible repeated word detected.")

    score = max(60, 100 - len(issues) * 15)
    return {
        "score": score,
        "summary": "Writing quality looks strong" if score >= 80 else "Polish the wording and consistency",
        "issues": issues,
    }


def calculate_ats_score(resume_text: str, job_role: str, jd_text: str | None = None) -> dict[str, Any]:
    keywords = extract_keywords_from_jd(job_role or "", jd_text or "")
    normalized_resume = normalize_text(resume_text.lower())

    matched = [kw for kw in keywords if contains_exact_keyword(normalized_resume, kw)]
    keyword_coverage = round((len(matched) / max(1, len(keywords))) * 100, 1) if keywords else 0.0

    resume_tokens = set(tokenize(normalized_resume))
    matched_tokens = [k for k in keywords if all(tok in resume_tokens for tok in k.split())]
    keyword_density = round((len(matched_tokens) / max(1, len(keywords))) * 100, 1) if keywords else 0.0

    score = 30
    if re.search(r"\b(summary|skills|experience|education)\b", normalized_resume):
        score += 15
    if len(re.findall(r"\b[a-z]{3,}\b", normalized_resume)) > 200:
        score += 10
    score += min(40, int(keyword_coverage * 0.4))
    score = min(100, score)

    summary = "Strong keyword alignment" if score >= 75 else "Increase role-specific keywords and phrasing"
    return {
        "score": score,
        "matched_keywords": matched,
        "keyword_density": keyword_density,
        "keyword_coverage": keyword_coverage,
        "summary": summary,
    }


def generate_summary(resume_text: str, job_role: str) -> str:
    if not resume_text.strip():
        return f"Results-driven professional with strong experience in {job_role or 'technology'} and a focus on impact, growth, and execution."
    return f"Results-driven professional with experience in {job_role or 'technology'}, known for delivering measurable outcomes, collaborating effectively, and building strong technical foundations."


def generate_bullets(resume_text: str, job_role: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", resume_text)
    bullets = []
    for sentence in sentences[:8]:
        cleaned = sentence.strip()
        if 20 <= len(cleaned) <= 140:
            bullet = cleaned.replace("•", "").replace("-", "").strip()
            if bullet and bullet[0].islower():
                bullet = bullet[0].upper() + bullet[1:]
            bullets.append(f"- {bullet}")
    if not bullets:
        bullets.append(f"- Delivered measurable impact aligned to {job_role or 'the target role'}.")
        bullets.append("- Improved efficiency, quality, and collaboration across teams and projects.")
    return bullets[:6]


def build_analysis(resume_text: str, job_role: str, jd_text: str | None = None) -> dict[str, Any]:
    formatting = score_formatting(resume_text)
    grammar = score_grammar(resume_text)
    ats = calculate_ats_score(resume_text, job_role, jd_text)
    keywords = extract_keywords_from_jd(job_role or "", jd_text or "")
    normalized_resume = normalize_text(resume_text.lower())

    skills = sorted([s for s in COMMON_SKILLS if contains_exact_keyword(normalized_resume, s)])[:10]
    missing_skills = [k for k in keywords if not contains_exact_keyword(normalized_resume, k)]
    matched_keywords = [k for k in keywords if contains_exact_keyword(normalized_resume, k)]

    suggestions = list(formatting["suggestions"])
    if missing_skills:
        if matched_keywords:
            suggestions.append(
                "Your resume includes "
                + ", ".join(matched_keywords[:5])
                + ", but it still misses these JD terms: "
                + ", ".join(missing_skills[:6])
                + "."
            )
        else:
            suggestions.append(
                "Your resume does not yet mention the JD's required tools and platforms. Add the missing technical skills exactly as they appear in the job description."
            )
        suggestions.append(
            "Place missing keywords in a dedicated skills section and reflect them in specific experience bullets."
        )
        if len(missing_skills) > 5:
            suggestions.append(
                "Start with the highest-priority missing skills, then add the rest with one concrete achievement bullet each."
            )
    elif keywords:
        suggestions.append(
            "Your resume already includes the main technical keywords from the JD. Strengthen it by making each bullet show the technology, the task, and the outcome."
        )

    if jd_text and jd_text.strip():
        if ats["keyword_coverage"] < 70:
            suggestions.append(
                "Keyword coverage is low for this JD. Focus on the exact technologies and platforms the job description names rather than generic words."
            )
            if job_role:
                suggestions.append(
                    f"Match the JD to the target role '{job_role}' by using phrases such as {', '.join(keywords[:5])} where appropriate."
                )
        else:
            suggestions.append(
                "Keyword alignment is good. Improve by tying those keywords to real achievements, metrics, and business value."
            )
    else:
        suggestions.append(
            "If you do not have a JD, use the target role to guide keyword selection and keep the list purely technical."
        )

    if not re.search(r"\b(skills|technical skills|core skills)\b", normalized_resume):
        suggestions.append(
            "Add a dedicated technical skills section listing languages, frameworks, systems, and tools used on the target role."
        )
    else:
        suggestions.append(
            "Ensure the skills section only contains technical items and not soft skills, roles, or generic phrases."
        )

    if not re.search(r"\b(summary|professional summary|about)\b", normalized_resume):
        suggestions.append(
            "Add a concise technical summary at the top that highlights your most relevant tools, platforms, and achievements."
        )
    else:
        suggestions.append(
            "Refine your summary to mention the most relevant technical strengths and top achievements that match the JD."
        )

    if missing_skills:
        suggestions.append(
            "For each missing keyword, include one bullet that shows context: what you built, the technology used, and the result or impact."
        )
    else:
        suggestions.append(
            "Strengthen existing bullets with specific metrics such as performance improvements, delivery times, or adoption rates."
        )

    if any(contains_exact_keyword(normalized_resume, term) for term in ["internship", "intern"]):
        suggestions.append(
            "Keep the keyword list focused on technical skills; remove or de-emphasize non-technical internship and company terms from the skill mapping."
        )

    suggestions.append(
        "Use numbers, percentages, and business outcomes to describe your contributions and technical impact."
    )

    # Deduplicate suggestions while preserving order
    final_suggestions: list[str] = []
    for suggestion in suggestions:
        if suggestion not in final_suggestions:
            final_suggestions.append(suggestion)

    return {
        "ats": ats,
        "formatting": formatting,
        "grammar": grammar,
        "keywords": keywords,
        "skills": skills,
        "missing_skills": missing_skills[:12],
        "suggestions": final_suggestions[:10],
        "professional_summary": generate_summary(resume_text, job_role),
        "achievement_bullets": generate_bullets(resume_text, job_role),
    }


def llm_reply(message: str, job_role: str, resume_text: str, analysis: dict[str, Any] | None) -> str:
    api_key = (
        os.getenv("OPENROUTER_API_KEY")
        or os.getenv("LLM_API_KEY")
        or st.session_state.get("llm_api_key", "")
    ).strip()
    if not api_key:
        return (
            "LLM API key is not configured yet. I can still help with heuristic guidance. "
            f"Your resume appears to target {job_role or 'the role'}; the strongest next step is to add role-specific keywords and quantify achievements."
        )

    base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
    model = os.getenv("LLM_MODEL", "poolside/laguna-m.1:free")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful resume review assistant. Answer concisely and professionally."},
            {"role": "user", "content": f"User question: {message}\n\nJob role: {job_role}\n\nResume excerpt:\n{resume_text[:6000]}\n\nCurrent analysis summary:\n{analysis}"},
        ],
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Resume Review Assistant",
    }
    try:
        response = requests.post(base_url, json=payload, headers=headers, timeout=45)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return "The LLM request could not be completed. The app will continue with built-in guidance."


if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "job_role" not in st.session_state:
    st.session_state.job_role = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("📄 Resume Review Assistant")
st.caption("Analyze resumes for formatting, grammar, ATS readiness, and targeted improvements.")

uploaded_file = st.file_uploader("Upload a resume (PDF or TXT)", type=["pdf", "txt"], key="resume_file")
job_role = st.text_input("Target job role", placeholder="Software Engineer, Data Analyst...", key="job_role")
jd_file = st.file_uploader("Upload a Job Description (JD) (PDF or TXT, optional)", type=["pdf", "txt"], key="jd_file")
jd_paste = st.text_area("Or paste JD text (optional)", height=120, key="jd_paste")

analyze_clicked = st.button("Analyze Resume", use_container_width=True)

if analyze_clicked and uploaded_file is not None and job_role.strip():
    with st.spinner("Reviewing your resume..."):
        resume_text = extract_text_from_upload(uploaded_file)
        # obtain JD text from uploaded file or pasted text
        jd_text = ""
        if jd_file is not None:
            try:
                jd_text = extract_text_from_upload(jd_file)
            except Exception:
                jd_text = jd_paste or ""
        else:
            jd_text = jd_paste or ""

        analysis = build_analysis(resume_text, job_role, jd_text)
        st.session_state.analysis = analysis
        st.session_state.resume_text = resume_text[:10000]
        # do not overwrite st.session_state.job_role because it is tied to the widget
        st.session_state.current_job_role = job_role
        st.session_state.jd_text = jd_text
        st.session_state.jd_text = jd_text

if st.session_state.analysis:
    analysis = st.session_state.analysis
    col1, col2, col3 = st.columns(3)
    col1.metric("ATS score", f"{analysis['ats']['score']}/100")
    col2.metric("Formatting", f"{analysis['formatting']['score']}/100")
    col3.metric("Grammar", f"{analysis['grammar']['score']}/100")

    st.subheader("Suggested improvements")
    st.write("\n".join(f"- {item}" for item in analysis["suggestions"]))

    st.subheader("Professional summary")
    st.write(analysis["professional_summary"])

    st.subheader("Achievement-oriented bullets")
    st.write("\n".join(analysis["achievement_bullets"]))

    st.subheader("Missing keywords")
    if analysis["missing_skills"]:
        st.write(", ".join(analysis["missing_skills"]))
    else:
        st.success("No obvious missing keywords detected.")

    st.subheader("Ask follow-up questions")
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(message)

    prompt = st.chat_input("Ask: How can I improve my summary?")
    if prompt:
        st.session_state.chat_history.append(("user", prompt))
        with st.chat_message("user"):
            st.write(prompt)
        job_for_chat = st.session_state.get('current_job_role', st.session_state.get('job_role', ''))
        reply = llm_reply(prompt, job_for_chat, st.session_state.resume_text, st.session_state.analysis)
        st.session_state.chat_history.append(("assistant", reply))
        with st.chat_message("assistant"):
            st.write(reply)
else:
    st.info("Upload a resume and provide a target role to start the review.")
