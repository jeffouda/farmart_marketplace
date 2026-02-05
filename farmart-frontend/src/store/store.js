import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import livestockReducer from '../features/livestock/livestockSlice';
import buyerReducer from '../features/buyer/buyerSlice';
import cartReducer from '../features/checkout/cartSlice';
import disputeReducer from '../features/disputes/disputeSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    livestock: livestockReducer,
    buyer: buyerReducer,
    cart: cartReducer,
    disputes: disputeReducer,
  },
});

export default store;
