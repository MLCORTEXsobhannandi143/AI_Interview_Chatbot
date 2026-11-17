import axios from "axios";

const apiClient = axios.create({
  baseURL: "https://ai-chatbot-for-interview.onrender.com",
  timeout: 30000, // If it take time more than 30 second then it generate error
});

export const startInterviewAPI = async (sessionId) => {
  try {
    const response = await apiClient.get(`/start/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error("Start Interview Error:", error.response?.data || error.message);
    return null;
  }
};

export const submitAPI = async (payload) => {
  try {
    const response = await apiClient.post("/submit", payload);
    return response.data;
  } catch (error) {
    console.error("Submit Answer Error:", error.response?.data || error.message);
    return null;
  }
};

export const reportAPI = async (sessionId) => {
  try {
    const response = await apiClient.get(`/report/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error("Report Generation Error:", error.response?.data || error.message);
    return null;
  }
};

export const endInterviewAPI = async (sessionId) => {
  try {
    const response = await apiClient.put(`/end/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error("End Interview Error:", error.response?.data || error.message);
    return null;
  }
};

export const generateQuestionsAPI = async (formData) => {
  try {
    // sending FormData Axios rebuild write Content-Type ও boundary and set it.
    const response = await apiClient.post("/generate-question", formData);
    return response.data;
  } catch (error) {
    console.error("Generate Questions Error:", error.response?.data || error.message);
    return null;
  }
};