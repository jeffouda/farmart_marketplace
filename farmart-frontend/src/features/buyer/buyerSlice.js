import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// Async thunk for fetching buyer orders
export const fetchOrders = createAsyncThunk(
  'buyer/fetchOrders',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/v1/buyer/orders');
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch orders');
    }
  }
);

// Async thunk for fetching buyer wishlist
export const fetchWishlist = createAsyncThunk(
  'buyer/fetchWishlist',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/v1/buyer/wishlist');
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch wishlist');
    }
  }
);

// Async thunk for adding to wishlist
export const addToWishlist = createAsyncThunk(
  'buyer/addToWishlist',
  async (livestockId, { rejectWithValue }) => {
    try {
      const response = await api.post(`/v1/buyer/wishlist/${livestockId}`);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to add to wishlist');
    }
  }
);

// Async thunk for removing from wishlist
export const removeFromWishlist = createAsyncThunk(
  'buyer/removeFromWishlist',
  async (livestockId, { rejectWithValue }) => {
    try {
      await api.delete(`/v1/buyer/wishlist/${livestockId}`);
      return livestockId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to remove from wishlist');
    }
  }
);

// Async thunk for fetching buyer profile
export const fetchBuyerProfile = createAsyncThunk(
  'buyer/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/v1/buyer/profile');
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to fetch profile');
    }
  }
);

// Async thunk for updating buyer profile
export const updateBuyerProfile = createAsyncThunk(
  'buyer/updateProfile',
  async (profileData, { rejectWithValue }) => {
    try {
      const response = await api.put('/v1/buyer/profile', profileData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || 'Failed to update profile');
    }
  }
);

const initialState = {
  orders: [],
  wishlist: [],
  profile: null,
  ordersStatus: 'idle',
  wishlistStatus: 'idle',
  profileStatus: 'idle',
  ordersError: null,
  wishlistError: null,
  profileError: null,
};

const buyerSlice = createSlice({
  name: 'buyer',
  initialState,
  reducers: {
    clearBuyerErrors: (state) => {
      state.ordersError = null;
      state.wishlistError = null;
      state.profileError = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Orders
      .addCase(fetchOrders.pending, (state) => {
        state.ordersStatus = 'loading';
        state.ordersError = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.ordersStatus = 'succeeded';
        state.orders = action.payload;
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.ordersStatus = 'failed';
        state.ordersError = action.payload;
      })
      // Wishlist
      .addCase(fetchWishlist.pending, (state) => {
        state.wishlistStatus = 'loading';
        state.wishlistError = null;
      })
      .addCase(fetchWishlist.fulfilled, (state, action) => {
        state.wishlistStatus = 'succeeded';
        state.wishlist = action.payload;
      })
      .addCase(fetchWishlist.rejected, (state, action) => {
        state.wishlistStatus = 'failed';
        state.wishlistError = action.payload;
      })
      // Add to wishlist
      .addCase(addToWishlist.fulfilled, (state, action) => {
        state.wishlist.push(action.payload);
      })
      // Remove from wishlist
      .addCase(removeFromWishlist.fulfilled, (state, action) => {
        state.wishlist = state.wishlist.filter(item => item.id !== action.payload);
      })
      // Profile
      .addCase(fetchBuyerProfile.pending, (state) => {
        state.profileStatus = 'loading';
        state.profileError = null;
      })
      .addCase(fetchBuyerProfile.fulfilled, (state, action) => {
        state.profileStatus = 'succeeded';
        state.profile = action.payload;
      })
      .addCase(fetchBuyerProfile.rejected, (state, action) => {
        state.profileStatus = 'failed';
        state.profileError = action.payload;
      })
      .addCase(updateBuyerProfile.fulfilled, (state, action) => {
        state.profile = action.payload;
      });
  },
});

export const { clearBuyerErrors } = buyerSlice.actions;
export default buyerSlice.reducer;
