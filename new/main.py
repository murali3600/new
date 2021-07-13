from typing import List
from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, status
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session, query
from sqlalchemy.sql.elements import RollbackToSavepointClause


from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


start = datetime.now(timezone.utc)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/jobs/", response_model=schemas.User)
def create_job(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_job_by_id(db, role= user.role)
    if db_user:
        raise HTTPException(status_code=400, detail="role already registered")
    return crud.create_job(db=db, user=user)


@app.get("/jobs/", response_model=List[schemas.User])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    job = crud.get_jobs(db, skip=skip, limit=limit)
    return job


@app.get("/job/{job_id}", response_model=schemas.User)
def read_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return db_job




@app.post("/job/{job_id}/apply/",response_model=schemas.apply)
def apply(job_id: int, user_id: int, apply: schemas.applyCreate, db: Session = Depends(get_db)):
     db_job = crud.get_job(db, job_id=job_id)
     db_user = crud.get_user(db, user_id=user_id)
     
     if db_job is None:
        raise HTTPException(status_code=404, detail="job not found")
     elif db_user is None:
         raise HTTPException(status_code=404, detail="user not found")
     
     return crud.apply( db=db, apply=apply, job_id=job_id, user_id=user_id )
  



@app.delete('/jobs/{id}')
def destroy(id, db: Session = Depends(get_db)):
    db.query(models.User).filter(models.User.id == id).delete(synchronize_session=False)
    db.commit()
    return 'done'
