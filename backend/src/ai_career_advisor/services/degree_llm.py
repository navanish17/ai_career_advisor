import google.generativeai as genai
from ai_career_advisor.core.config import settings


# Configure Gemini once
genai.configure(api_key=settings.GEMINI_API_KEY)


PROMPT_TEMPLATE = """
You are a Degree Description Generator.
Generate EXACTLY 2 simple lines about the degree {degree_name}.
Line 1: What this degree is, written in simple academic language.
Line 2: Include all domains or specialisations if it has.
Rules:
- No careers, salary, colleges, exams.
- No bullets, no numbering.
- No extra lines.
- Use formal but simple tone.
- Similar depth and style as a university prospectus.
Return only plain text.
""".strip()


def generate_degree_description(degree_name: str) -> str:
    """
    Generates a 2-line academic description for a degree using Gemini.
    Returns plain text only.
    """

    if not degree_name:
        raise ValueError("Degree name is required")

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = PROMPT_TEMPLATE.format(degree_name=degree_name)

    response = model.generate_content(prompt)

    if not response or not response.text:
        raise RuntimeError("Empty response from Gemini API")

    # Clean output (safety)
    text = response.text.strip()

    # Ensure max 2 lines only
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:4])
