from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import RecruitQualification, Applicant
import schemas

app = FastAPI(title="Spectrackr API", description="채용정보를 위한 FastAPI", version="1.0")

# ✅ Decorator Pattern: 로그 출력용 데코레이터 정의
def log_endpoint(func):
    def wrapper(*args, **kwargs):
        print(f"📨 호출됨: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# ✅ Factory Method Pattern: DB 세션 팩토리 함수
def db_session_factory():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Adapter Pattern: row 데이터를 dict로 변환
def adapt_company_row(row):
    return {"company": row[0]} if row and row[0] else {}

def adapt_detail_job_row(row):
    return {"detail_job": row[0]} if row and row[0] else {}

def adapt_company_and_job_row(row):
    return {"company": row[0], "detail_job": row[1]} if row else {}

# ✅ Facade Pattern: 복잡한 비즈니스 로직을 내부 함수로 위임
def get_job_posting_facade(db, req):
    result = db.query(
        RecruitQualification.location,
        RecruitQualification.education_level,
        RecruitQualification.experience,
        RecruitQualification.image,
        RecruitQualification.etc_requirements,
        RecruitQualification.preferred_qualification
    ).filter(
        RecruitQualification.job_category == req.job_category,
        RecruitQualification.company_name == req.company_name,
        RecruitQualification.detail_job == req.detail_job
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="해당 조건에 맞는 채용 정보가 없습니다.")

    location, education_level, experience, image, etc_requirements, preferred_qualification = result

    base_data = {
        "location": location,
        "education_level": education_level,
        "experience": experience,
    }

    if image:
        base_data["image"] = image
    else:
        base_data["etc_requirements"] = etc_requirements
        base_data["preferred_qualification"] = preferred_qualification

    return [base_data]

# ✅ 엔드포인트들
@app.get("/")
@log_endpoint
def root():
    return {"message": "Spectrackr API is live!"}

@app.post("/get-company-name-and-detail-job")
@log_endpoint
def get_company_name_and_detail_job(req: schemas.JobCategoryRequest, db: Session = Depends(db_session_factory)):
    results = (
        db.query(RecruitQualification.company_name, RecruitQualification.detail_job)
          .filter(RecruitQualification.job_category == req.job_category)
          .all()
    )
    return results

@app.post("/get-detail-job-by-company-name")
@log_endpoint
def get_detail_job_by_company_name(req: schemas.CompanyNameRequest, db: Session = Depends(db_session_factory)):
    results = (
        db.query(RecruitQualification.detail_job)
          .filter(RecruitQualification.company_name == req.company_name)
          .all()
    )
    return results

@app.post("/get-company-name-by-detail-job")
@log_endpoint
def get_company_name_by_detail_job(req: schemas.DetailJobRequest, db: Session = Depends(db_session_factory)):
    results = (
        db.query(RecruitQualification.company_name)
          .filter(RecruitQualification.detail_job == req.detail_job)
          .all()
    )
    return results

@app.post("/get-job-posting")
@log_endpoint
def get_job_posting(req: schemas.JobPostingRequest, db: Session = Depends(db_session_factory)):
    return get_job_posting_facade(db, req)

@app.post("/get-applicants-by-company-detail-job")
@log_endpoint
def get_applicants_by_company_detail_job(req: schemas.ApplicantSearchByCompanyDetailJobRequest, db: Session = Depends(db_session_factory)):
    results = (
        db.query(Applicant)
          .filter(Applicant.company == req.company, Applicant.detail_job == req.detail_job)
          .all()
    )
    return results

@app.post("/get-companiy-by-detail-job")
@log_endpoint
def get_companies_by_detail_job(req: schemas.DetailJobOnlyRequest, db: Session = Depends(db_session_factory)):
    results = (
        db.query(Applicant.company)
          .filter(Applicant.detail_job == req.detail_job)
          .distinct()
          .all()
    )
    return [adapt_company_row(r) for r in results]

@app.post("/get-detail-job-by-company")
@log_endpoint
def get_detail_jobs_by_company(req: schemas.CompanyOnlyRequest, db: Session = Depends(db_session_factory)):
    results = (
        db.query(Applicant.detail_job)
          .filter(Applicant.company == req.company)
          .distinct()
          .all()
    )
    return [adapt_detail_job_row(r) for r in results]

@app.get("/get-all-universities")
@log_endpoint
def get_all_universities(db: Session = Depends(db_session_factory)):
    results = (
        db.query(Applicant.university)
          .filter(Applicant.university.isnot(None))
          .filter(Applicant.university != "")
          .distinct()
          .all()
    )
    return [r[0] for r in results]

@app.post("/get-applicants-by-school")
@log_endpoint
def get_applicants_by_school(req: schemas.SchoolRequest, db: Session = Depends(db_session_factory)):
    results = (
        db.query(Applicant.company, Applicant.detail_job)
          .filter(Applicant.university == req.university)
          .distinct()
          .all()
    )
    return [adapt_company_and_job_row(r) for r in results]

@app.on_event("startup")
def test_db():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        print("✅ DB 연결 성공")
        db.close()
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)