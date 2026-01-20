import json
import google.generativeai as genai
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.logger import logger
import asyncio
from functools import partial
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError


genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")


class BackwardPlannerLLM:
    """
    Generates complete backward career roadmap using Gemini AI
    """
    
    @staticmethod
    def _validate_roadmap(data: dict) -> tuple[bool, list]:
        """
        Validates roadmap with MANDATORY and OPTIONAL fields
        
        MANDATORY: Must be present
        OPTIONAL: Nice to have, can be skipped
        
        Returns:
            (is_complete, missing_fields)
        """
        
        mandatory_fields = [
            "career_name",
            "career_description",
            "required_education",
            "entrance_exams"
        ]
        

        optional_fields = [
            "stream_recommendation",
            "skills_required",
            "timeline",
            "projects_to_build",
            "certifications",
            "internships",
            "top_colleges",
            "career_prospects"
        ]
        
        missing = []
        
        
        for field in mandatory_fields:
            if field not in data or not data[field]:
                missing.append(field)
        
        if missing:
            return (False, missing)
        
        return (True, [])
    
    @staticmethod
    async def generate_roadmap(
        *,
        career_name: str,
        category: str
    ) -> dict:
        """
        Generates complete backward roadmap for a career
        
        Args:
            career_name: Normalized career name (e.g., "Software Engineer")
            category: Career category (e.g., "Technology")
        
        Returns:
            Complete roadmap dict or error dict
        """
        
        logger.info(f"🤖 Generating roadmap for '{career_name}' ({category})")
        
        MAX_RETRIES = 3
        base_delay = 5
        
        for attempt in range(1, MAX_RETRIES + 1):
            
            if attempt == 1:
                logger.info(f"   📊 [Attempt {attempt}/{MAX_RETRIES}] Generating roadmap...")
            else:
                logger.warning(f"   🔄 [Attempt {attempt}/{MAX_RETRIES}] Retrying due to incomplete data...")
            
            
            if attempt == 1:
                flexibility = "STRICT: Only include information you are 100% certain about."
            elif attempt == 2:
                flexibility = "MODERATE: Include reasonable estimates and common career paths."
            else:
                flexibility = "RELAXED: Provide best available guidance even if some details are approximate."
            
            prompt = f"""
You are an expert Indian career counselor creating a COMPLETE backward roadmap.

CAREER: {career_name}
CATEGORY: {category}

{flexibility}

Generate a detailed REVERSE roadmap from this career back to Class 10 level.
Focus on the Indian education system (CBSE/State boards, IITs, NITs, NEET, JEE, etc.)

RETURN STRICT JSON ONLY (no markdown, no comments, no extra text):

{{
  "career_name": "{career_name}",
  "career_description": "2-3 sentences describing this career and what professionals do",
  
  "required_education": {{
    "degree_options": ["BTech Computer Science", "BCA", "BSc Computer Science"],
    "minimum_degree": "Bachelor's degree",
    "preferred_degree": "BTech/BE in Computer Science",
    "specialization": "Computer Science/IT/Software Engineering"
  }},
  
  "entrance_exams": [
    {{
      "exam_name": "JEE Main",
      "for": "BTech admission in NITs/IIITs/GFTIs",
      "difficulty": "High",
      "when_to_prepare": "Class 11-12"
    }},
    {{
      "exam_name": "JEE Advanced",
      "for": "BTech admission in IITs",
      "difficulty": "Very High",
      "when_to_prepare": "Class 11-12"
    }}
  ],
  
  "stream_recommendation": {{
    "class_11_12": "Science with PCM (Physics, Chemistry, Mathematics)",
    "reason": "Mathematics and logical thinking are essential for engineering entrance exams",
    "alternatives": ["Science with PCM + Computer Science (optional 5th subject)"]
  }},
  
  "skills_required": [
    {{
      "skill": "Programming",
      "level": "Expert",
      "languages": ["Python", "Java", "C++", "JavaScript"]
    }},
    {{
      "skill": "Data Structures and Algorithms",
      "level": "Expert"
    }},
    {{
      "skill": "Problem Solving",
      "level": "Expert"
    }},
    {{
      "skill": "Web Development",
      "level": "Intermediate to Advanced"
    }}
  ],
  
  "projects_to_build": [
    "Personal Portfolio Website",
    "E-commerce Web Application",
    "Machine Learning Project (Image Classification/NLP)",
    "Mobile App (Android/iOS)",
    "Open Source Contributions on GitHub"
  ],
  
  "internships": [
    {{
      "type": "Software Development Intern",
      "when": "After Year 2 of degree",
      "duration": "2-3 months (summer break)"
    }},
    {{
      "type": "Full Stack Developer Intern",
      "when": "After Year 3 of degree",
      "duration": "6 months"
    }}
  ],
  
  "certifications": [
    "AWS Certified Developer - Associate",
    "Google Cloud Professional",
    "Full Stack Web Development (Coursera/Udemy)",
    "Competitive Programming (CodeChef/Codeforces ratings)"
  ],
  
  "top_colleges": [
    {{
      "name": "IIT Bombay",
      "nirf_rank": 3,
      "type": "Government"
    }},
    {{
      "name": "IIT Delhi",
      "nirf_rank": 1,
      "type": "Government"
    }},
    {{
      "name": "NIT Trichy",
      "nirf_rank": 10,
      "type": "Government"
    }},
    {{
      "name": "BITS Pilani",
      "nirf_rank": 25,
      "type": "Private"
    }}
  ],
  
  "career_prospects": {{
    "average_salary": "₹6-12 LPA for freshers",
    "experienced_salary": "₹20-50 LPA with 5+ years experience",
    "growth_rate": "High - Tech industry growing rapidly",
    "job_availability": "Excellent - High demand in IT sector"
  }},
  
  "timeline": {{
    "class_10": "Focus on Mathematics and Science. Start basic coding (Scratch/Python basics).",
    "class_11_12": "Take Science with PCM. Prepare seriously for JEE/CUET. Learn programming fundamentals (C++/Python). Build 1-2 small projects.",
    "year_1_2": "Core CS subjects (DSA, DBMS, OS). Master one programming language. Build 2-3 projects. Participate in hackathons.",
    "year_3_4": "Advanced topics (ML, Cloud, Web Dev). Do 2 internships. Build strong GitHub profile. Prepare for placements. Complete 5+ projects.",
    "total_duration": "4 years Bachelor's degree + continuous learning throughout career"
  }}
}}

IMPORTANT RULES:
- Be specific and actionable for Indian students
- Include realistic Indian salary ranges (in LPA)
- Mention Indian colleges (IITs, NITs, AIIMS, etc.)
- Mention Indian entrance exams (JEE, NEET, CUET, CAT, etc.)
- Provide year-wise timeline from Class 10 onwards
- All fields must be filled with meaningful data
- Return ONLY valid JSON, no extra text
"""
            
            try:
                # Rate limit delay
                await asyncio.sleep(base_delay)
                
                # Call Gemini
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        partial(model.generate_content, prompt)
                    ),
                    timeout=120.0  # 2 minutes for complex generation
                )
                
                text = response.text.strip()
                
                # Clean markdown
                if text.startswith("```"):
                    text = text.replace("```json", "").replace("```", "").strip()
                
                # Parse JSON
                try:
                    roadmap = json.loads(text)
                except json.JSONDecodeError as e:
                    logger.error(f"   🔴 JSON parse error: {str(e)[:100]}")
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(base_delay * attempt)
                        continue
                    else:
                        logger.error(f"   ❌ Failed to generate valid JSON after {MAX_RETRIES} attempts")
                        return {
                            "error": "invalid_json_after_retries",
                            "message": "Could not generate valid roadmap structure"
                        }
                
            
                is_complete, missing = BackwardPlannerLLM._validate_roadmap(roadmap)
                
                if is_complete:
                    logger.success(f"   ✅ Mandatory fields present for '{career_name}'")
                    
                    
                    
                    if "stream_recommendation" not in roadmap or not roadmap["stream_recommendation"]:
                        logger.warning(f"   ⚠️ stream_recommendation missing, adding default")
                        roadmap["stream_recommendation"] = {
                            "class_11_12": "Consult career counselor based on specific requirements",
                            "reason": "Stream depends on entrance exam requirements for this career",
                            "alternatives": []
                        }
                    
                    if "skills_required" not in roadmap or not roadmap["skills_required"]:
                        logger.warning(f"   ⚠️ skills_required missing, adding default")
                        roadmap["skills_required"] = [
                            {"skill": "Core domain knowledge", "level": "Expert"},
                            {"skill": "Communication and teamwork", "level": "Intermediate"}
                        ]
                    
                    if "timeline" not in roadmap or not roadmap["timeline"]:
                        logger.warning(f"   ⚠️ timeline missing, adding default")
                        roadmap["timeline"] = {
                            "class_10": "Focus on foundational subjects and explore career interests",
                            "class_11_12": f"Prepare for entrance exams required for {career_name}",
                            "year_1_2": "Build foundational knowledge in the chosen field",
                            "year_3_4": "Gain practical experience through internships and projects",
                            "total_duration": "Typically 4+ years of formal education"
                        }
                    
                    if "projects_to_build" not in roadmap or not roadmap["projects_to_build"]:
                        roadmap["projects_to_build"] = []
                    
                    if "certifications" not in roadmap or not roadmap["certifications"]:
                        roadmap["certifications"] = []
                    
                    if "internships" not in roadmap or not roadmap["internships"]:
                        roadmap["internships"] = []
                    
                    if "top_colleges" not in roadmap or not roadmap["top_colleges"]:
                        roadmap["top_colleges"] = []
                    
                    if "career_prospects" not in roadmap or not roadmap["career_prospects"]:
                        roadmap["career_prospects"] = {
                            "average_salary": "Varies by industry and experience",
                            "growth_rate": "Moderate to High",
                            "job_availability": "Moderate"
                        }
                    
                    logger.success(f"   ✅ Complete roadmap ready for '{career_name}'")
                    return roadmap
                    
                else:
                    logger.warning(f"   ⚠️ INCOMPLETE: Missing mandatory fields → {missing}")
                    
                    if attempt < MAX_RETRIES:
                        retry_delay = base_delay * (attempt + 1)
                        logger.info(f"   ⏳ Waiting {retry_delay}s before retry...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"   ❌ Incomplete roadmap after {MAX_RETRIES} attempts")
                        logger.error(f"   ❌ Missing mandatory fields: {missing}")
                        return {
                            "error": "incomplete_roadmap_after_retries",
                            "message": f"Could not generate complete roadmap. Missing mandatory: {missing}"
                        }
            
            except asyncio.TimeoutError:
                logger.error(f"   ⏱️ Timeout (attempt {attempt})")
                if attempt < MAX_RETRIES:
                    continue
                else:
                    logger.error(f"   ❌ Timeout after {MAX_RETRIES} attempts")
                    return {
                        "error": "timeout_exceeded",
                        "message": "Roadmap generation took too long. Please try again."
                    }
            
            except ResourceExhausted:
                logger.warning(f"   🟡 Rate limit hit (attempt {attempt})")
                await asyncio.sleep(60)
                if attempt < MAX_RETRIES:
                    continue
                else:
                    logger.error(f"   ❌ Quota exhausted")
                    return {
                        "error": "quota_exhausted",
                        "message": "API quota exhausted. Please try again later."
                    }
            
            except GoogleAPIError as e:
                logger.error(f"   🔴 API Error: {str(e)}")
                return {
                    "error": "api_error",
                    "message": f"API error: {str(e)}"
                }
            
            except Exception as e:
                logger.error(f"   🔴 Unexpected error: {str(e)}")
                return {
                    "error": "unexpected_error",
                    "message": f"Unexpected error: {str(e)}"
                }
        
        # Fallback
        logger.error(f"   ❌ All retries exhausted for '{career_name}'")
        return {
            "error": "all_retries_failed",
            "message": "Could not generate roadmap after multiple attempts"
        }
