import sys
from pathlib import Path
from fastapi import FastAPI
from routers.interview import router as interview_router
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    
app = FastAPI(
    version="0.0.1",
    title=" AI_INTERVIEW_PLATFROM",
    description="AI Interview Platform using FastAPI"
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(interview_router)