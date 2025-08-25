import { useEffect, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import "./SearchResultPage.css";

/* -------- helpers -------- */
function useQuery() {
  const { search } = useLocation();
  return new URLSearchParams(search);
}

// Extract first integer from "23a" / "TG23" / "23/165" → 23
function parseCardNumber(num) {
  const s = String(num ?? "").trim();
  const m = /(\d+)/.exec(s);
  return m ? parseInt(m[1], 10) : NaN;
}

// Prefer server image; else build from set+number
function imageUrlForCard(card) {
  const img =
    card?.images?.large ||
    card?.images?.small ||
    card?.image ||
    null;

  if (img) return { primary: img, fallback: null };

  const setId = card?.set_id || card?.setId || card?.set?.id || null;
  const n = parseCardNumber(card?.number);
  if (!setId || Number.isNaN(n)) return { primary: "/default-card.png", fallback: null };

  const base = `https://images.pokemontcg.io/${setId}/${n}`;
  return { primary: `${base}_hires.png`, fallback: `${base}.png` };
}

export default function SearchResultsPage() {
  const q = (useQuery().get("q") || "").trim();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({ binders: [], cards: [], users: [] });

  useEffect(() => {
    if (!q) {
      setData({ binders: [], cards: [], users: [] });
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`, {
          credentials: "include",
        });
        const j = await res.json();
        if (!cancelled) setData(j || { binders: [], cards: [], users: [] });
      } catch {
        if (!cancelled) setData({ binders: [], cards: [], users: [] });
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [q]);

  return (
    <div className="search-page container">
      <h1>Search: “{q}”</h1>
      {loading && <p>Loading…</p>}

      {/* BINDERS */}
      <div className="sr-section">
        <h2>
          Binders <span className="count-badge">{data.binders.length}</span>
        </h2>
        <div className="grid">
          {data.binders.map((b) => (
            <Link key={b.id} className="card card-binder" to={`/binders/${b.id}`}>
              <img
                src={b.setImage || "/default-set.png"}
                alt={b.setName || b.name || "Binder"}
                loading="lazy"
              />
              <div className="title">{b.name}</div>
              <div className="sub">{b.setName || b.set_id || ""}</div>
            </Link>
          ))}
          {!loading && data.binders.length === 0 && (
            <div className="empty">No binders.</div>
          )}
        </div>
      </div>

      {/* CARDS */}
      <div className="sr-section">
        <h2>
          Cards <span className="count-badge">{data.cards.length}</span>
        </h2>
        <div className="grid">
          {data.cards.map((c) => {
            const { primary, fallback } = imageUrlForCard(c);
            const key = c.id || `${c.set_id || c.setId}-${c.number || ""}`;
            const subtitle = `${c.set_id || c.setId || (c.set && c.set.id) || ""}${
              c.number ? ` #${c.number}` : ""
            }`;
            const cardImgAlt =
              c.name ? `${c.name}${c.number ? ` #${c.number}` : ""}` : "Card";

            const cardThumb = (
              <div className="thumb-card">
                <img
                  src={primary}
                  alt={cardImgAlt}
                  loading="lazy"
                  onError={(e) => {
                    if (fallback && e.currentTarget.src !== fallback) {
                      e.currentTarget.src = fallback;
                    } else {
                      e.currentTarget.src = "/default-card.png";
                    }
                  }}
                />
              </div>
            );

            if (c.binderId) {
              const cardQuery = c.number ? `?card=${encodeURIComponent(c.number)}` : "";
              return (
                <Link
                  key={key}
                  className="card card-tcg"
                  to={`/binders/${c.binderId}${cardQuery}`}
                >
                  {cardThumb}
                  <div className="title">{c.name || "Unnamed card"}</div>
                  <div className="sub">{subtitle}</div>
                </Link>
              );
            }

            return (
              <div key={key} className="card card-tcg">
                {cardThumb}
                <div className="title">{c.name || "Unnamed card"}</div>
                <div className="sub">{subtitle}</div>
              </div>
            );
          })}
          {!loading && data.cards.length === 0 && (
            <div className="empty">No cards.</div>
          )}
        </div>
      </div>

      {/* USERS */}
      <div className="sr-section">
        <h2>
          Users <span className="count-badge">{data.users.length}</span>
        </h2>
        <div className="grid">
          {data.users.map((u) => (
            <Link key={u.id} className="card card-user" to={`/users/${u.username}`}>
              <img
                src={u.profileImage || "/default-avatar.png"}
                alt={u.username ? `@${u.username}` : "User"}
                loading="lazy"
              />
              <div className="title">@{u.username}</div>
              <div className="sub">
                {u.firstName} {u.lastName}
              </div>
            </Link>
          ))}
          {!loading && data.users.length === 0 && (
            <div className="empty">No users.</div>
          )}
        </div>
      </div>
    </div>
  );
}
