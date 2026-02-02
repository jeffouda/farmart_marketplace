import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk for fetching livestock
export const fetchLivestock = createAsyncThunk(
  'livestock/fetchLivestock',
  async (_, { rejectWithValue }) => {
    try {
      // Mock API call - replace with actual API
      const response = await fetch('/api/livestock');
      if (!response.ok) {
        throw new Error('Failed to fetch livestock');
      }
      return await response.json();
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  items: [],
  status: 'idle',
  error: null,
  filters: {},
  total: 0,
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
      });
  },
});

export const { addLivestock, removeLivestock, updateLivestock, setFilters } = livestockSlice.actions;
export default livestockSlice.reducer;
