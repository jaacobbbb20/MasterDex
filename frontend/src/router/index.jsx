import { createBrowserRouter } from "react-router-dom";
import Layout from "./Layout";
import LandingPage from "../components/LandingPage";
import ProfilePage from "../components/ProfilePage";
import ViewBinderPage from "../components/ViewBinderPage";
import SearchResultsPage from "../components/SearchResultPage/SearchResultPage";

export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <LandingPage /> },
      { path: "profiles/:profileId", element: <ProfilePage /> },
      { path: "users/:username", element: <ProfilePage /> },
      { path: "binders/:binderId", element: <ViewBinderPage /> },
      { path: "/search", element: <SearchResultsPage />},
      { path: "*", element: <h2>Page Not Found</h2> },
    ],
  },
]);
