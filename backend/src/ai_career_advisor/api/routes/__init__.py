from .auth import router as auth
from .agent import router as agent
from .career import router as career
from .colleges import router as colleges
from .profile import router as profile
from .quiz import router as quiz
from .roadmap import router as roadmap
from .scholarships import router as scholarships
from .degree import router as degree_router
from .branch import router as branch
from .career_insight import router as career_insight
from .colleges import router as college_router
from .backward_planner import router as backward_planner_router





__all__ = [
    "auth",
    "agent",
    "career",
    "colleges",
    "profile",
    "quiz",
    "roadmap",
    "scholarships",
    "degree_router",
    "branch",
    "career_insight",
    "college_router",
    "backward_planner_router",
]
