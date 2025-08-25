import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import "./FollowsModal.css";

export default function FollowsModal({
  isOpen,
  onClose,
  userId,
  initialTab = "followers",
  onCountsChange,
}) {
  const [tab, setTab] = useState(initialTab);
  const [lists, setLists] = useState({ followers: [], following: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => setTab(initialTab), [initialTab]);

  useEffect(() => {
    if (!isOpen) return; 

    let cancelled = false;
    setError("");
    setLoading(true);

    const fetchJson = async (path) => {
      const res = await fetch(path, { credentials: "include" });
      const data = await res.json().catch(() => ({}));
      return res.ok ? data : {};
    };

    (async () => {
      try {
        const [f1, f2] = await Promise.all([
          fetchJson(`/api/follows/${userId}/followers`),
          fetchJson(`/api/follows/${userId}/following`),
        ]);
        if (!cancelled) {
          setLists({
            followers: Array.isArray(f1.followers) ? f1.followers : [],
            following: Array.isArray(f2.following) ? f2.following : [],
          });
        }
      } catch {
        if (!cancelled) setError("Failed to load follow data.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [isOpen, userId]);

  useEffect(() => {
    if (typeof onCountsChange === "function") {
      onCountsChange({
        followers: lists.followers.length,
        following: lists.following.length,
      });
    }
  }, [lists, onCountsChange]);

  const activeList = useMemo(() => {
    return tab === "followers" ? lists.followers : lists.following;
  }, [tab, lists]);

  const initials = (u) => {
    const fn = u.firstName || u.first_name || "";
    const ln = u.lastName || u.last_name || "";
    const i = `${fn.charAt(0)}${ln.charAt(0)}`.toUpperCase();
    return i || "@";
  };

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Tabs */}
        <div className="tab-navigation">
          <button
            type="button"
            className={`tab-button ${tab === "followers" ? "active" : ""}`}
            onClick={() => setTab("followers")}
          >
            Followers ({lists.followers.length})
          </button>
          <button
            type="button"
            className={`tab-button ${tab === "following" ? "active" : ""}`}
            onClick={() => setTab("following")}
          >
            Following ({lists.following.length})
          </button>
        </div>

        {/* Body */}
        <div className="modal-body">
          {error && <div className="error">{error}</div>}
          {loading && <div className="loading">Loading…</div>}

          {!loading && activeList.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">🫥</div>
              {tab === "followers" ? "No followers yet." : "Not following anyone yet."}
            </div>
          )}

          {!loading && activeList.length > 0 && (
            <ul>
              {activeList.map((u) => (
                <li key={u.id} className="user-item">
                  <Link
                    to={`/users/${u.username}`}
                    className="user-info"
                    onClick={onClose}
                  >
                    <div className="user-avatar">
                      {u.profileImage ? (
                        <img
                          src={u.profileImage}
                          alt=""
                          className="user-avatar-img"
                          loading="lazy"
                        />
                      ) : (
                        initials(u)
                      )}
                    </div>
                    <div className="user-details">
                      <div className="username">@{u.username}</div>
                      <div className="name">
                        {(u.firstName || u.first_name) || ""}{" "}
                        {(u.lastName || u.last_name) || ""}
                      </div>
                    </div>
                  </Link>

                  {/* Reserved for future follow/unfollow actions */}
                  <div className="user-actions" />
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
