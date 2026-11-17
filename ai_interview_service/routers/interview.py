from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from model.interview import InteriewStatusEnum
from request_model.Answer_request import AnswerRequest
from response_model.Answer_response import AnswerResponse

from service.ai_services import generate_questions_intro, generate_report, rephrase_question
from service.interview_service import create_session, get_session, save_answer
from utill.file_utill import extract_text, validate_file

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)

REPEAT_EXACT = ["repeat", "say again", "pardon", "repeat the question", "আবার বলুন"]
EXPLAIN_SIMPLE = ["didn't understand", "don't understand", "explain", "rephrase", "simplify", "বুঝতে পারিনি"]


@router.post("/generate-question")
async def generate_questions(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        await validate_file(resume)
        resume_text = await extract_text(resume)

        resp = await generate_questions_intro(job_title=job_title, job_description=job_description, resume_text=resume_text)

        session = create_session()
        session.questions = resp.get("questions")
        session.introText = resp.get("introText")

        return { "session_id": session.session_id }
        
    except Exception as e:
    
        print(f"CRITICAL BACKEND ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/start/{session_id}")
async def start_interview(session_id: str):
    session = get_session(session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")

    return {
        "introText": session.introText,
        "firstQuestion": session.questions[0]
    }


@router.post("/submit", response_model=AnswerResponse)
async def submit_answer(answerReq: AnswerRequest):
    session = get_session(answerReq.session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")

    # aleart for candidate response
    user_text = answerReq.answer.lower().strip() if (answerReq.answer and not answerReq.skip) else ""
    
    if len(user_text.split()) <= 8:
        current_question = session.questions[session.current_index]
        
        # for repeted question answer will not be save
        if any(word in user_text for word in REPEAT_EXACT):
            return {
                "interviewEnded": False,
                "nextQuestion": current_question
            }
        
        
        elif any(word in user_text for word in EXPLAIN_SIMPLE):
            simplified_question = await rephrase_question(current_question)
            return {
                "interviewEnded": False,
                "nextQuestion": simplified_question
            }

    
    save_answer(answerReq.answer, answerReq.skip, session)

    if session.status == InteriewStatusEnum.COMPLETED:
        return {
            "interviewEnded": True
        }
    
    return {
        "interviewEnded": False,
        "nextQuestion": session.questions[session.current_index]
    }


@router.put("/end/{session_id}")
async def end_interview(session_id: str):
    session = get_session(session_id)
    if not session or session.status == InteriewStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")
    
    session.status = InteriewStatusEnum.COMPLETED

    return {
        "interviewEnded": True
    }


@router.get("/report/{session_id}")
async def report(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview Session Not Found")
    
    # If report has generated already ,it returns this report 
    if hasattr(session, "report") and session.report:
        return { "result": session.report }

    resp = await generate_report(session.answers)
    session.report = resp  # session have saved for future

    return { "result": resp }