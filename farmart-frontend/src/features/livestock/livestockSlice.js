import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

export const fetchAnimals = createAsyncThunk(
  "livestock/fetchAnimals",
  async (filters) => {
    // Converts filters into URL params: ?type=goat&location=kiambu
    const response = await axios.get("/api/animals", { params: filters });
    return response.data;
  },
);

const livestockSlice = createSlice({
  name: "livestock",
  initialState: { items: [], status: "idle", error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchAnimals.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchAnimals.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload;
      })
      .addCase(fetchAnimals.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export default livestockSlice.reducer;
