import io
import json
import logging
import re
from typing import Any
import httpx
import pdfplumber
from pydantic import BaseModel, Field

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ProjectItem(BaseModel):
    title: str = Field(default="Untitled Project")
    description: str = Field(default="")
    technologies: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    degree: str = Field(default="")
    institution: str = Field(default="")
    year: str | int | None = Field(default=None)


class ParsedResumeData(BaseModel):
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts raw text from PDF bytes using pdfplumber."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def strip_pii(text: str) -> str:
    """
    Strips Personally Identifiable Information (PII) like emails, phone numbers,
    and URLs before forwarding to an LLM.
    """
    # Strip emails
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED_EMAIL]", text)
    # Strip phone numbers (various formats)
    text = re.sub(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "[REDACTED_PHONE]", text)
    # Strip github/linkedin profile links (to protect identity)
    text = re.sub(r"https?://(www\.)?(linkedin|github)\.com/[^\s]+", "[REDACTED_PROFILE]", text)
    return text


def rule_based_fallback_parse(text: str) -> ParsedResumeData:
    """
    Fallback deterministic parser extracting common skills and sections
    when LLM is unreachable or times out.
    """
    known_skills = [
        "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "SQL", "HTML", "CSS",
        "React", "Node.js", "Express", "FastAPI", "Django", "Flask", "Spring Boot",
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes", "AWS",
        "Git", "GitHub", "Linux", "Data Structures", "Algorithms", "Machine Learning",
        "Deep Learning", "TensorFlow", "PyTorch", "OOP", "DBMS", "Operating Systems",
        "Computer Networks", "REST API", "GraphQL"
    ]
    found_skills = set()
    for skill in known_skills:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.add(skill)

    projects = []
    project_match = re.search(r"(?:projects?|academic projects?)\s*[:\n]([\s\S]*?)(?:education|skills|experience|$)", text, re.IGNORECASE)
    if project_match:
        project_snippet = project_match.group(1).strip()
        lines = [line.strip("- •* ") for line in project_snippet.split("\n") if len(line.strip()) > 5]
        for line in lines[:4]:
            projects.append(ProjectItem(title=line[:50], description=line, technologies=[]))

    education = []
    edu_match = re.search(r"(?:education|academics?)\s*[:\n]([\s\S]*?)(?:projects?|skills|experience|$)", text, re.IGNORECASE)
    if edu_match:
        edu_lines = [line.strip("- •* ") for line in edu_match.group(1).split("\n") if len(line.strip()) > 5]
        for line in edu_lines[:2]:
            education.append(EducationItem(degree=line[:60], institution="University / College"))

    return ParsedResumeData(
        skills=sorted(list(found_skills)),
        projects=projects,
        education=education,
    )


async def parse_resume_with_llm(sanitized_text: str) -> ParsedResumeData:
    """
    Sends sanitized resume text to local Ollama Qwen2.5-3B model requesting structured JSON.
    """
    system_prompt = (
        "You are an expert technical resume parser. Extract structured information from the candidate resume. "
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "skills": ["string"],\n'
        '  "projects": [{"title": "string", "description": "string", "technologies": ["string"]}],\n'
        '  "education": [{"degree": "string", "institution": "string", "year": "string"}]\n'
        "}\n"
        "Do not include any explanation or markdown formatting outside the JSON."
    )

    prompt = f"Resume Content:\n{sanitized_text[:4000]}\n\nParse into the required JSON schema:"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False,
                    "format": "json",
                },
            )
            if resp.status_code == 200:
                raw_json = resp.json().get("response", "")
                data = json.loads(raw_json)
                return ParsedResumeData(**data)
            else:
                logger.warning(f"Ollama returned status {resp.status_code}. Using fallback.")
    except Exception as e:
        logger.warning(f"Ollama extraction failed: {e}. Falling back to rule-based parser.")

    return rule_based_fallback_parse(sanitized_text)
