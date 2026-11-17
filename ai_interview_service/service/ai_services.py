import os
import json
import asyncio
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
from dotenv import load_dotenv
from model.interview import QuestionsIntroSchema, ReportSchema

load_dotenv()

# 1. read many API key from `.env`file
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2")
]

# filture all key which is found
ACTIVE_KEYS = [key for key in API_KEYS if key]

current_key_index = 0

def get_next_client():
    """চক্রাকারে (Round-robin) একটি একটি করে জেমিনি ক্লায়েন্ট রিটার্ন করবে"""
    global current_key_index
    if not ACTIVE_KEYS:
        # If key not in list,empty clint
        return genai.Client()
    
    key = ACTIVE_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(ACTIVE_KEYS)
    return genai.Client(api_key=key)

# latest model
MODEL_NAME = "gemini-3.8-flash"


# 2.Multi key and auto-retry logic(for 429 or 503) 
async def generate_with_multi_key_retry(api_call_func, max_retries=6):
    total_attempts = max_retries * max(len(ACTIVE_KEYS), 1)
    delay = 2

    for attempt in range(total_attempts):
        try:
            # API call by taking present clint instance
            client_instance = get_next_client()
            return await api_call_func(client_instance)
            
        except (ServerError, ClientError) as e:
            error_code = getattr(e, 'status_code', 500)
           
            if error_code in [429, 503]:
                print(f"⚠️ API Error ({error_code}). Switching API key and retrying... (Attempt {attempt + 1}/{total_attempts})")
                await asyncio.sleep(delay)
                delay *= 2
                continue
            else:
                raise e
        except Exception as e:
            #stop for any error
            raise e

    raise Exception("❌ All API keys are exhausted or rate limited!")



async def generate_questions_intro(job_title, job_description, resume_text):
    SYSTEM_PROMPT = f"""
        You are an AI interview expert, who generates questions based on candidate's job_title, job_description, resume_text.
        You need to find out candidate's name, you need to generate an introduction text including candidate's name, you need to generate questions
        based on job_description, job_title, user's skills, years of experience from resume_text.

        Input:
            job_title: {job_title},
            job_description: {job_description},
            resume_text: {resume_text}

        Output Structure:
            questions: array,
            introText: string,
            candidate_name: string

        Rules:
            - For Questions:
                a) Generate 10-15 questions.
                b) Consider years of experience to label of difficulty of interview questions.
                c) Questions should be easy to hard manner.
                d) Questions related to only Skills mentioned in resume, job_description and job_title
                e) Questions are needs to be small and to the point and some time scenario based.
            - For Introduction Text:
                a) It's simple text introduction which is going to be played on browser before starting the interview
                b) Include candidate name, job title in the text.
                c) Add your own creativity
            - For Candidate Name:
                a) Extract candidate name from resume, if candidate not found then consider candidate name as "Candidate".

            - Output:
                Output needs to be in json format and it should have questions, introText, candidate_name
    """

    async def call_api(client_instance):
        return await client_instance.aio.models.generate_content(
            model=MODEL_NAME,
            contents=SYSTEM_PROMPT,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=QuestionsIntroSchema,
            ),
        )

    response = await generate_with_multi_key_retry(call_api)
    return json.loads(response.text)


async def generate_report(answers = []):
    if not answers or all(
        getattr(item, "skip", True) or not getattr(item, "answer", None) 
        for item in answers
    ):
        return {
            "score": "0%",
            "correct_answer": 0,
            "improvment_area": ["No answers were provided during the interview."]
        }

    SYSTEM_PROMPT = f"""
        You are an expert AI interviewer, who analyzes the answers based on questions, and shares the feedbacks.
        You need to find out Score in percentage, Total Correct Answers and detailed areas of improvement (not more than 5 points).

        Input: {answers}

        Input Structure:
        answers is an array which will have objects. 
        - array[]
            - object
                - question: string = it'll contain question in string.
                - answer: string | None = if skip is true then answer will be None else answer will have string.
                - skip: bool = if user gives answer then skip = False else skip = True

        Output Structure:
        I need output in JSON format, and it'll contain below object
        - Object
            - score: string = It should calculate percentage from correct (answer / total question) % 100
            - correct_answer: number = number of correct answer
            - improvment_area: array of string = it'll contain area of improvement. not more than 5 points.

        Rule:
         - Don't be so strict to evaluate the answer.
         - Consider the answer is correct if candidate at least answered 70%. But provide the feedback
         - If candidate didn't answer anything then mark score 0%, correct_answer 0 and improvment_area as it is provided.
    """

    async def call_api(client_instance):
        return await client_instance.aio.models.generate_content(
            model=MODEL_NAME,
            contents=SYSTEM_PROMPT,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReportSchema,
                max_output_tokens=1500,
            ),
        )

    response = await generate_with_multi_key_retry(call_api)
    return json.loads(response.text)


async def rephrase_question(question: str) -> str:
    SYSTEM_PROMPT = f"""
        You are a friendly AI interviewer. The candidate did not understand the current question.
        Rephrase and simplify the question in plain, conversational English so it is easier to understand, without giving away the answer. Keep it short (1-2 sentences).

        Original Question: "{question}"
    """

    async def call_api(client_instance):
        return await client_instance.aio.models.generate_content(
            model=MODEL_NAME,
            contents=SYSTEM_PROMPT,
            config=types.GenerateContentConfig(
                temperature=0.4,
            ),
        )

    response = await generate_with_multi_key_retry(call_api)
    return response.text.strip()