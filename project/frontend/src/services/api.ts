// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://interviewiq-production-e6c9.up.railway.app/api';

// Types
export interface User {
  id: string;
  email: string;
  name: string;
}

export interface AuthData {
  token: string;
  user: User;
}

export interface InterviewSessionData {
  id: string;
  user_id?: string;
  resume_text?: string;
  resume_filename?: string;
  personality: string;
  status: 'in_progress' | 'completed' | 'abandoned';
  created_at: string;
  completed_at?: string;
}

export interface InterviewResponse {
  id: string;
  session_id: string;
  question_index: number;
  question: string;
  answer: string;
  input_mode: 'text' | 'audio' | 'video';
  recording_duration: number;
  timestamp: number;
}

export interface PerformanceResult {
  id: string;
  session_id: string;
  technical_accuracy: number;
  language_proficiency: number;
  confidence_level: number;
  sentiment_score: number;
  emotional_stability: number;
  overall_score: number;
  feedback?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Helper function for API calls
async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  try {
    const token = sessionStorage.getItem('interviewiq_token');
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || data.error || 'API request failed');
    }
    return data;
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

// Auth API
export const authApi = {
  register: async (name: string, email: string, password: string): Promise<ApiResponse<AuthData>> => {
    return apiCall('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  login: async (email: string, password: string): Promise<ApiResponse<AuthData>> => {
    return apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  getMe: async (): Promise<ApiResponse<User>> => {
    return apiCall('/auth/me');
  },
};

// Session API
export const sessionApi = {
  create: async (data: {
    resume_text?: string;
    resume_filename?: string;
    personality: string;
    user_id?: string;
  }): Promise<ApiResponse<InterviewSessionData>> => {
    return apiCall('/sessions/', { method: 'POST', body: JSON.stringify(data) });
  },

  getById: async (id: string): Promise<ApiResponse<InterviewSessionData>> => {
    return apiCall(`/sessions/${id}`);
  },

  getAll: async (page = 1, limit = 10) => {
    return apiCall(`/sessions/?page=${page}&limit=${limit}`);
  },

  getFull: async (id: string) => {
    return apiCall(`/sessions/${id}/full`);
  },

  updateStatus: async (id: string, status: string): Promise<ApiResponse<void>> => {
    return apiCall(`/sessions/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },

  delete: async (id: string): Promise<ApiResponse<void>> => {
    return apiCall(`/sessions/${id}`, { method: 'DELETE' });
  },
};

// Interview API
export const interviewApi = {
  saveResponse: async (data: {
    session_id: string;
    question_index: number;
    question: string;
    answer: string;
    input_mode?: string;
    recording_duration?: number;
    timestamp: number;
  }) => {
    return apiCall('/interviews/responses', { method: 'POST', body: JSON.stringify(data) });
  },

  saveResponsesBatch: async (
    session_id: string,
    responses: Array<{
      question_index: number;
      question: string;
      answer: string;
      input_mode?: string;
      recording_duration?: number;
      timestamp: number;
    }>
  ) => {
    return apiCall('/interviews/responses/batch', {
      method: 'POST',
      body: JSON.stringify({ session_id, responses }),
    });
  },

  getResponses: async (sessionId: string) => {
    return apiCall(`/interviews/responses/${sessionId}`);
  },

  saveResults: async (data: {
    session_id: string;
    technical_accuracy: number;
    language_proficiency: number;
    confidence_level: number;
    sentiment_score: number;
    emotional_stability: number;
    feedback?: string;
  }) => {
    return apiCall('/interviews/results', { method: 'POST', body: JSON.stringify(data) });
  },

  getResults: async (sessionId: string) => {
    return apiCall(`/interviews/results/${sessionId}`);
  },

  getQuestions: async (personality: string) => {
    return apiCall(`/interviews/questions/${personality}`);
  },

  getStats: async () => {
    return apiCall('/interviews/stats/overview');
  },
};

// Health check
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
};

// AI API
export const aiApi = {
  uploadResume: async (file: File): Promise<ApiResponse<{
    resume_text: string;
    filename: string;
    analysis: {
      name: string | null;
      email: string | null;
      skills: string[];
      experience: Array<{ title: string; company: string; duration: string; highlights: string[] }>;
      education: Array<{ degree: string; institution: string; year: string }>;
      summary: string;
    };
    char_count: number;
  }>> => {
    try {
      const token = sessionStorage.getItem('interviewiq_token');
      const formData = new FormData();
      formData.append('file', file);

      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch(`${API_BASE_URL}/ai/resume/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Upload failed');
      return data;
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Upload failed' };
    }
  },

  /** Server-side speech-to-text: send a WAV blob, get back a transcript. */
  transcribeAudio: async (audioBlob: Blob): Promise<ApiResponse<{ transcript: string }>> => {
    try {
      const token = sessionStorage.getItem('interviewiq_token');
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.wav');

      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch(`${API_BASE_URL}/ai/transcribe`, {
        method: 'POST',
        headers,
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Transcription failed');
      return data;
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : 'Transcription failed' };
    }
  },

  generateQuestions: async (sessionId: string, personality: string, numQuestions = 15): Promise<ApiResponse<{
    questions: Array<{ question: string; category: string; difficulty: string }>;
    personality: string;
    resume_skills: string[];
  }>> => {
    return apiCall('/ai/questions/generate', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, personality, num_questions: numQuestions }),
    });
  },

  evaluateInterview: async (sessionId: string): Promise<ApiResponse<{
    technical_accuracy: number;
    language_proficiency: number;
    confidence_level: number;
    sentiment_score: number;
    emotional_stability: number;
    overall_score: number;
    per_question_feedback: Array<{ question_index: number; score: number; strength: string; improvement: string }>;
    recommendations: string[];
    summary_feedback: string;
  }>> => {
    return apiCall('/ai/evaluate', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  },
};

// Report API
export const reportApi = {
  emailReport: async (sessionId: string, recipientEmail: string, recipientName?: string): Promise<ApiResponse<{
    delivered: boolean;
    fallback?: boolean;
    report_text?: string;
    recipient?: string;
    message: string;
  }>> => {
    return apiCall('/reports/email', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, recipient_email: recipientEmail, recipient_name: recipientName }),
    });
  },

  generateReport: async (sessionId: string): Promise<ApiResponse<{
    report_text: string;
    session_id: string;
    generated_at: string;
  }>> => {
    return apiCall('/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  },
};

export default { session: sessionApi, interview: interviewApi, ai: aiApi, report: reportApi, healthCheck };
