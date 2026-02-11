import { authClient } from '@/lib/auth-client';

// Base API configuration – Hugging Face Space live URL
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://sufiyan-23-00001111hakathon.hf.space/api';

// Helper to ensure HTTPS protocol for production, allow HTTP for localhost
const ensureCorrectProtocol = (url: string): string => {
  // Allow HTTP for localhost and 127.0.0.1 (development)
  if (url.includes('localhost') || url.includes('127.0.0.1')) {
    console.log('[API Protocol] Allowing HTTP for localhost development:', url);
    return url;
  }

  // Force HTTPS for production URLs
  if (url.startsWith('http://')) {
    console.warn('[API Protocol Fix] Converting HTTP to HTTPS for production:', url);
    return url.replace('http://', 'https://');
  }

  return url;
};

// Define frontend types (camelCase)
export interface Task {
  id: string;
  displayId?: number;  // Simple numeric ID for display
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
  userId: string;
  dueDate: string | null;
  priority: 'low' | 'medium' | 'high' | null;
}

export interface GetTasksResponse {
  tasks: Task[];
  totalCount: number;
  currentPage: number;
  totalPages: number;
}

export interface CreateTaskResponse {
  task: Task;
  message: string;
}

export interface UpdateTaskResponse {
  task: Task;
  message: string;
}

export interface DeleteTaskResponse {
  message: string;
}

export interface LoginResponse {
  user: any;
  token: string;
  message: string;
}

export interface SignupResponse {
  user: any;
  token: string;
  message: string;
}

// Helper to transform backend task (snake_case → camelCase)
const transformTask = (backendTask: any): Task => {
  if (!backendTask) return {} as Task;
  console.log('[API Transform] RAW backend task:', backendTask);

  const transformedTask: Task = {
    id: backendTask.id || backendTask._id,
    displayId: backendTask.display_id || backendTask.displayId,
    title: backendTask.title,
    description: backendTask.description,
    completed: backendTask.completed || false,
    createdAt: backendTask.created_at || backendTask.createdAt,
    updatedAt: backendTask.updated_at || backendTask.updatedAt,
    userId: backendTask.user_id || backendTask.userId,
    dueDate: backendTask.due_date || backendTask.dueDate || null,
    priority: backendTask.priority || backendTask.Priority || null,
  };

  console.log('[API Transform] FINAL task:', {
    id: transformedTask.id,
    displayId: transformedTask.displayId,
    title: transformedTask.title
  });

  return transformedTask;
};

// Transform response ONLY for task-related endpoints
const transformResponse = <T>(rawResult: any, endpoint: string): T => {
  if (endpoint.startsWith('/tasks')) {
    // ✅ Handle case where response is directly an array of tasks
    if (Array.isArray(rawResult)) {
      console.log('[API Transform] Response is array, transforming all tasks');
      return rawResult.map(transformTask) as T;
    }

    // Handle case where response has a 'task' property (single task)
    if (rawResult.task) {
      rawResult.task = transformTask(rawResult.task);
    }

    // Handle case where response has a 'tasks' property (array of tasks)
    if (rawResult.tasks && Array.isArray(rawResult.tasks)) {
      rawResult.tasks = rawResult.tasks.map(transformTask);
    }
  }
  return rawResult as T;
};

class ApiClient {
  private baseUrl: string;

