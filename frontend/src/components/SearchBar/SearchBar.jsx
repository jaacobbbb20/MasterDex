import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FiSearch } from "react-icons/fi";
import "./SearchBar.css";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    const s = query.trim();
    if (s) navigate(`/search?q=${encodeURIComponent(s)}`);
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <FiSearch className="search-icon" aria-hidden />
      <input
        type="text"
        placeholder="Binders, Cards, Users..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search"
      />
      <button type="submit">Search</button>
    </form>
  );
}
