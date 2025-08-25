import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

// -------------------- THUNKS --------------------

// Fetch a user's followers
export const fetchFollowers = createAsyncThunk(
  "follows/fetchFollowers",
  async (userId) => {
    const res = await fetch(`/api/follows/${userId}/followers`);
    if (!res.ok) throw new Error("Failed to load followers");
    const data = await res.json();
    return data.followers; // backend returns { followers: [...] }
  }
);

// Fetch who a user is following
export const fetchFollowing = createAsyncThunk(
  "follows/fetchFollowing",
  async (userId) => {
    const res = await fetch(`/api/follows/${userId}/following`);
    if (!res.ok) throw new Error("Failed to load following");
    const data = await res.json();
    return data.following; // backend returns { following: [...] }
  }
);

// Follow a user
export const followUser = createAsyncThunk(
  "follows/followUser",
  async (userId) => {
    const res = await fetch(`/api/follows/${userId}`, {
      method: "POST",
      credentials: "include",
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.errors?.message || "Failed to follow user");
    }
    const data = await res.json();
    return data.follow; // backend returns { follow: {...} }
  }
);

// Unfollow a user
export const unfollowUser = createAsyncThunk(
  "follows/unfollowUser",
  async (userId) => {
    const res = await fetch(`/api/follows/${userId}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.errors?.message || "Failed to unfollow user");
    }
    return userId; // just need to remove from state
  }
);

// -------------------- SLICE --------------------
const followsSlice = createSlice({
  name: "follows",
  initialState: {
    followers: [],
    following: [],
    status: "idle",
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      // Followers
      .addCase(fetchFollowers.fulfilled, (state, action) => {
        state.followers = action.payload;
      })
      // Following
      .addCase(fetchFollowing.fulfilled, (state, action) => {
        state.following = action.payload;
      })
      // Follow user
      .addCase(followUser.fulfilled, (state, action) => {
        // Push new following if not already there
        const newFollow = action.payload;
        if (!state.following.find((u) => u.id === newFollow.followingId)) {
          state.following.push({
            id: newFollow.followingId,
            followerId: newFollow.followerId,
          });
        }
      })
      // Unfollow user
      .addCase(unfollowUser.fulfilled, (state, action) => {
        state.following = state.following.filter(
          (u) => u.id !== action.payload
        );
      });
  },
});

export default followsSlice.reducer;