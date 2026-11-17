import { useEffect, useRef, useState } from "react";
import { APP_CONSTANT } from "../util/constant";
import StartInterview from "../components/StartInterview";
import { submitAPI, reportAPI, endInterviewAPI } from "../services/interview";
import { playAudio } from "../util/audio";
import Interview from "../components/Interview";
import { useSpeechToText } from "../hooks/useSpeechToText";
import Report from "../components/Report";
import "../assets/css/InterviewPage.css";

const InterviewPage = () => {
  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState(APP_CONSTANT.IDLE);
  const [question, setQuestion] = useState("");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  // for holding latest session and question
  const sessionIdRef = useRef(sessionId);
  const questionRef = useRef(question);

  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  useEffect(() => {
    questionRef.current = question;
  }, [question]);

  const isRepeatRequest = (text) => {
    const clean = text.toLowerCase().trim();
    const repeatKeywords = [
      "repeat",
      "repeat the question",
      "say again",
      "say that again",
      "pardon",
      "could you repeat",
      "please repeat",
    ];
    return clean.split(" ").length <= 7 && repeatKeywords.some((k) => clean.includes(k));
  };

  // শুধু status ASKING করলে নিচের useEffect নিজে থেকেই প্রশ্নটি একবার প্লে করবে
  const repeatQuestion = () => {
    stopListening();
    setStatus(APP_CONSTANT.ASKING);
  };

  const onAutoSubmit = async (finalText) => {
    stopListening();

    if (!finalText || !finalText.trim()) {
      return;
    }

    // repeat question
    if (isRepeatRequest(finalText)) {
      repeatQuestion();
      return;
    }

    // If answer normal then it will be submitting in database
    const payload = {
      session_id: sessionIdRef.current,
      answer: finalText,
      skip: false,
    };

    const data = await submitAPI(payload);
    if (!data) return;

    if (data.interviewEnded) {
      await finshInterview();
    } else {
      setQuestion(data.nextQuestion);
      setStatus(APP_CONSTANT.ASKING);
    }
  };

  const { startListening, stopListening } = useSpeechToText(onAutoSubmit);

  const finshInterview = async () => {
    setLoading(true);
    try {
      const data = await reportAPI(sessionIdRef.current);
      if (data && data.result) {
        setReport(data.result);
        setStatus(APP_CONSTANT.COMPLETED);
      }
    } finally {
      setLoading(false);
    }
  };

  const endInterview = async () => {
    stopListening();
    setLoading(true);
    await endInterviewAPI(sessionIdRef.current);
    await finshInterview();
  };

  const skipQuestion = async () => {
    stopListening();

    const payload = {
      session_id: sessionIdRef.current,
      answer: "",
      skip: true,
    };

    const data = await submitAPI(payload);
    if (!data) return;

    if (data.interviewEnded) {
      await finshInterview();
    } else {
      setQuestion(data.nextQuestion);
      setStatus(APP_CONSTANT.ASKING);
    }
  };

  useEffect(() => {
    if (status === APP_CONSTANT.ASKING && question) {
      playAudio(question, () => {
        setStatus(APP_CONSTANT.LISTENING);
        startListening();
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, question]);

  const startInterview = async (data, session_id) => {
    setLoading(true);

    setSessionId(session_id);
    setQuestion(data.firstQuestion);
    setStatus(APP_CONSTANT.INTRO);

    const introText = data.introText;
    playAudio(introText, () => {
      setLoading(false);
      setStatus(APP_CONSTANT.ASKING);
    });
  };

  return (
    <>
      {loading && <div className="loader"></div>}

      {status === APP_CONSTANT.IDLE && <StartInterview onClick={startInterview} />}

      {(status === APP_CONSTANT.ASKING || status === APP_CONSTANT.LISTENING) && (
        <Interview
          repeatQuestion={repeatQuestion}
          skipQuestion={skipQuestion}
          endInterview={endInterview}
          state={status}
        />
      )}

      {status === APP_CONSTANT.COMPLETED && <Report report={report} />}
    </>
  );
};

export default InterviewPage;