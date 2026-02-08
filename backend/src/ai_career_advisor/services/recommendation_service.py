"""
Career Recommendation Service
Implements hybrid recommendation engine with content-based and collaborative filtering
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any, Optional, Tuple
from ai_career_advisor.models.user_preferences import UserPreferences
from ai_career_advisor.models.career_attributes import CareerAttributes
from ai_career_advisor.models.user_career_interaction import UserCareerInteraction, INTERACTION_SCORES
from ai_career_advisor.core.logger import logger
import math


class RecommendationService:
    """
    Hybrid Career Recommendation Engine
    
    Algorithms:
    1. Content-Based: Jaccard similarity between user profile and career attributes
    2. Collaborative: User-user similarity based on career interactions
    3. Hybrid: Weighted combination of both
    """
    
    # Weights for hybrid scoring
    CONTENT_WEIGHT = 0.6  # For new users or sparse data
    COLLABORATIVE_WEIGHT = 0.4  # When user history exists
    
    # Minimum interactions needed for collaborative filtering
    MIN_INTERACTIONS_FOR_COLLAB = 3
    
    # ================== CORE RECOMMENDATION API ==================
    
    @staticmethod
    async def get_recommendations(
        db: AsyncSession,
        user_email: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get top-K career recommendations for a user using Semantic Search.
        """
        logger.info(f"🎯 Generating semantic recommendations for: {user_email}")
        
        # Step 1: Get user preferences
        user_prefs = await RecommendationService._get_user_preferences(db, user_email)
        
        if not user_prefs:
            logger.warning(f"No preferences found for {user_email}, using popularity-based fallback")
            return await RecommendationService._get_popular_careers(db, top_k)
        
        # Phase 4 Upgrade: Generate User Embedding Vector
        logger.info("🧠 Generating User Semantic Vector...")
        user_profile_text = (
            f"Skills: {', '.join(user_prefs.skills or [])}. "
            f"Interests: {', '.join(user_prefs.interests or [])}. "
            f"Personality: {', '.join(user_prefs.personality_traits or [])}. "
            f"Education: {user_prefs.education_level or 'Not specified'}."
        )
        
        try:
            from ai_career_advisor.core.model_manager import ModelManager
            user_vector = await ModelManager.get_embedding(user_profile_text)
        except Exception as e:
            logger.error(f"❌ Could not generate user embedding: {e}")
            user_vector = None

        # Step 2: Get all careers
        careers = await RecommendationService._get_all_careers(db)
        
        if not careers:
            logger.error("No careers in database!")
            return []
        
        # Step 3: Interaction Check
        interaction_count = await RecommendationService._get_user_interaction_count(db, user_email)
        use_collaborative = interaction_count >= RecommendationService.MIN_INTERACTIONS_FOR_COLLAB
        
        # Step 4: Calculate scores
        scored_careers = []
        for career in careers:
            # Phase 4: Semantic Content Score
            if user_vector and career.semantic_vector:
                # Use Cosine Similarity (Semantic)
                content_score = RecommendationService._cosine_similarity(user_vector, career.semantic_vector)
                # Boost by basic Jaccard for literal matches
                literal_boost = RecommendationService._calculate_content_score(user_prefs, career)
                content_score = (content_score * 0.7) + (literal_boost * 0.3)
            else:
                # Fallback to pure keyword matching
                content_score = RecommendationService._calculate_content_score(user_prefs, career)
            
            if use_collaborative:
                collab_score = await RecommendationService._calculate_collaborative_score(
                    db, user_email, career.career_name
                )
                final_score = (
                    RecommendationService.CONTENT_WEIGHT * content_score +
                    RecommendationService.COLLABORATIVE_WEIGHT * collab_score
                )
            else:
                final_score = content_score
            
            scored_careers.append({
                "career": career.to_dict(),
                "match_score": round(final_score * 100, 1),
                "content_score": round(content_score * 100, 1),
                "recommendation_type": "semantic_hybrid" if user_vector else "keyword_match"
            })
        
        # Step 5: Sort
        scored_careers.sort(key=lambda x: x["match_score"], reverse=True)
        
        logger.success(f"✅ Generated {len(scored_careers[:top_k])} recommendations")
        return scored_careers[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    # ================== CONTENT-BASED FILTERING ==================
    
    @staticmethod
    def _calculate_content_score(user_prefs: UserPreferences, career: CareerAttributes) -> float:
        """
        Calculate content-based similarity score using weighted Jaccard similarity.
        
        Components:
        - Skill match (50%): How many user skills match career requirements
        - Interest match (30%): How many user interests match career tags
        - Education match (15%): Does user meet education requirements
        - Work style match (5%): Does work style preference match
        """
        scores = []
        weights = []
        
        # 1. Skill match (50% weight)
        skill_similarity = RecommendationService._jaccard_similarity(
            user_prefs.skills or [],
            career.required_skills or []
        )
        scores.append(skill_similarity)
        weights.append(0.50)
        
        # 2. Interest match (30% weight)
        interest_similarity = RecommendationService._jaccard_similarity(
            user_prefs.interests or [],
            career.interest_tags or []
        )
        scores.append(interest_similarity)
        weights.append(0.30)
        
        # 3. Education match (15% weight)
        education_score = RecommendationService._calculate_education_match(
            user_prefs.education_level,
            career.min_education
        )
        scores.append(education_score)
        weights.append(0.15)
        
        # 4. Work style match (5% weight)
        work_style_score = 1.0 if (
            not career.work_style or
            not user_prefs.preferred_work_style or
            career.work_style == user_prefs.preferred_work_style
        ) else 0.5
        scores.append(work_style_score)
        weights.append(0.05)
        
        # Weighted average
        final_score = sum(s * w for s, w in zip(scores, weights))
        
        return min(1.0, max(0.0, final_score))
    
    @staticmethod
    def _jaccard_similarity(set_a: List[str], set_b: List[str]) -> float:
        """
        Calculate Jaccard similarity between two sets.
        
        J(A,B) = |A ∩ B| / |A ∪ B|
        
        Returns value between 0 and 1.
        """
        if not set_a or not set_b:
            return 0.0
        
        # Normalize to lowercase for matching
        set_a_normalized = set(s.lower().strip() for s in set_a)
        set_b_normalized = set(s.lower().strip() for s in set_b)
        
        intersection = len(set_a_normalized & set_b_normalized)
        union = len(set_a_normalized | set_b_normalized)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    @staticmethod
    def _calculate_education_match(user_education: Optional[str], career_min: Optional[str]) -> float:
        """
        Calculate education compatibility score.
        
        Returns:
        - 1.0: User meets or exceeds requirement
        - 0.7: User is close (one level below)
        - 0.3: User needs significant upgrade
        """
        if not career_min or not user_education:
            return 1.0  # No requirement or no data = assume compatible
        
        # Education levels in ascending order
        EDUCATION_LEVELS = {
            "10th": 1, "12th": 2, 
            "graduate": 3, "diploma": 3, "btech": 3, "bca": 3,
            "postgraduate": 4, "mtech": 4, "mba": 4, "mca": 4,
            "phd": 5
        }
        
        user_level = EDUCATION_LEVELS.get(user_education.lower(), 2)
        career_level = EDUCATION_LEVELS.get(career_min.lower(), 2)
        
        if user_level >= career_level:
            return 1.0
        elif user_level == career_level - 1:
            return 0.7  # Close enough
        else:
            return 0.3  # Significant gap
    
    # ================== COLLABORATIVE FILTERING ==================
    
    @staticmethod
    async def _calculate_collaborative_score(
        db: AsyncSession,
        user_email: str,
        career_name: str
    ) -> float:
        """
        Calculate collaborative filtering score.
        
        Based on: "Users similar to you liked this career"
        
        Steps:
        1. Find users who interacted with similar careers
        2. Check if those users interacted with target career
        3. Weight by similarity and interaction score
        """
        try:
            # Get current user's career interactions
            user_interactions = await RecommendationService._get_user_interactions(db, user_email)
            user_careers = {i.career_name for i in user_interactions}
            
            if not user_careers:
                return 0.5  # Neutral score if no history
            
            # Find other users who interacted with same careers
            similar_users = await db.execute(
                select(UserCareerInteraction.user_email)
                .where(UserCareerInteraction.career_name.in_(user_careers))
                .where(UserCareerInteraction.user_email != user_email)
                .distinct()
            )
            similar_user_emails = [row[0] for row in similar_users.fetchall()]
            
            if not similar_user_emails:
                return 0.5  # No similar users found
            
            # Check how many similar users interacted with target career
            positive_interactions = await db.execute(
                select(func.avg(UserCareerInteraction.score))
                .where(UserCareerInteraction.user_email.in_(similar_user_emails))
                .where(UserCareerInteraction.career_name == career_name)
            )
            avg_score = positive_interactions.scalar() or 0.5
            
            return min(1.0, max(0.0, avg_score))
            
        except Exception as e:
            logger.error(f"Collaborative scoring error: {e}")
            return 0.5  # Neutral on error
    
    # ================== DATABASE HELPERS ==================
    
    @staticmethod
    async def _get_user_preferences(db: AsyncSession, user_email: str) -> Optional[UserPreferences]:
        """Get user preferences from database"""
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_email == user_email)
        )
        return result.scalars().first()
    
    @staticmethod
    async def _get_all_careers(db: AsyncSession) -> List[CareerAttributes]:
        """Get all career attributes from database"""
        result = await db.execute(select(CareerAttributes))
        return result.scalars().all()
    
    @staticmethod
    async def _get_user_interactions(db: AsyncSession, user_email: str) -> List[UserCareerInteraction]:
        """Get all user career interactions"""
        result = await db.execute(
            select(UserCareerInteraction)
            .where(UserCareerInteraction.user_email == user_email)
        )
        return result.scalars().all()
    
    @staticmethod
    async def _get_user_interaction_count(db: AsyncSession, user_email: str) -> int:
        """Count user's career interactions"""
        result = await db.execute(
            select(func.count(UserCareerInteraction.id))
            .where(UserCareerInteraction.user_email == user_email)
        )
        return result.scalar() or 0
    
    @staticmethod
    async def _get_popular_careers(db: AsyncSession, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback: Return most popular careers for cold-start users.
        """
        result = await db.execute(
            select(CareerAttributes)
            .order_by(CareerAttributes.popularity_score.desc())
            .limit(top_k)
        )
        careers = result.scalars().all()
        
        return [
            {
                "career": c.to_dict(),
                "match_score": round(c.popularity_score * 100, 1),
                "recommendation_type": "popularity"
            }
            for c in careers
        ]
    
    # ================== USER PREFERENCE MANAGEMENT ==================
    
    @staticmethod
    async def save_user_preferences(
        db: AsyncSession,
        user_email: str,
        preferences: Dict[str, Any]
    ) -> UserPreferences:
        """
        Save or update user preferences from quiz.
        """
        # Check if exists
        existing = await RecommendationService._get_user_preferences(db, user_email)
        
        if existing:
            # Update existing
            for key, value in preferences.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.quiz_completed = True
            existing.quiz_completion_percentage = 100
        else:
            # Create new
            existing = UserPreferences(
                user_email=user_email,
                quiz_completed=True,
                quiz_completion_percentage=100,
                **preferences
            )
            db.add(existing)
        
        await db.commit()
        await db.refresh(existing)
        
        logger.info(f"✅ Saved preferences for {user_email}")
        return existing
    
    # ================== INTERACTION TRACKING ==================
    
    @staticmethod
    async def track_interaction(
        db: AsyncSession,
        user_email: str,
        career_name: str,
        interaction_type: str,
        source: str = "recommendation",
        session_id: str = None
    ) -> UserCareerInteraction:
        """
        Track a user-career interaction for collaborative filtering.
        """
        score = INTERACTION_SCORES.get(interaction_type, 0.5)
        
        interaction = UserCareerInteraction(
            user_email=user_email,
            career_name=career_name,
            interaction_type=interaction_type,
            score=score,
            source=source,
            session_id=session_id
        )
        
        db.add(interaction)
        await db.commit()
        await db.refresh(interaction)
        
        logger.info(f"📊 Tracked interaction: {user_email} -> {career_name} ({interaction_type})")
        return interaction
    
    # ================== SIMILAR CAREERS ==================
    
    @staticmethod
    async def get_similar_careers(
        db: AsyncSession,
        career_name: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get careers similar to a given career.
        Uses content similarity between career attributes.
        """
        # Get target career
        result = await db.execute(
            select(CareerAttributes).where(CareerAttributes.career_name == career_name)
        )
        target_career = result.scalars().first()
        
        if not target_career:
            return []
        
        # Get all other careers
        result = await db.execute(
            select(CareerAttributes).where(CareerAttributes.career_name != career_name)
        )
        other_careers = result.scalars().all()
        
        # Calculate similarity for each
        similarities = []
        target_vector = target_career.get_attribute_vector()
        
        for career in other_careers:
            similarity = RecommendationService._jaccard_similarity(
                target_vector,
                career.get_attribute_vector()
            )
            similarities.append({
                "career": career.to_dict(),
                "similarity_score": round(similarity * 100, 1)
            })
        
        # Sort and return top-K
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similarities[:top_k]
