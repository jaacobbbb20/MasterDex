import { useEffect, useState, useMemo, useCallback } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate, useParams } from "react-router-dom";
import { FaUserCircle } from "react-icons/fa";
import { thunkAuthenticate } from "../../redux/session";
import FollowsModal from "../FollowsModal/FollowsModal";
import "./ProfilePage.css";

function getCSRFToken() {
  const c = document.cookie.split("; ").find((x) => x.startsWith("csrf_token="));
  return c ? c.split("=")[1] : null;
}

/* ---------- Helpers ---------- */
const getOwnedCount = (binder) => {
  if (typeof binder?.ownedCount === "number") return binder.ownedCount;
  if (typeof binder?.totalOwned === "number") return binder.totalOwned;
  if (Array.isArray(binder?.binder_cards)) {
    return binder.binder_cards.filter((bc) => bc?.owned).length;
  }
  if (Array.isArray(binder?.cards)) {
    return binder.cards.filter((c) => c?.owned || c?.collected).length;
  }
  return 0;
};

const getTotalInSet = (binder) => {
  if (typeof binder?.totalSetCards === "number") return binder.totalSetCards;
  if (typeof binder?.cardsTotal === "number") return binder.cardsTotal;
  if (typeof binder?.setTotal === "number") return binder.setTotal;
  if (Array.isArray(binder?.cards)) return Math.max(binder.cards.length, 1);
  return 1;
};

function normalizeUser(u) {
  return {
    id: u.id,
    username: u.username,
    firstName: u.firstName ?? u.first_name ?? "",
    lastName: u.lastName ?? u.last_name ?? "",
    bio: u.bio ?? "",
    profileImage: u.profileImage ?? u.profile_image ?? null,
    createdAt: u.createdAt ?? u.created_at ?? null,
    followersCount: u.followersCount ?? u.followers_count ?? 0,
    followingCount: u.followingCount ?? u.following_count ?? 0,
    isFollowing: !!(u.isFollowing ?? u.is_following),
  };
}

