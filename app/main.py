from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.estudiante import Estudiante


app = FastAPI()



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/Estudiantes")
def get_estudiantes(db: Session = Depends(get_db)):
    estudiantes = db.query(Estudiante).all()
    return estudiantes


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)     
    
























































































































