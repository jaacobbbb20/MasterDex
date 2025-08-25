import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// -------------------- THUNKS --------------------

// Fetch all comments for a binder
export const fetchComments = createAsyncThunk(
  "comments/fetchComments",
  async (binderId) => {
    const res = await fetch(`/api/binders/${binderId}/comments`);
    if (!res.ok) throw new Error("Failed to fetch comments");
    return await res.json(); // backend returns an array of comments
  }
);

// Create a comment on a binder
export const createComment = createAsyncThunk(
  "comments/createComment",
  async ({ binderId, content }) => {
    const res = await fetch(`/api/binders/${binderId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
      credentials: "include",
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.errors?.message || "Failed to create comment");
    }
    return await res.json(); // returns the new comment
  }
);

// Update a comment
export const updateComment = createAsyncThunk(
  "comments/updateComment",
  async ({ commentId, content }) => {
    const res = await fetch(`/api/comments/${commentId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
      credentials: "include",
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.errors?.message || "Failed to update comment");
    }
    return await res.json(); // updated comment
  }
);

// Delete a comment
export const deleteComment = createAsyncThunk(
  "comments/deleteComment",
  async (commentId) => {
    const res = await fetch(`/api/comments/${commentId}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.errors?.message || "Failed to delete comment");
    }
    return commentId;
  }
);

// -------------------- SLICE --------------------
const commentsSlice = createSlice({
  name: "comments",
  initialState: {
    byId: {}, // { [id]: comment }
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchComments.fulfilled, (state, action) => {
        const comments = action.payload;
        state.byId = {};
        comments.forEach((c) => {
          state.byId[c.id] = c;
        });
      })
      .addCase(createComment.fulfilled, (state, action) => {
        const comment = action.payload;
        state.byId[comment.id] = comment;
      })
      .addCase(updateComment.fulfilled, (state, action) => {
        const comment = action.payload;
        state.byId[comment.id] = comment;
      })
      .addCase(deleteComment.fulfilled, (state, action) => {
        delete state.byId[action.payload];
      });
  },
});

export default commentsSlice.reducer;