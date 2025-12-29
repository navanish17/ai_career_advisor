from sqlalchemy import Column, Integer, String, ForeignKey, JSON, UniqueConstraint
from ai_career_advisor.core.database import Base


class CollegeDetails(Base):
    __tablename__ = "college_details"

    id = Column(Integer, primary_key=True, index=True)

    college_id = Column(
        Integer,
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    degree = Column(String(100), nullable=False)
    branch = Column(String(100), nullable=False)

    # -------- Fees --------
    fees_value = Column(String(100), nullable=True)
    fees_source = Column(String(500), nullable=True)
    fees_extracted_text = Column(String(1000), nullable=True)

    # -------- Placement (Average) --------
    avg_package_value = Column(String(100), nullable=True)
    avg_package_source = Column(String(500), nullable=True)
    avg_package_extracted_text = Column(String(1000), nullable=True)

    # -------- Placement (Highest) --------
    highest_package_value = Column(String(100), nullable=True)
    highest_package_source = Column(String(500), nullable=True)
    highest_package_extracted_text = Column(String(1000), nullable=True)

    # -------- Entrance Exam --------
    entrance_exam_value = Column(String(100), nullable=True)
    entrance_exam_source = Column(String(500), nullable=True)
    entrance_exam_extracted_text = Column(String(1000), nullable=True)

    # -------- Cutoff --------
    cutoff_value = Column(String(200), nullable=True)
    cutoff_source = Column(String(500), nullable=True)
    cutoff_extracted_text = Column(String(1000), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "college_id",
            "degree",
            "branch",
            name="uq_college_degree_branch"
        ),
    )
