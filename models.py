from sqlalchemy import Column, String, Integer
from database import Base

class RecruitQualification(Base):
    __tablename__ = "recruit_qualifications"

    job_category = Column(String, primary_key=True)
    company_name = Column(String, primary_key=True)
    detail_job = Column(String, primary_key=True)

    company_type = Column(String)
    location = Column(String)
    education_level = Column(String)
    major = Column(String)
    main_job = Column(String)
    experience_years = Column(Integer)
    language_requirement = Column(String)
    military_requirement = Column(String)
    overseas_available = Column(String)
    etc_requirements = Column(String)
    process = Column(String)
