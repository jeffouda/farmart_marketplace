import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import livestockReducer from '../features/livestock/livestockSlice';
import cartReducer from '../features/checkout/cartSlice';
import disputeReducer from '../features/disputes/disputeSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    livestock: livestockReducer,
    cart: cartReducer,
    disputes: disputeReducer,
  },
});

export default store;
