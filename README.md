# AI_Interview_Chatbot
An intelligent AI-powered mock interview platform built with FastAPI and React that analyzes resumes, conducts dynamic technical/HR interviews, and provides real-time feedback.



🚀 Tech Stack
This project is built using the following technologies:



Backend: FastAPI (Python)
Frontend: ReactJS
AI Engine: OpenAI
Containerization: Docker & Docker Compose




🧠 Features
The user shall be able to enter a job title, job description, and upload a resume.
The user shall be able to start the interview after providing the required information.
The system shall analyze the resume, job title, and job description to generate personalized interview questions based on:
Relevant skills
Years of experience
Job role requirements
The AI bot shall ask interview questions one at a time.
The user shall be able to answer a question or skip a question.
Once all questions have been asked or the user ends the interview manually, the system shall generate a detailed interview feedback report, including:
Performance evaluation
Strengths and improvement areas
Overall interview summary




🐳 Prerequisites
Before running the application, make sure you have the following installed:

Python 3+
NodeJS
Docker (Optional)
Set Environment Variables
GEMINI_API_KEY=your_api_key_here
▶️ Run the Application
To start the application using docker, run the following command from the project root directory:

docker compose up -d
OR To start the application manually
Start Backend
cd ai_interview_service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
Start Frontend
cd ai_interview_frontend
npm install
npm start
