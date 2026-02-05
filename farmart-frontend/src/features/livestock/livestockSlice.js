import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunk for fetching livestock
export const fetchLivestock = createAsyncThunk(
  'livestock/fetchLivestock',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/livestock');
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch livestock');
    }
  }
);

// Async thunk for creating livestock
export const createLivestock = createAsyncThunk(
  'livestock/createLivestock',
  async (livestockData, { rejectWithValue }) => {
    try {
      const response = await api.post('/v1/farmer/livestock', livestockData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to create livestock');
    }
  }
);

const initialState = {
  items: [],
  status: 'idle',
  error: null,
  filters: {},
  total: 0,
  loading: false,
};

const livestockSlice = createSlice({
  name: 'livestock',
  initialState,
  reducers: {
    addLivestock: (state, action) => {
      state.items.push(action.payload);
    },
    removeLivestock: (state, action) => {
      state.items = state.items.filter(item => item.id !== action.payload);
    },
    updateLivestock: (state, action) => {
      const index = state.items.findIndex(item => item.id === action.payload.id);
      if (index >= 0) {
        state.items[index] = action.payload;
      }
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch livestock
      .addCase(fetchLivestock.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchLivestock.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchLivestock.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      // Create livestock
      .addCase(createLivestock.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createLivestock.fulfilled, (state, action) => {
        state.loading = false;
        state.items.push(action.payload);
      })
      .addCase(createLivestock.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { addLivestock, removeLivestock, updateLivestock, setFilters } = livestockSlice.actions;
export default livestockSlice.reducer;
