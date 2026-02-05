import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchDisputes = createAsyncThunk('disputes/fetchAll', async (_, { rejectWithValue }) => {
  try {
    const response = await api.get('/admin/disputes');
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data?.message || 'Failed to fetch disputes');
  }
});

export const createDispute = createAsyncThunk('disputes/create', async (data, { rejectWithValue }) => {
  try {
    const response = await api.post('/buyer/disputes', data);
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data?.message || 'Failed to create dispute');
  }
});

export const resolveDispute = createAsyncThunk('disputes/resolve', async ({ id, resolution }, { rejectWithValue }) => {
  try {
    const response = await api.put(`/admin/disputes/${id}/resolve`, { resolution });
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data?.message || 'Failed to resolve dispute');
  }
});

const initialState = {
  items: [],
  currentDispute: null,
  loading: false,
  error: null,
};

const disputeSlice = createSlice({
  name: 'disputes',
  initialState,
  reducers: {
    clearCurrentDispute: (state) => {
      state.currentDispute = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDisputes.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDisputes.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchDisputes.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(createDispute.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      })
      .addCase(resolveDispute.fulfilled, (state, action) => {
        const index = state.items.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      });
  },
});

export const { clearCurrentDispute, clearError } = disputeSlice.actions;
export default disputeSlice.reducer;
