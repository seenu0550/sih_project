import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getBatches: () => axios.get('http://localhost:8000/batches/public'),
  getProfile: (token) => {
    return api.get('/profile', {
      headers: { Authorization: `Bearer ${token}` }
    });
  },
};

// Classrooms API
export const classroomsAPI = {
  getAll: () => api.get('/classrooms/'),
  create: (classroom) => api.post('/classrooms/', classroom),
  update: (id, classroom) => api.put(`/classrooms/${id}`, classroom),
  delete: (id) => api.delete(`/classrooms/${id}`),
};

// Subjects API
export const subjectsAPI = {
  getAll: () => api.get('/subjects/'),
  create: (subject) => api.post('/subjects/', subject),
  update: (id, subject) => api.put(`/subjects/${id}`, subject),
  delete: (id) => api.delete(`/subjects/${id}`),
};

// Faculty API
export const facultyAPI = {
  getAll: () => api.get('/faculty/'),
  create: (faculty) => api.post('/faculty/', faculty),
  update: (id, faculty) => api.put(`/faculty/${id}`, faculty),
  delete: (id) => api.delete(`/faculty/${id}`),
};

// Batches API
export const batchesAPI = {
  getAll: () => api.get('/batches/'),
  create: (batch) => api.post('/batches/', batch),
  update: (id, batch) => api.put(`/batches/${id}`, batch),
  delete: (id) => api.delete(`/batches/${id}`),
};

// Timetables API
export const timetablesAPI = {
  getAll: () => api.get('/timetables/'),
  generate: (request) => api.post('/timetables/generate', request),
  save: (timetable) => api.post('/timetables/save', timetable),
  update: (id, timetable) => api.put(`/timetables/${id}`, timetable),
  approve: (id) => api.put(`/timetables/${id}/approve`),
  delete: (id) => api.delete(`/timetables/${id}`),
};

// Profile API
export const profileAPI = {
  get: () => api.get('/profile'),
  update: (profileData) => api.put('/profile', profileData),
};

export default api;