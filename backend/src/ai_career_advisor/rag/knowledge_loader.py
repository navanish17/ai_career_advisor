from sqlalchemy import select
from ai_career_advisor.core.database import get_db
from ai_career_advisor.models.college import College
from ai_career_advisor.models.career_template import CareerTemplate
from ai_career_advisor.models.entrance_exam import EntranceExam
from ai_career_advisor.models.backward_roadmap import BackwardRoadmap
from ai_career_advisor.models.college_details import CollegeDetails
from ai_career_advisor.models.roadmap import Roadmap
from ai_career_advisor.models.roadmap_step import RoadmapStep
from ai_career_advisor.models.career import Career
from ai_career_advisor.models.branch import Branch
from ai_career_advisor.models.degree import Degree
from ai_career_advisor.models.career_insight import CareerInsight
from ai_career_advisor.core.logger import logger
from typing import List, Dict, Any

class KnowledgeLoader:
    """Loads ALL knowledge from database for RAG indexing"""
    
    @staticmethod
    async def load_colleges() -> List[Dict[str, Any]]:
        """Load college basic info"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(select(College))
                colleges = result.scalars().all()
                
                for college in colleges:
                    content_parts = [f"{college.name}"]
                    
                    if hasattr(college, 'state') and college.state:
                        content_parts.append(f"located in {college.state}")
                    if hasattr(college, 'nirf_rank') and college.nirf_rank:
                        content_parts.append(f"NIRF Rank: {college.nirf_rank}")
                    if hasattr(college, 'type') and college.type:
                        content_parts.append(f"Type: {college.type}")
                    
                    doc = {
                        "id": f"college_{college.id}",
                        "content": ". ".join(content_parts) + ".",
                        "metadata": {
                            "source": "college",
                            "type": "basic_info",
                            "college_id": college.id,
                            "college_name": college.name
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} college documents")
                break
            except Exception as e:
                logger.error(f"Error loading colleges: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_college_details() -> List[Dict[str, Any]]:
        """Load detailed college info"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(select(CollegeDetails))
                details = result.scalars().all()
                
                for detail in details:
                    # Get college name
                    college_result = await db.execute(
                        select(College).where(College.id == detail.college_id)
                    )
                    college = college_result.scalar_one_or_none()
                    
                    if college:
                        content_parts = [f"{college.name}"]
                        
                        if hasattr(detail, 'degree') and detail.degree:
                            content_parts.append(f"{detail.degree}")
                        if hasattr(detail, 'branch') and detail.branch:
                            content_parts.append(f"{detail.branch}")
                        
                        details_parts = []
                        if hasattr(detail, 'fees_value') and detail.fees_value:
                            details_parts.append(f"Fees: {detail.fees_value}")
                        if hasattr(detail, 'avg_package_value') and detail.avg_package_value:
                            details_parts.append(f"Average package: {detail.avg_package_value}")
                        if hasattr(detail, 'highest_package_value') and detail.highest_package_value:
                            details_parts.append(f"Highest package: {detail.highest_package_value}")
                        if hasattr(detail, 'entrance_exam_value') and detail.entrance_exam_value:
                            details_parts.append(f"Entrance exam: {detail.entrance_exam_value}")
                        if hasattr(detail, 'cutoff_value') and detail.cutoff_value:
                            details_parts.append(f"Cutoff: {detail.cutoff_value}")
                        
                        content = " ".join(content_parts) + ": " + ", ".join(details_parts)
                        
                        doc = {
                            "id": f"college_detail_{detail.id}",
                            "content": content,
                            "metadata": {
                                "source": "college_detail",
                                "type": "detailed_info",
                                "college_id": detail.college_id,
                                "college_name": college.name
                            }
                        }
                        documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} college detail documents")
                break
            except Exception as e:
                logger.error(f"Error loading college details: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_careers() -> List[Dict[str, Any]]:
        """Load career information"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(select(Career))
                careers = result.scalars().all()
                
                for career in careers:
                    # Dynamically build content based on available attributes
                    content = f"{getattr(career, 'career_name', getattr(career, 'careername', 'Career'))} career"
                    
                    doc = {
                        "id": f"career_{career.id}",
                        "content": content,
                        "metadata": {
                            "source": "career",
                            "type": "career_info",
                            "career_id": career.id
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} career documents")
                break
            except Exception as e:
                logger.error(f"Error loading careers: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_career_templates() -> List[Dict[str, Any]]:
        """Load pre-built career templates"""
        documents = []
        
        async for db in get_db():
            try:
                # Try without is_active filter first
                result = await db.execute(select(CareerTemplate))
                templates = result.scalars().all()
                
                for template in templates:
                    career_name = getattr(template, 'career_name', getattr(template, 'careername', 'Career'))
                    description = getattr(template, 'career_description', getattr(template, 'careerdescription', ''))
                    
                    content = f"{career_name} career: {description or 'Career guidance available.'}"
                    
                    doc = {
                        "id": f"career_template_{template.id}",
                        "content": content,
                        "metadata": {
                            "source": "career_template",
                            "type": "career_overview",
                            "career_name": career_name
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} career template documents")
                break
            except Exception as e:
                logger.error(f"Error loading career templates: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_career_insights() -> List[Dict[str, Any]]:
        """Load career insights"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(select(CareerInsight))
                insights = result.scalars().all()
                
                for insight in insights:
                    content = "Career insight available"
                    
                    doc = {
                        "id": f"career_insight_{insight.id}",
                        "content": content,
                        "metadata": {
                            "source": "career_insight",
                            "type": "top_1_percent"
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} career insight documents")
                break
            except Exception as e:
                logger.error(f"Error loading career insights: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_branches() -> List[Dict[str, Any]]:
        """Load branch information"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(select(Branch))
                branches = result.scalars().all()
                
                for branch in branches:
                    branch_name = getattr(branch, 'branch_name', getattr(branch, 'branchname', 'Branch'))
                    content = f"{branch_name} branch"
                    
                    doc = {
                        "id": f"branch_{branch.id}",
                        "content": content,
                        "metadata": {
                            "source": "branch",
                            "type": "branch_info",
                            "branch_name": branch_name
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} branch documents")
                break
            except Exception as e:
                logger.error(f"Error loading branches: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_degrees() -> List[Dict[str, Any]]:
        """Load degree information"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(select(Degree))
                degrees = result.scalars().all()
                
                for degree in degrees:
                    degree_name = getattr(degree, 'degree_name', getattr(degree, 'degreename', 'Degree'))
                    content = f"{degree_name} degree"
                    
                    doc = {
                        "id": f"degree_{degree.id}",
                        "content": content,
                        "metadata": {
                            "source": "degree",
                            "type": "degree_info",
                            "degree_name": degree_name
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} degree documents")
                break
            except Exception as e:
                logger.error(f"Error loading degrees: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_entrance_exams() -> List[Dict[str, Any]]:
        """Load entrance exam information"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(select(EntranceExam))
                exams = result.scalars().all()
                
                for exam in exams:
                    exam_name = getattr(exam, 'exam_name', getattr(exam, 'examname', 'Exam'))
                    content = f"{exam_name} entrance exam"
                    
                    doc = {
                        "id": f"exam_{exam.id}",
                        "content": content,
                        "metadata": {
                            "source": "entrance_exam",
                            "type": "exam_info",
                            "exam_name": exam_name
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} entrance exam documents")
                break
            except Exception as e:
                logger.error(f"Error loading entrance exams: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_backward_roadmaps() -> List[Dict[str, Any]]:
        """Load backward career roadmaps"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(select(BackwardRoadmap))
                roadmaps = result.scalars().all()
                
                for roadmap in roadmaps:
                    career_name = getattr(roadmap, 'normalized_career', getattr(roadmap, 'career_goal_input', 'Career'))
                    content = f"{career_name} career roadmap"
                    
                    doc = {
                        "id": f"backward_roadmap_{roadmap.id}",
                        "content": content,
                        "metadata": {
                            "source": "backward_roadmap",
                            "type": "career_roadmap"
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} backward roadmap documents")
                break
            except Exception as e:
                logger.error(f"Error loading backward roadmaps: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_guided_roadmaps() -> List[Dict[str, Any]]:
        """Load guided roadmaps"""
        documents = []
        
        async for db in get_db():
            try:
                result = await db.execute(
                    select(Roadmap).where(Roadmap.roadmap_type == "guided")
                )
                roadmaps = result.scalars().all()
                
                for roadmap in roadmaps:
                    content = f"Roadmap for {roadmap.class_level} student"
                    
                    doc = {
                        "id": f"guided_roadmap_{roadmap.id}",
                        "content": content,
                        "metadata": {
                            "source": "guided_roadmap",
                            "type": "step_by_step",
                            "class_level": roadmap.class_level
                        }
                    }
                    documents.append(doc)
                
                logger.info(f"Loaded {len(documents)} guided roadmap documents")
                break
            except Exception as e:
                logger.error(f"Error loading guided roadmaps: {str(e)}")
        
        return documents
    
    @staticmethod
    async def load_all() -> List[Dict[str, Any]]:
        """Load ALL knowledge base documents"""
        logger.info("=" * 60)
        logger.info("Loading complete knowledge base...")
        logger.info("=" * 60)
        
        all_docs = []
        
        # Load each category
        logger.info("\n📚 Loading colleges...")
        colleges = await KnowledgeLoader.load_colleges()
        all_docs.extend(colleges)
        
        logger.info("📚 Loading college details...")
        college_details = await KnowledgeLoader.load_college_details()
        all_docs.extend(college_details)
        
        logger.info("📚 Loading careers...")
        careers = await KnowledgeLoader.load_careers()
        all_docs.extend(careers)
        
        logger.info("📚 Loading career templates...")
        templates = await KnowledgeLoader.load_career_templates()
        all_docs.extend(templates)
        
        logger.info("📚 Loading career insights...")
        insights = await KnowledgeLoader.load_career_insights()
        all_docs.extend(insights)
        
        logger.info("📚 Loading branches...")
        branches = await KnowledgeLoader.load_branches()
        all_docs.extend(branches)
        
        logger.info("📚 Loading degrees...")
        degrees = await KnowledgeLoader.load_degrees()
        all_docs.extend(degrees)
        
        logger.info("📚 Loading entrance exams...")
        exams = await KnowledgeLoader.load_entrance_exams()
        all_docs.extend(exams)
        
        logger.info("📚 Loading backward roadmaps...")
        backward = await KnowledgeLoader.load_backward_roadmaps()
        all_docs.extend(backward)
        
        logger.info("📚 Loading guided roadmaps...")
        guided = await KnowledgeLoader.load_guided_roadmaps()
        all_docs.extend(guided)
        
        logger.info("=" * 60)
        logger.success(f"✅ Total documents loaded: {len(all_docs)}")
        logger.info("=" * 60)
        
        return all_docs
