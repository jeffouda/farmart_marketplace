import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Password validation utility
const validatePassword = (password) => {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecialChar = /[@$!%*?&]/.test(password);

  if (password.length < minLength) {
    return 'Password must be at least 8 characters';
  }
  if (!hasUpperCase || !hasLowerCase) {
    return 'Password must contain uppercase and lowercase letters';
  }
  if (!hasNumber) {
    return 'Password must contain a number';
  }
  if (!hasSpecialChar) {
    return 'Password must contain a special character (@$!%*?&)';
  }
  return null;
};

// Utility for robust error extraction with Mercy Logic for 401 handling
const extractErrorMessage = (error) => {
  // Handle plain string errors (from api.js service layer)
  if (typeof error === 'string') {
    return error;
  }

  // Handle axios error objects
  if (error.response) {
    const { status, data } = error.response;

    // Check for explicit error message from backend
    if (data?.error) {
      if (Array.isArray(data.error)) {
        return data.error.join(', ');
      }
      return data.error;
    }
    if (data?.message) return data.message;
    if (data?.detail) return data.detail;

    // Status-specific messages
    if (status === 401) {
      // Mercy Logic: Don't show generic message for 401
      return 'Session expired. Please log in again.';
    }
    if (status === 403) return 'Your account is not verified';
    if (status === 404) return 'Resource not found';
    if (status === 422) return 'Validation error';
    if (status === 429) return 'Too many attempts. Please try again later';

    return `Request failed with status ${status}`;
  }

  // Handle network errors
  if (error.request) {
    return 'Network error. Please check your connection.';
  }

  // Fallback
  return 'An unexpected error occurred. Please try again.';
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/login', credentials);
      
      const access_token = response?.access_token;
      const user = response?.user;
      
      if (!access_token || !user) {
        throw new Error('Invalid response from server');
      }
      
      localStorage.setItem('token', access_token);
      return { access_token, user };
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error));
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/register', userData);
      return response;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error));
    }
  }
);

export const getProfile = createAsyncThunk(
  'auth/profile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/auth/me');
      return response;
    } catch (error) {
      return rejectWithValue(extractErrorMessage(error));
    }
  }
);

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData, { rejectWithValue, getState }) => {
    try {
      // Mercy Logic: Check if this is a file upload (FormData)
      const isFileUpload = profileData instanceof FormData;
      
      const response = await api.patch('/auth/profile', profileData);
      return response;
    } catch (error) {
      const message = extractErrorMessage(error);
      
      // Mercy Logic: For file uploads with 401, return special message
      // Don't trigger logout - let the UI handle session refresh
      if (error.response?.status === 401 && profileData instanceof FormData) {
        return rejectWithValue('Session expired during file upload. Refreshing session... Please try again.');
      }
      
      return rejectWithValue(message);
    }
  }
);

// Initial state - production ready
const initialState = {
  user: null,
  isAuthenticated: false,
  token: localStorage.getItem('token') || null,
  loading: false,
  error: null,
  isRefreshing: false, // For Mercy Logic
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.token = null;
      state.error = null;
      state.isRefreshing = false;
      localStorage.removeItem('token');
    },
    clearError: (state) => {
      state.error = null;
    },
    setRefreshing: (state, action) => {
      state.isRefreshing = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload?.user || null;
        state.token = action.payload?.access_token || null;
        state.isRefreshing = false;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.isRefreshing = false;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Get Profile
      .addCase(getProfile.fulfilled, (state, action) => {
        state.user = action.payload?.user || action.payload || null;
        state.isAuthenticated = true;
      })
      // Update Profile with Mercy Logic
      .addCase(updateProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.isRefreshing = false;
        if (action.payload?.user) {
          state.user = action.payload.user;
        }
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.loading = false;
        // Don't logout automatically - Mercy Logic
        state.error = action.payload;
        
        // Check if session expired during file upload
        if (action.payload?.includes?.('Session expired')) {
          state.isRefreshing = true;
        }
      });
  },
});

export const { logout, clearError, setRefreshing } = authSlice.actions;
export default authSlice.reducer;
