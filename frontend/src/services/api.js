import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

// Request interceptor to attach JWT Bearer token if present
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for consistent error extraction and 401 handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token is invalid or expired
      const isLoginRequest = error.config?.url?.includes('/api/v1/auth/login');
      if (!isLoginRequest) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('auth_user');
        window.dispatchEvent(new Event('auth:unauthorized'));
      }
    }

    let message = 'An unexpected network error occurred.';
    if (error.response) {
      const data = error.response.data;
      if (typeof data?.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data?.detail)) {
        message = data.detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
      } else if (data?.message) {
        message = data.message;
      } else if (data?.error) {
        message = data.error;
      }
    } else if (error.request) {
      message = 'Cannot connect to backend server. Please ensure FastAPI is running on http://127.0.0.1:8000.';
    }
    return Promise.reject(new Error(message));
  }
);

export const apiService = {
  // Authentication Endpoints
  registerUser: async (userData) => {
    const res = await apiClient.post('/api/v1/auth/register', userData);
    return res.data;
  },

  loginUser: async (credentials) => {
    const res = await apiClient.post('/api/v1/auth/login', credentials);
    return res.data;
  },

  getCurrentUser: async () => {
    const res = await apiClient.get('/api/v1/auth/me');
    return res.data;
  },

  // System Health
  getSystemStatus: async () => {
    const res = await apiClient.get('/');
    return res.data;
  },

  // Student Endpoints
  getStudents: async (skip = 0, limit = 500) => {
    const res = await apiClient.get('/api/v1/students', { params: { skip, limit } });
    return res.data;
  },

  getStudentById: async (studentId) => {
    const res = await apiClient.get(`/api/v1/students/${encodeURIComponent(studentId)}`);
    return res.data;
  },

  createStudent: async (studentData) => {
    const res = await apiClient.post('/api/v1/students', studentData);
    return res.data;
  },

  deleteStudent: async (studentId) => {
    const res = await apiClient.delete(`/api/v1/students/${encodeURIComponent(studentId)}`);
    return res.data;
  },

  uploadStudentImages: async (studentId, files) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    const res = await apiClient.post(
      `/api/v1/students/${encodeURIComponent(studentId)}/images`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return res.data;
  },

  trainModel: async () => {
    const res = await apiClient.post('/api/v1/students/train/model');
    return res.data;
  },

  // Attendance Endpoints
  getTodayAttendance: async () => {
    const res = await apiClient.get('/api/v1/attendance/today');
    return res.data;
  },

  getAttendanceByDate: async (dateStr) => {
    const res = await apiClient.get(`/api/v1/attendance/date/${dateStr}`);
    return res.data;
  },

  getStudentAttendanceHistory: async (studentId) => {
    const res = await apiClient.get(`/api/v1/attendance/student/${encodeURIComponent(studentId)}`);
    return res.data;
  },

  recognizeAndMarkAttendance: async (imageFile, threshold = null) => {
    const formData = new FormData();
    formData.append('file', imageFile);
    const params = threshold ? { threshold } : {};
    const res = await apiClient.post('/api/v1/attendance/recognize', formData, {
      params,
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};

export default apiService;
