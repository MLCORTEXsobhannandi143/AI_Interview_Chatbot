from enum import Enum
from typing import Optional,Dict,Any
from pydantic import BaseModel


class InteriewStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Answer(BaseModel):
    question: str
    answer: Optional[str]
    skip: bool = False

class InterviewSession(BaseModel):
    session_id: str
    questions: list[str] = []
    status: InteriewStatusEnum = InteriewStatusEnum.IN_PROGRESS
    answers: list[Answer] = []
    current_index: int = 0
    introText: str = ""
    report: Optional[Dict[str, Any]] = None

class QuestionsIntroSchema(BaseModel):
    questions: list[str]
    introText: str
    candidate_name: str

class ReportSchema(BaseModel):
    score: str
    correct_answer: int
    improvment_area: list[str]

