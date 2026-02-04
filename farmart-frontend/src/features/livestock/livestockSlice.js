import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

export const fetchLivestock = createAsyncThunk(
  "livestock/fetchLivestock",
  async (filters) => {
    // This sends your search criteria to the Flask backend
    const response = await axios.get("/api/animals", { params: filters });
    return response.data;
  },
);

const livestockSlice = createSlice({
  name: "livestock",
  initialState: { items: [], status: "idle" },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchLivestock.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchLivestock.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload;
      });
  },
});

export default livestockSlice.reducer;