  constructor() {
    // Allow HTTP for localhost, enforce HTTPS for production
    this.baseUrl = ensureCorrectProtocol(API_BASE);
    console.log('[API Client] Initialized with base URL:', this.baseUrl);
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    if (typeof window !== 'undefined') {
      // Try the new auth storage format first
      const storedData = localStorage.getItem('auth');
      if (storedData) {
        try {
          const authData = JSON.parse(storedData);
          const token = authData.token;
          if (token) {
            console.log('[API] Using Bearer token from localStorage');
            return { Authorization: `Bearer ${token}` };
          }
        } catch (e) {
          console.error('Error parsing auth data:', e);
        }
      }

      // Fallback to the old format for compatibility
      const oldToken = localStorage.getItem('token');
      if (oldToken) {
        console.log('[API] Using Bearer token from old storage format');
        return { Authorization: `Bearer ${oldToken}` };
      }
    }
    console.log('[API] No auth token found');
    return {};
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // Properly construct the URL ensuring no double slashes and correct protocol
    const normalizedBaseUrl = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    let url = `${normalizedBaseUrl}${normalizedEndpoint}`;

    // Ensure the URL is always HTTPS regardless of how it's constructed
    url = ensureCorrectProtocol(url);

    console.log(`[API Request] ${options.method || 'GET'} ${url}`);

    const authHeaders = await this.getAuthHeaders();

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        ...authHeaders,
        ...options.headers,
      },
      cache: 'no-store' as RequestCache,
    };

    try {
      const response = await fetch(url, config);

      // Additional check for protocol downgrade after fetch
      if (response.url && response.url.startsWith('http://')) {
        console.error(`[API PROTOCOL ERROR] Request resulted in HTTP URL: ${response.url}`);
        // Try to reconstruct with HTTPS if we detect a downgrade
        const httpsResponseUrl = response.url.replace('http://', 'https://');
        console.warn(`[API PROTOCOL FIX] Attempting to use HTTPS version: ${httpsResponseUrl}`);
      }

      if (!response.ok) {
        const err = await response.json().catch(() => ({ message: `HTTP ${response.status}` }));
        console.error(`[API ERROR] ${url} → ${response.status}`, err);
        throw new Error(err.message || `Request failed: ${response.status}`);
      }

      const result = await response.json();

      if (endpoint.startsWith('/tasks') && !result) {
        return [] as unknown as T;
      }

      const transformed = transformResponse<T>(result, endpoint);
      console.log(`[API] Success for ${endpoint}:`, transformed);
      return transformed;
    } catch (error) {
      console.error(`[API] Request failed: ${url}`, error);
      // If it's a network error related to mixed content, provide more specific info
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.error(`[API NETWORK ERROR] This may be a mixed content error. Ensure your API endpoint (${url}) supports HTTPS.`);
      }
      throw error;
    }
  }

  async getTasks(
    status?: 'all' | 'pending' | 'completed',
    sortBy?: 'createdAt' | 'title' | 'dueDate',
    sortOrder?: 'asc' | 'desc',
    cacheBust?: string
  ): Promise<GetTasksResponse> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (sortBy) params.append('sortBy', sortBy);
    if (sortOrder) params.append('sortOrder', sortOrder);
    if (cacheBust) params.append('_t', cacheBust);

    const queryString = params.toString();
    const endpoint = `/tasks${queryString ? `?${queryString}` : ''}`;

    console.log('[API] Fetching tasks from:', endpoint);

    // ✅ Backend returns array directly, not wrapped in object
    const result = await this.request<Task[]>(endpoint);

    console.log('[API] getTasks raw result:', result);
    console.log('[API] First task displayId:', result[0]?.displayId);

    // ✅ Wrap array in GetTasksResponse format for frontend compatibility
    return {
      tasks: result,
      totalCount: result.length,
      currentPage: 1,
      totalPages: 1
    };
  }

  async getTaskById(id: string): Promise<Task> {
    return this.request<Task>(`/tasks/${id}`);
  }

  async createTask(taskData: Omit<Task, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<CreateTaskResponse> {
    console.log('[API] Creating task:', taskData);

    const response = await this.request<CreateTaskResponse>('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });

    console.log('[API] Task created - Full response:', response);
    console.log('[API] Task UUID:', response.task?.id);
    console.log('[API] Task displayId:', response.task?.displayId);

    return response;
  }

  async updateTask(id: string, taskData: Partial<Task>): Promise<UpdateTaskResponse> {
    return this.request<UpdateTaskResponse>(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(id: string): Promise<DeleteTaskResponse> {
    return this.request<DeleteTaskResponse>(`/tasks/${id}`, { method: 'DELETE' });
  }

  async toggleTaskCompletion(id: string): Promise<UpdateTaskResponse> {
    console.log("[API] Toggle completion for task:", id);
    return this.request<UpdateTaskResponse>(`/tasks/${id}/toggle-completion`, {
      method: 'PATCH',
    });
  }

  // Authentication methods
  async login(email: string, password: string): Promise<LoginResponse> {
    console.log("[API] Login attempt:", email);
    const normalizedBaseUrl = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
    let url = `${normalizedBaseUrl}/auth/login`;

    // Use the protocol helper (allows HTTP for localhost)
    url = ensureCorrectProtocol(url);

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Login failed' }));
      console.error("[API] Login failed:", response.status, errorData);
      throw new Error(errorData.message || 'Login failed');
    }

    const result = await response.json();

    if (typeof window !== 'undefined') {
      localStorage.setItem('auth', JSON.stringify({ token: result.token }));
      console.log("[API] Login success - token stored");
    }

    return result;
  }

  async signup(email: string, password: string): Promise<SignupResponse> {
    console.log("[API] Signup attempt:", email);
    const normalizedBaseUrl = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
    let url = `${normalizedBaseUrl}/auth/signup`;

    // Use the protocol helper (allows HTTP for localhost)
    url = ensureCorrectProtocol(url);

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Signup failed' }));
      console.error("[API] Signup failed:", response.status, errorData);
      throw new Error(errorData.message || 'Signup failed');
    }

    const result = await response.json();

    if (typeof window !== 'undefined') {
      localStorage.setItem('auth', JSON.stringify({ token: result.token }));
      console.log("[API] Signup success - token stored");
    }

    return result;
  }

  async logout(): Promise<{ message: string }> {
    // Use the same URL construction and HTTPS enforcement as the main request method
    const normalizedBaseUrl = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
    let url = `${normalizedBaseUrl}/auth/logout`;

    // Ensure the URL is always HTTPS
    url = ensureCorrectProtocol(url);

    // Additional safety check for auth endpoints
    if (!url.startsWith('https://')) {
      console.error(`[API AUTH ERROR] URL is not HTTPS after normalization: ${url}`);
      url = url.replace('http://', 'https://');
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Logout failed' }));
      throw new Error(errorData.message || 'Logout failed');
    }

    const result = await response.json();

    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth');
    }

    return result;
  }

  async getProfile(): Promise<any> {
    return this.request<any>('/auth/profile');
  }
}

export const apiClient = new ApiClient();

export const {
  getTasks,
  getTaskById,
  createTask,
  updateTask,
  deleteTask,
  toggleTaskCompletion,
  login,
  signup,
  logout,
  getProfile,
} = apiClient;
