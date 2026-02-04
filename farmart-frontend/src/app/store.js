import { configureStore } from "@reduxjs/toolkit";
import livestockReducer from "../features/livestock/livestockSlice";

export const store = configureStore({
  reducer: {
    livestock: livestockReducer,
  },
});
