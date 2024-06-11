from typing import List

from fastapi import FastAPI, Depends, status, HTTPException, Request, Form
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import models
import schemas

from database import engine, SessionLocal

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def get_all_tasks(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Task).all()
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})


@app.post("/add")
def create_task(db: Session = Depends(get_db),
                title: str = Form(...),
                body: str = Form(...)):
    new_task = models.Task(title=title, body=body)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.post("/delete_task/{id}")
def delete_task(id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Cannot delete Blog with id {id}, because its not found")
    else:
        db.delete(task)
        db.delete(task)
        db.commit()
