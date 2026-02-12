import { useState, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const useAI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeClassroom = useCallback(async (studentsData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/classroom-insights`, {
        students: studentsData
      }, {
        timeout: 15000
      });

      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'AI analysis failed';
      setError(errorMessage);
      console.error('AI analysis error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const checkAllCode = useCallback(async (students, language = 'python') => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/check-all-code`, {
        students,
        language
      }, {
        timeout: 30000
      });

      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Code review failed';
      setError(errorMessage);
      console.error('Code review error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const generateMessage = useCallback(async (studentContext) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ai/message-suggest`,
        studentContext,
        { timeout: 10000 }
      );

      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Message generation failed';
      setError(errorMessage);
      console.error('Message generation error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    analyzeClassroom,
    checkAllCode,
    generateMessage,
    isLoading,
    error
  };
};
