import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Add subject
  addSubject: async (subject) => {
    try {
      const response = await api.post('/subjects', subject);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all subjects
  getSubjects: async () => {
    try {
      const response = await api.get('/subjects');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete subject
  deleteSubject: async (id) => {
    try {
      await api.delete(`/subjects/${id}`);
    } catch (error) {
      throw error;
    }
  },
};
