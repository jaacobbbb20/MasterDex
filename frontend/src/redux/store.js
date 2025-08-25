import { configureStore } from "@reduxjs/toolkit";
import sessionReducer from "./session";
import cardsReducer from "./cards";
import bindersReducer from "./binders";
import followsReducer from "./follows";
import commentsReducer from "./comments";

let logger;
if (import.meta.env.MODE !== "production") {
  const mod = await import("redux-logger");
  logger = mod.default;
}

const store = configureStore({
  reducer: {
    session: sessionReducer,
    cards: cardsReducer,
    binders: bindersReducer,
    follows: followsReducer,
    comments: commentsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    import.meta.env.MODE === "production"
      ? getDefaultMiddleware()
      : getDefaultMiddleware().concat(logger),
  devTools: import.meta.env.MODE !== "production",
});

export default store;