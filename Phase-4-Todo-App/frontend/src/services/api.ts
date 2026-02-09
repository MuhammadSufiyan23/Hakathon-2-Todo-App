// API client for todo operations
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests - match backend auth expectations
apiClient.interceptors.request.use((config) => {
  const storedAuth = localStorage.getItem('auth');
  let token = null;

  if (storedAuth) {
    try {
      const authData = JSON.parse(storedAuth);
      token = authData.token;
    } catch (e) {
      console.error('Error parsing auth data from localStorage:', e);
    }
  }

  if (token) {
    if (!config.headers) {
      config.headers = {};
    }
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Chat API functions
export const chatApi = {
  sendMessage: async (userId: string, message: string, conversationId?: number | null | undefined) => {
    const requestBody = {
      message,
      conversation_id: conversationId ?? null
    };

    try {
      const response = await apiClient.post(`/${userId}/chat`, requestBody);

      // Handle different response structures gracefully
      if (response.data && typeof response.data === 'object') {
        // Type assertion to handle the response property safely
        const responseData = response.data as { response?: string };
        if ('response' in responseData && responseData.response) {
          return { response: responseData.response, success: true };
        } else {
          return { response: JSON.stringify(response.data), success: true }; // Fallback for other object responses
        }
      } else if (response.data && typeof response.data === 'string') {
        return { response: response.data, success: true }; // Wrap string response
      } else {
        return { response: 'Received response from server', success: true }; // Safe fallback
      }
    } catch (error: any) {
      console.error('Chat API error:', error);
      if (error.response) {
        // Server responded with error status
        throw new Error(`Server error: ${error.response.status} - ${error.response.data.detail || 'Unknown error'}`);
      } else if (error.request) {
        // Request was made but no response received
        throw new Error('Network error: Unable to reach the server. Please check your connection.');
      } else {
        // Something else happened
        throw new Error(`Request error: ${error.message}`);
      }
    }
  }
};

// Existing todo API functions
export const todoApi = {
  getTodos: async () => {
    const response = await apiClient.get('/tasks');
    return response.data;
  },

  addTodo: async (todoData: { title: string; description?: string; completed?: boolean }) => {
    const response = await apiClient.post('/tasks', todoData);
    return response.data;
  },

  updateTodo: async (id: string, todoData: Partial<{ title: string; description?: string; completed?: boolean }>) => {
    const response = await apiClient.put(`/tasks/${id}`, todoData);
    return response.data;
  },

  deleteTodo: async (id: string) => {
    const response = await apiClient.delete(`/tasks/${id}`);
    return response.data;
  },

  toggleComplete: async (id: string) => {
    const response = await apiClient.patch(`/tasks/${id}/toggle-complete`);
    return response.data;
  }
};

export default apiClient;