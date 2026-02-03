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

// Utility for robust error extraction
const extractErrorMessage = (error) => {
  if (!error.response?.data) {
    return error.message || 'An error occurred';
  }
  const data = error.response.data;
  // Check for 'error' key (backend standard) or 'message' key
  return data.error || data.message || data.detail || 'An error occurred';
};

// Async thunks
export const login = createAsyncThunk('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    const response = await api.post('/auth/login', credentials);
    
    // Safety check - fetch returns JSON directly, not wrapped in .data
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
});

export const register = createAsyncThunk('auth/register', async (userData, { rejectWithValue }) => {
  try {
    const response = await api.post('/auth/register', userData);
    return response;
  } catch (error) {
    return rejectWithValue(extractErrorMessage(error));
  }
});

export const getProfile = createAsyncThunk('auth/profile', async (_, { rejectWithValue }) => {
  try {
    const response = await api.get('/auth/me');
    return response;
  } catch (error) {
    return rejectWithValue(extractErrorMessage(error));
  }
});

// Initial state - production ready
const initialState = {
  user: null,
  isAuthenticated: false,
  token: localStorage.getItem('token') || null,
  loading: false,
  error: null,
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
      localStorage.removeItem('token');
    },
    clearError: (state) => {
      state.error = null;
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
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
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
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
