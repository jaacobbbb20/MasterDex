import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// -------------------- THUNKS --------------------

// Get all binders for current user
export const fetchBinders = createAsyncThunk("binders/fetchAll", async () => {
  const res = await fetch("/api/binders");
  const data = await res.json();
  if (!res.ok) throw data;
  return data.binders;
});

// Get cards in a binder
export const fetchBinderCards = createAsyncThunk(
  "binders/fetchCards",
  async (binderId) => {
    const res = await fetch(`/api/binders/${binderId}/cards`);
    const data = await res.json();
    if (!res.ok) throw data;
    return { binderId, cards: data.cards };
  }
);

// Create a binder
export const createBinder = createAsyncThunk(
  "binders/create",
  async (binderData) => {
    const res = await fetch("/api/binders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(binderData),
    });
    const data = await res.json();
    if (!res.ok) throw data;
    return data.binder;
  }
);

// Add card to binder
export const addCardToBinder = createAsyncThunk(
  "binders/addCard",
  async ({ binderId, card }) => {
    const res = await fetch(`/api/binders/${binderId}/cards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ card }),
    });
    const data = await res.json();
    if (!res.ok) throw data;
    return { binderId, card: data.card };
  }
);

// Delete binder
export const deleteBinder = createAsyncThunk(
  "binders/delete",
  async (binderId) => {
    const res = await fetch(`/api/binders/${binderId}`, { method: "DELETE" });
    if (!res.ok) throw await res.json();
    return binderId;
  }
);

// -------------------- SLICE --------------------
const bindersSlice = createSlice({
  name: "binders",
  initialState: {
    all: {}, // normalized by binderId
    status: "idle", // idle | loading | succeeded | failed
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Fetch all
      .addCase(fetchBinders.fulfilled, (state, action) => {
        state.all = {};
        action.payload.forEach((binder) => {
          state.all[binder.id] = binder;
        });
        state.status = "succeeded";
      })
      // Fetch binder cards
      .addCase(fetchBinderCards.fulfilled, (state, action) => {
        const { binderId, cards } = action.payload;
        if (state.all[binderId]) {
          state.all[binderId].cards = cards;
        }
      })
      // Create binder
      .addCase(createBinder.fulfilled, (state, action) => {
        state.all[action.payload.id] = action.payload;
      })
      // Add card to binder
      .addCase(addCardToBinder.fulfilled, (state, action) => {
        const { binderId, card } = action.payload;
        if (state.all[binderId]) {
          if (!state.all[binderId].cards) state.all[binderId].cards = [];
          state.all[binderId].cards.push(card);
        }
      })
      // Delete binder
      .addCase(deleteBinder.fulfilled, (state, action) => {
        delete state.all[action.payload];
      })
      // Handle pending/errors
      .addMatcher(
        (action) => action.type.endsWith("/pending"),
        (state) => {
          state.status = "loading";
          state.error = null;
        }
      )
      .addMatcher(
        (action) => action.type.endsWith("/rejected"),
        (state, action) => {
          state.status = "failed";
          state.error = action.error?.message || "Something went wrong";
        }
      );
  },
});

export default bindersSlice.reducer;