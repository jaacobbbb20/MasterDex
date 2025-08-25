import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

export const fetchSets = createAsyncThunk("sets/fetch", async () => {
  const res = await fetch("/api/sets");
  const data = await res.json();
  if (!res.ok) throw data;
  return data.sets;
});

const setsSlice = createSlice({
  name: "sets",
  initialState: { all: [], status: "idle", error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchSets.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchSets.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.all = action.payload;
      })
      .addCase(fetchSets.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export default setsSlice.reducer;
