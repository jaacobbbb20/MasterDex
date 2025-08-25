import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// -------------------- THUNKS --------------------

// Search cards from Pokémon TCG API through backend
export const searchCards = createAsyncThunk(
  "cards/searchCards",
  async ({ query, page = 1, pageSize = 20 }) => {
    const res = await fetch(
      `/api/cards/search?q=${encodeURIComponent(query)}&page=${page}&pageSize=${pageSize}`
    );
    if (!res.ok) throw new Error("Failed to fetch cards");
    const data = await res.json(); // comes straight from TCG API
    return data; // { data: [...], page, pageSize, count, totalCount }
  }
);

// -------------------- SLICE --------------------
const cardsSlice = createSlice({
  name: "cards",
  initialState: {
    searchResults: [],   // last search's cards
    single: null,        // one card details if needed
    pagination: {},      // { page, pageSize, count, totalCount }
    status: "idle",      // "idle" | "loading" | "succeeded" | "failed"
    error: null,
  },
  reducers: {
    setSingleCard(state, action) {
      state.single = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(searchCards.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(searchCards.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.searchResults = action.payload.data;
        state.pagination = {
          page: action.payload.page,
          pageSize: action.payload.pageSize,
          count: action.payload.count,
          totalCount: action.payload.totalCount,
        };
      })
      .addCase(searchCards.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export const { setSingleCard } = cardsSlice.actions;
export default cardsSlice.reducer;