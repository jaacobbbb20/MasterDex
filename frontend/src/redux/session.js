import { createSlice, createAsyncThunk } from "@reduxjs/toolkit"; 

// -------------------- 
// Helper: CSRF Token 
// -------------------- 

function getCSRFToken() { 
  const cookie = document.cookie 
  .split("; ") 
  .find((c) => c.startsWith("csrf_token=")); 
  return cookie ? cookie.split("=")[1] : null; 
} 

// -------------------- 
// Thunks 
// -------------------- 
export const thunkAuthenticate = createAsyncThunk( 
  "session/authenticate", 
  async (_, { rejectWithValue }) => { 
    try { 
      const res = await fetch("/api/auth/", { credentials: "include" }); 
      if (!res.ok) return rejectWithValue("Authentication failed"); 
      const data = await res.json(); 
      return data.user || data; 
    } catch (err) { 
      return rejectWithValue(err.message); 
    } 
  } 
); 

export const thunkLogin = createAsyncThunk( 
  "session/login", async (credentials, { rejectWithValue }) => { 
    try { 
      const res = await fetch("/api/auth/login", { 
        method: "POST", 
        headers: { 
          "Content-Type": "application/json", 
          "X-CSRFToken": getCSRFToken(), 
        }, 
        credentials: "include", 
        body: JSON.stringify(credentials), 
      }); 
      const data = await res.json(); 
      if (!res.ok) return rejectWithValue(data); 
      return data.user || data; 
    } catch (err) { 
      return rejectWithValue({ server: "An unexpected login error occurred." }); 
    } 
  } 
); 

export const thunkSignup = createAsyncThunk( 
  "session/signup", 
  async (userData, { rejectWithValue }) => { 
    try { 
      const res = await fetch("/api/auth/signup", { 
        method: "POST", 
        headers: { 
          "Content-Type": "application/json", 
          "X-CSRFToken": getCSRFToken(), 
        }, 
        credentials: "include", 
        body: JSON.stringify(userData), 
      }); 
      const data = await res.json(); 
      if (!res.ok) return rejectWithValue(data); 
      return data.user || data; 
    } catch (err) { 
      return rejectWithValue({ server: "An unexpected signup error occurred." });
     } 
    } 
  ); 
  
  
  export const thunkLogout = createAsyncThunk( 
    "session/logout", 
    async (_, { rejectWithValue }) => { 
      try { 
        const res = await fetch("/api/auth/logout", { 
          method: "POST", 
          headers: { "X-CSRFToken": getCSRFToken() }, 
          credentials: "include", 
        }); 
        if (!res.ok) return rejectWithValue("Logout failed"); 
        return null; // no user 
        } catch (err) { 
          return rejectWithValue(err.message); 
        } 
      } 
    ); 
    
// -------------------- 
// Slice 
// -------------------- 

const sessionSlice = createSlice({ 
  name: "session", 
  initialState: { user: null, isAuthenticated: false, error: null }, 
  reducers: {}, 
  extraReducers: (builder) => { 
    builder .addCase(thunkAuthenticate.fulfilled, (state, action) => { 
      state.user = action.payload; 
      state.isAuthenticated = true; 
    }) 
    .addCase(thunkLogin.fulfilled, (state, action) => { 
      state.user = action.payload; 
      state.isAuthenticated = true; 
    }) 
    .addCase(thunkSignup.fulfilled, (state, action) => { 
      state.user = action.payload; 
      state.isAuthenticated = true; 
    }) 
    .addCase(thunkLogout.fulfilled, (state) => { 
      state.user = null; state.isAuthenticated = false; 
    }) 
    .addMatcher( 
      (action) => action.type.endsWith("/rejected"), 
      (state, action) => { 
        state.error = action.payload || "Something went wrong"; 
      } 
    ); 
  }, 
});

// -------------------- 
// Export Reducer 
// -------------------- 

export default sessionSlice.reducer;