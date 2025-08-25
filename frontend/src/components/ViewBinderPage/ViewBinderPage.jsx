import { useEffect, useMemo, useState, useCallback } from "react";
import { useSelector } from "react-redux";
import { useParams, useNavigate } from "react-router-dom";
import Comments from "../Comments/Comments";
import "./ViewBinderPage.css";

/* ---------------- Helpers ---------------- */

// Parse usable integer for pocket placement ("23/165" -> 23, "TG23" -> 23, "23a" -> 23)
function parseCardNumber(num) {
  const s = String(num ?? "").trim();
  return parseInt((/(\d+)/.exec(s) || [])[1], 10) || NaN;
}

// Small wrapper around fetch with consistent headers + error
async function apiFetch(path) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
  });
  if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
  return res.json();
}

function toNum(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function getCSRFToken() {
  const c = document.cookie.split("; ").find((x) => x.startsWith("csrf_token="));
  return c ? c.split("=")[1] : null;
}

/* ---------------- Constants ---------------- */

const PAGE_SIZE = 9;
const FALLBACK_SETS = {
  "151": "sv3pt5",
  "Scarlet & Violet": "sv1",
  "Paldea Evolved": "sv2",
  "Obsidian Flames": "sv3",
  "Paradox Rift": "sv4",
};

/* ---------------- Component ---------------- */

export default function ViewBinderPage() {
  const { binderId } = useParams();
  const navigate = useNavigate();
  const sessionUser = useSelector((s) => s.session.user);

  const [binder, setBinder] = useState(null);
  const [setMeta, setSetMeta] = useState(null);
  const [pageCards, setPageCards] = useState([]);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteErr, setDeleteErr] = useState("");

  /* ---- Load binder ---- */
  useEffect(() => {
    setLoading(true);
    apiFetch(`/api/binders/${binderId}`)
      .then((res) => setBinder(res.binder))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [binderId]);

  /* ---- Set ID ---- */
  const setId = useMemo(
    () => binder?.setId || FALLBACK_SETS[binder?.name] || null,
    [binder]
  );

  /* ---- Set metadata ---- */
  useEffect(() => {
    if (!setId) return;
    apiFetch(`/api/sets`)
      .then((j) => {
        const allSets = j.data || [];
        const match = allSets.find((s) => s.id === setId || s.alias === setId);
        setSetMeta(match || null);
      })
      .catch(() => setSetMeta(null));
  }, [setId]);

  /* ---- Totals ---- */
  const totalInSet =
    (setMeta?.total_in_set != null ? toNum(setMeta.total_in_set) : 0) ||
    (binder?.totalSetCards  != null ? toNum(binder.totalSetCards)  : 0) ||
    (binder?.cardsTotal     != null ? toNum(binder.cardsTotal)     : 0) ||
    (binder?.setTotal       != null ? toNum(binder.setTotal)       : 0) ||
    (Array.isArray(binder?.cards) ? Math.max(binder.cards.length, 0) : 0);

  const totalOwned =
    Array.isArray(binder?.cards) ? binder.cards.length :
    (binder?.ownedCount != null ? toNum(binder.ownedCount) : 0) ||
    (binder?.totalOwned != null ? toNum(binder.totalOwned) : 0);

  const progressPct =
    totalInSet > 0
      ? Math.min(100, Math.max(0, Math.round((totalOwned / totalInSet) * 100)))
      : 0;

  /* ---- Page cards ---- */
  useEffect(() => {
    if (!setId || !totalInSet) return;
    const start = (page - 1) * PAGE_SIZE + 1;
    const end = Math.min(totalInSet, start + PAGE_SIZE - 1);

    apiFetch(`/api/sets/${setId}/cards?start=${start}&end=${end}`)
      .then((j) => {
        const cards = (j.cards || []).map((c) => ({
          ...c,
          set: c.set || { id: setId },
        }));
        setPageCards(cards);
      })
      .catch(() => setPageCards([]));
  }, [setId, totalInSet, page]);

  useEffect(() => setPage(1), [query]);

  /* ---- Pockets ---- */
  const pockets = useMemo(() => {
    const map = new Map();
    pageCards.forEach((c) => {
      const n = parseCardNumber(c.number);
      if (!Number.isNaN(n)) map.set(n, c);
    });
    const start = (page - 1) * PAGE_SIZE + 1;
    return Array.from({ length: PAGE_SIZE }, (_, i) => {
      const slotNum = start + i;
      return map.get(slotNum) ?? { __empty: true, number: slotNum };
    });
  }, [pageCards, page]);

  /* ---- Navigation ---- */
  const totalPages = Math.ceil(totalInSet / PAGE_SIZE) || 1;
  const goPrev = useCallback(() => setPage((p) => Math.max(1, p - 1)), []);
  const goNext = useCallback(
    () => setPage((p) => Math.min(totalPages, p + 1)),
    [totalPages]
  );

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "ArrowLeft") goPrev();
      if (e.key === "ArrowRight") goNext();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [goPrev, goNext]);

  const isOwner =
    !!sessionUser &&
    !!binder &&
    (binder.userId ?? binder.user_id) === sessionUser.id;

  async function handleDeleteBinder() {
    setDeleting(true);
    setDeleteErr("");
    try {
      const res = await fetch(`/api/binders/${binder.id}`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
      });
      const text = await res.text();
      let data = {};
      try { data = text ? JSON.parse(text) : {}; } catch {/* Ignore */}
      if (!res.ok) throw new Error(data?.errors?.message || `${res.status} ${res.statusText}`);
      navigate(`/users/${sessionUser.username}`);
    } catch (e) {
      setDeleteErr(e.message || "Failed to delete binder");
    } finally {
      setDeleting(false);
    }
  }

  /* ---- Render ---- */
  if (loading) return <SkeletonBinderPage />;
  if (error || !binder) return <ErrorBox message={error} onBack={() => navigate(-1)} />;

  return (
    <div className="binder-page container">
      {/* Header */}
      <BinderHeader
        binder={binder}
        setMeta={setMeta}
        totalOwned={totalOwned}
        totalInSet={totalInSet}
        progressPct={progressPct}
      />

      {/* Toolbar */}
      <div className="binder-toolbar">
        <input
          type="text"
          placeholder="Feature Coming Soon..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="search-input"
        />
        <div className="toolbar-actions">
          <button className="btn btn-secondary" onClick={() => navigate(-1)}>
            Back
          </button>

          {isOwner ? (
            <button className="btn btn-danger" onClick={() => setConfirmOpen(true)}>
              Delete Binder
            </button>
          ) : (
            <button className="btn" disabled>Coming Soon</button>
          )}
        </div>
      </div>

      {/* Binder page */}
      <div className="binder-view">
        <button className="page-btn prev" onClick={goPrev} disabled={page === 1}>‹</button>
        <div className="binder-sheet">
          <div className="pocket-grid">
            {pockets.map((p, i) => {
              const setForPocket = p?.set?.id || setId || setMeta?.id;
              const pNum = parseCardNumber(p.number);

              // find the owned entry for THIS set + number
              const ownedCard = (binder.cards || []).find((c) => {
                const cNum = parseCardNumber(c.number);
                const cSet = c?.set?.id || setId || setMeta?.id;
                return cNum === pNum && cSet === setForPocket;
              });

              const stableKey = `${binder.id}-${setForPocket}-${pNum ?? i}`;

              return (
                <Pocket
                  key={stableKey}
                  card={{ ...p, ...(ownedCard || {}), owned: !!ownedCard }}
                  binderSetId={setForPocket}
                  binderId={binder.id}
                  onToggle={(updatedCard, ownedNow) => {
                    if (!updatedCard?.number) return;

                    setBinder((prev) => {
                      if (!prev) return prev;
                      const toNumLocal = (x) => parseCardNumber(x?.number);
                      const updatedNum = toNumLocal(updatedCard);
                      const updatedSet = updatedCard?.set?.id || setForPocket;

                      const clean = (prev.cards || []).filter((c) => c && c.number);

                      let next;
                      if (ownedNow) {
                        const already = clean.some(
                          (c) => toNumLocal(c) === updatedNum && (c?.set?.id || setForPocket) === updatedSet
                        );
                        next = already ? clean : [...clean, { ...updatedCard, owned: true }];
                      } else {
                        next = clean.filter(
                          (c) => !(toNumLocal(c) === updatedNum && (c?.set?.id || setForPocket) === updatedSet)
                        );
                      }
                      return { ...prev, cards: next };
                    });
                  }}
                />
              );
            })}
          </div>
        </div>
        <button className="page-btn next" onClick={goNext} disabled={page === totalPages}>›</button>
      </div>

      <div className="page-indicator">Page {page} / {totalPages}</div>

      {/* --- Comments section --- */}
      <div className="binder-comments-section">
        <Comments binderId={binder.id} ownerId={binder.userId ?? binder.user_id} />
      </div>

      {/* --- Delete confirm modal --- */}
      {confirmOpen && (
        <div
          className="confirm-overlay"
          onClick={() => !deleting && setConfirmOpen(false)}
          role="dialog"
          aria-modal="true"
        >
          <div className="confirm-content" onClick={(e) => e.stopPropagation()}>
            <h3>Delete binder?</h3>
            <p>This action cannot be undone.</p>
            {deleteErr && <p className="inline-error">{deleteErr}</p>}
            <div className="confirm-actions">
              <button className="btn" onClick={() => setConfirmOpen(false)} disabled={deleting}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={handleDeleteBinder} disabled={deleting}>
                {deleting ? "Deleting…" : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ---------------- Small Components ---------------- */

function SkeletonBinderPage() {
  return (
    <div className="binder-page container">
      <div className="skeleton-header" />
      <div className="skeleton-grid">
        {Array.from({ length: 9 }).map((_, i) => (
          <div key={i} className="skeleton-card" />
        ))}
      </div>
    </div>
  );
}

function ErrorBox({ message, onBack }) {
  return (
    <div className="binder-page container">
      <div className="error-box">
        <h2>Unable to load binder</h2>
        <p>{message || "Something went wrong."}</p>
        <button className="btn" onClick={onBack}>Go Back</button>
      </div>
    </div>
  );
}

function BinderHeader({ binder, setMeta, totalOwned, totalInSet, progressPct }) {
  return (
    <div className="binder-header">
      <div className="binder-title-area">
        {binder.setLogo && (
          <img className="set-logo" src={binder.setLogo} alt={binder.setName || "Set"} />
        )}
        <div className="titles">
          <h1 className="binder-name">{binder.name}</h1>
          {(binder.setName || setMeta?.name) && (
            <p className="binder-subtitle">{binder.setName || setMeta?.name}</p>
          )}
          {binder.description && <p className="binder-desc">{binder.description}</p>}
        </div>
      </div>
      <div className="binder-stats">
        <Stat label="Owned" value={totalOwned} />
        <Stat label="In Set" value={totalInSet} />
        <Stat label="Complete" value={`${progressPct}%`} />
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <div className="stat-number">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function Pocket({ card, binderSetId, binderId, onToggle }) {
  const [localOwned, setLocalOwned] = useState(!!card.owned);
  useEffect(() => { setLocalOwned(!!card.owned); }, [card.owned]);

  const n = parseCardNumber(card.number);
  const setForCard = card?.set?.id || binderSetId;
  const cdnBase =
    !Number.isNaN(n) && setForCard
      ? `https://images.pokemontcg.io/${setForCard}/${n}`
      : null;

  const primary =
    card.images?.large ||
    card.images?.small ||
    (cdnBase && `${cdnBase}_hires.png`);
  const fallback = cdnBase && `${cdnBase}.png`;

  const toggleOwned = useCallback(async () => {
    setLocalOwned((prev) => !prev);
    try {
      const res = await fetch(`/api/cards/${card.id}/toggle`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ binder_id: binderId }),
      });

      const raw = await res.text();
      let data;
      try { data = raw ? JSON.parse(raw) : {}; } catch { data = { _nonJson: raw }; }

      if (!res.ok) {
        setLocalOwned((prev) => !prev);
        return;
      }

      const owned = Boolean(data?.owned);
      const serverCard = data?.card ?? {};
      setLocalOwned(owned);
      onToggle({ ...card, ...serverCard, owned }, owned);
    } catch {
      setLocalOwned((prev) => !prev);
    }
  }, [binderId, card, onToggle]);

  if (card.__empty) {
    return (
      <div className="pocket empty" title={`#${card.number} (empty)`}>
        <div className="pocket-gloss" />
        <div className="empty-pocket-content">
          <div className="pokeball-dot" />
          <span>#{card.number}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`pocket filled ${localOwned ? "owned" : "unowned"}`} onClick={toggleOwned}>
      <div className="pocket-gloss" />
      <div className="card-in-pocket">
        {primary && (
          <img
            src={primary}
            alt={card.name}
            className={`card-image ${!localOwned ? "grayscale" : ""}`}
            loading="lazy"
            width={245}
            height={342}
            onError={(e) => {
              if (e.currentTarget.src !== fallback && fallback) {
                e.currentTarget.src = fallback;
              } else e.currentTarget.style.display = "none";
            }}
          />
        )}
        <div className="card-caption">
          <div className="card-name">{card.name}</div>
          <div className="card-meta">
            <span className="card-number">#{card.number}</span>
            {card.rarity && <span className="rarity-tag">{card.rarity}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}