export default function ProfilePage() {
  const navigate = useNavigate();
  const { username: routeUsername } = useParams();
  const sessionUser = useSelector((state) => state.session.user);
  const dispatch = useDispatch();

  const isViewingOther =
    !!routeUsername &&
    routeUsername.toLowerCase() !== (sessionUser?.username || "").toLowerCase();

  // ---- State (declare all hooks before any early returns) ----
  const [profileUser, setProfileUser] = useState(null);
  const [binders, setBinders] = useState([]);
  const [loadingBinders, setLoadingBinders] = useState(true);

  const [showFollows, setShowFollows] = useState(false);
  const [followsTab, setFollowsTab] = useState("followers");

  const [loadingProfile, setLoadingProfile] = useState(false);
  const [profileError, setProfileError] = useState("");

  const [followBusy, setFollowBusy] = useState(false);

  /* ---------- Load profile user ---------- */
  useEffect(() => {
    let cancelled = false;

    (async () => {
      setProfileError("");
      setLoadingProfile(true);

      if (!isViewingOther) {
        if (!cancelled) {
          setProfileUser(sessionUser || null);
          setLoadingProfile(false);
        }
        return;
      }

      try {
        const res = await fetch(
          `/api/users/by-username/${encodeURIComponent(routeUsername)}`,
          { credentials: "include", headers: { "Cache-Control": "no-store" } }
        );
        const raw = await res.text();
        let data = {};
        try { data = JSON.parse(raw); } catch {/*ignore*/}

        if (!res.ok) {
          throw new Error(data?.errors?.message || `${res.status} ${res.statusText}`);
        }

        const u = data.user || data;
        if (!cancelled) setProfileUser(normalizeUser(u));
      } catch (e) {
        if (!cancelled) {
          console.error("Failed to load user:", e);
          setProfileUser(null);
          setProfileError(String(e.message || e));
        }
      } finally {
        if (!cancelled) setLoadingProfile(false);
      }
    })();

    return () => { cancelled = true; };
  }, [isViewingOther, routeUsername, sessionUser]);

  /* ---------- Load binders for the viewed user ---------- */
  useEffect(() => {
    let cancelled = false;

    (async () => {
      setLoadingBinders(true);
      try {
        if (!isViewingOther) {
          const res = await fetch("/api/binders", { credentials: "include" });
          if (!res.ok) throw new Error("Failed to fetch binders");
          const data = await res.json();
          if (!cancelled) setBinders(data.binders || []);
          return;
        }

        const res = await fetch(
          `/api/users/by-username/${encodeURIComponent(routeUsername)}/binders`,
          { credentials: "include" }
        );

        if (res.ok) {
          const data = await res.json();
          if (!cancelled) setBinders(data.binders || data || []);
        } else {
          if (!cancelled) setBinders([]);
        }
      } catch (err) {
        console.error(err);
        if (!cancelled) setBinders([]);
      } finally {
        if (!cancelled) setLoadingBinders(false);
      }
    })();

    return () => { cancelled = true; };
  }, [isViewingOther, routeUsername]);

  const totalCards = useMemo(
    () => (Array.isArray(binders) ? binders.reduce((sum, b) => sum + getOwnedCount(b), 0) : 0),
    [binders]
  );

  const refetchViewedUser = useCallback(async () => {
    if (!isViewingOther || !routeUsername) return;
    const res = await fetch(
      `/api/users/by-username/${encodeURIComponent(routeUsername)}`,
      { credentials: "include", headers: { "Cache-Control": "no-store" } }
    );
    const raw = await res.text();
    let data = {};
    try { data = raw ? JSON.parse(raw) : {}; } catch {/* Ignore */}
    if (res.ok && (data.user || data)) {
      setProfileUser(normalizeUser(data.user || data));
    }
  }, [isViewingOther, routeUsername]);

  const toggleFollow = useCallback(async () => {
    if (!isViewingOther || !profileUser || followBusy) return;

    const wantFollow = !profileUser.isFollowing;
    setFollowBusy(true);

    try {
      const res = await fetch(`/api/follows/${profileUser.id}`, {
        method: wantFollow ? "POST" : "DELETE",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
          "Cache-Control": "no-store",
        },
      });

      const raw = await res.text().catch(() => "");
      if (!res.ok) {
        console.error("Follow API error:", res.status, raw);
        return;
      }

      await refetchViewedUser();

      dispatch(thunkAuthenticate());
    } catch (e) {
      console.error("Follow toggle failed:", e);
    } finally {
      setFollowBusy(false);
    }
  }, [dispatch, followBusy, isViewingOther, profileUser, refetchViewedUser]);

  if (loadingProfile) {
    return (
      <div className="profile-container">
        <div className="profile-page">
          <p>Loading profile…</p>
        </div>
      </div>
    );
  }

  if (profileError) {
    return (
      <div className="profile-container">
        <div className="profile-page">
          <p className="error">Unable to load profile: {profileError}</p>
          <button className="btn" onClick={() => navigate(-1)}>Go Back</button>
        </div>
      </div>
    );
  }

  if (!profileUser) {
    if (!isViewingOther) return <p>Please log in to view your profile.</p>;
    return (
      <div className="profile-container">
        <div className="profile-page">
          <p>User not found.</p>
          <button className="btn" onClick={() => navigate(-1)}>Go Back</button>
        </div>
      </div>
    );
  }

  const {
    firstName,
    lastName,
    username,
    createdAt,
    bio,
    profileImage,
  } = profileUser;

  const followersDisplay = profileUser.followersCount ?? 0;
  const followingDisplay = profileUser.followingCount ?? 0;

  const goToBinder = (binderId) => navigate(`/binders/${binderId}`);

  return (
    <div className="profile-container">
      <div className="profile-page">
        {/* Top Profile Info Card */}
        <div className="profile-info-card">
          {/* Left side: avatar + names */}
          <div className="profile-left">
            <div className="profile-avatar">
              {profileImage ? (
                <img
                  src={profileImage}
                  alt={`${firstName || ""} ${lastName || ""}`}
                  style={{ width: 80, height: 80, borderRadius: "50%", objectFit: "cover" }}
                />
              ) : (
                <FaUserCircle size={80} color="#888" />
              )}
            </div>
            <div className="profile-names">
              <h2>
                {firstName} {lastName}
              </h2>
              <p className="username">@{username}</p>
              {createdAt && (
                <p className="member-since">
                  Member since{" "}
                  {new Date(createdAt).toLocaleDateString("en-US", {
                    month: "long",
                    year: "numeric",
                  })}
                </p>
              )}
            </div>
          </div>

          {/* Right side: stats + actions */}
          <div className="profile-stats">
            <button
              type="button"
              className="stat"
              onClick={() => {
                setFollowsTab("followers");
                setShowFollows(true);
              }}
              aria-label="View followers"
            >
              <h3>{followersDisplay}</h3>
              <p>Followers</p>
            </button>

            <button
              type="button"
              className="stat"
              onClick={() => {
                setFollowsTab("following");
                setShowFollows(true);
              }}
              aria-label="View following"
            >
              <h3>{followingDisplay}</h3>
              <p>Following</p>
            </button>

            <div className="stat">
              <h3>{totalCards}</h3>
              <p>Total Cards</p>
              {loadingBinders && <small style={{ opacity: 0.7 }}>loading…</small>}
            </div>

            {isViewingOther && (
              <button
                type="button"
                className={`follow-btn ${profileUser.isFollowing ? "unfollow" : "follow"}`}
                onClick={toggleFollow}
                disabled={followBusy}
                aria-busy={followBusy ? "true" : "false"}
              >
                {profileUser.isFollowing ? "Unfollow" : "Follow"}
              </button>
            )}
          </div>
        </div>

        {/* Bio */}
        {bio && <p className="profile-bio">&quot;{bio}&quot;</p>}

        <hr className="divider" />

        {/* Binders Grid */}
        {binders.length > 0 && (
          <div className="binders-grid">
            {binders.map((binder) => {
              const owned = getOwnedCount(binder);
              const total = getTotalInSet(binder);
              const progress = Math.round((owned / total) * 100);

              return (
                <div
                  key={binder.id}
                  className="binder-card"
                  onClick={() => goToBinder(binder.id)}
                >
                  <img
                    src={binder.setImage || "/default-set.png"}
                    alt={binder.setName || "Binder Set"}
                  />
                  <div className="binder-banner">
                    <span className="binder-name">{binder.setName || binder.name}</span>
                    <span className="binder-progress">{progress}% Complete</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
        {binders.length === 0 && !loadingBinders && isViewingOther && (
          <p style={{ opacity: 0.8 }}>This user has no public binders (or they’re hidden).</p>
        )}
      </div>

      {/* Followers/Following Modal */}
      {showFollows && profileUser?.id && (
        <FollowsModal
          key={followsTab}
          isOpen={showFollows}
          onClose={() => setShowFollows(false)}
          userId={profileUser.id}
          initialTab={followsTab}
          onCountsChange={({ followers, following }) => {
            setProfileUser((u) =>
              u ? { ...u, followersCount: followers, followingCount: following } : u
            );
          }}
        />
      )}
    </div>
  );
}
