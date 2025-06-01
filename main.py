from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import RecruitQualification, Applicant
import schemas

app = FastAPI(title="Spectrackr API", description="채용정보를 위한 FastAPI", version="1.0")

# 의존성: 요청마다 DB 세션 생성 → 종료
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. /get-company-name-and-detail-job
@app.post("/get-company-name-and-detail-job", response_model=list[schemas.CompanyAndDetailJob], tags=['회사 기준 검색'])
def get_company_name_and_detail_job(req: schemas.JobCategoryRequest, db: Session = Depends(get_db)):
    results = db.query(RecruitQualification.company_name, RecruitQualification.detail_job) \
        .filter(RecruitQualification.job_category == req.job_category).all()
    return results

# 2. /get-detail-job-by-company-name
@app.post("/get-detail-job-by-company-name", response_model=list[schemas.DetailJob], tags=['회사 기준 검색'])
def get_detail_job_by_company_name(req: schemas.CompanyNameRequest, db: Session = Depends(get_db)):
    results = db.query(RecruitQualification.detail_job) \
        .filter(RecruitQualification.company_name == req.company_name).all()
    return results

# 3. /get-company-name-by-detail-job
@app.post("/get-company-name-by-detail-job", response_model=list[schemas.CompanyName], tags=['회사 기준 검색'])
def get_company_name_by_detail_job(req: schemas.DetailJobRequest, db: Session = Depends(get_db)):
    results = db.query(RecruitQualification.company_name) \
        .filter(RecruitQualification.detail_job == req.detail_job).all()
    return results

# main.py 수정
@app.post("/get-job-posting", response_model=list[schemas.JobPosting], tags=['회사 기준 검색'])
def get_job_posting(req: schemas.JobPostingRequest, db: Session = Depends(get_db)):
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

# 5. /get-applicants
@app.post("/get-applicants-by-company-detail-job", response_model=list[schemas.ApplicantSchema], tags=["스펙 기준 검색"])
def get_applicants_by_company_detail_job(req: schemas.ApplicantSearchByCompanyDetailJobRequest, db: Session = Depends(get_db)):
    results = db.query(Applicant).filter(
        Applicant.company == req.company,
        Applicant.detail_job == req.detail_job
    ).all()
    return results

# 6. /get-companies-by-detail-job
@app.post("/get-companiy-by-detail-job", response_model=list[schemas.CompanyList], tags=['스펙 기준 검색'])
def get_companies_by_detail_job(req: schemas.DetailJobOnlyRequest, db: Session = Depends(get_db)):
    results = db.query(Applicant.company).filter(Applicant.detail_job == req.detail_job).distinct().all()
    return [{"company": r[0]} for r in results]

# 7. /get-detail-jobs-by-company
@app.post("/get-detail-job-by-company", response_model=list[schemas.DetailJobList], tags=['스펙 기준 검색'])
def get_detail_jobs_by_company(req: schemas.CompanyOnlyRequest, db: Session = Depends(get_db)):
    results = db.query(Applicant.detail_job).filter(Applicant.company == req.company).distinct().all()
    return [{"detail_job": r[0]} for r in results]

# 8. /get-all-universities
@app.get("/get-all-universities", response_model=list[str], tags=["스펙 기준 검색"])
def get_all_universities(db: Session = Depends(get_db)):
    results = db.query(Applicant.university) \
                .filter(Applicant.university.isnot(None)) \
                .filter(Applicant.university != "") \
                .distinct().all()
    return [r[0] for r in results]

@app.post("/get-applicants-by-school", response_model=list[schemas.CompanyAndJob], tags=["스펙 기준 검색"])
def get_applicants_by_school(req: schemas.SchoolRequest, db: Session = Depends(get_db)):
    results = db.query(Applicant.company, Applicant.detail_job) \
        .filter(Applicant.university == req.university) \
        .distinct().all()
    return [{"company": r[0], "detail_job": r[1]} for r in results]



@app.get("/")
def root():
    return {"message": "Spectrackr API is live!"}

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