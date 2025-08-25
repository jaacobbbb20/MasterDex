import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import "./Comments.css";

/*----------------------------------*/
/*     Helper for JSON Requests     */
/*----------------------------------*/
async function api(url, options = {}) {
  const res = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, data };
}

export default function Comments({ binderId, ownerId }) {
  const sessionUser = useSelector((s) => s.session.user);

  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  /* Add Comment UI */
  const [showForm, setShowForm] = useState(false);
  const [posting, setPosting] = useState(false);
  const [newContent, setNewContent] = useState("");
  const [postError, setPostError] = useState("");

  /* Edit Comment UI */
  const [editingId, setEditingId] = useState(null);
  const [editContent, setEditContent] = useState("");

  /* Load comments */
  useEffect(() => {
    (async () => {
      setLoading(true);
      setError("");
      const { ok, data } = await api(`/api/binders/${binderId}/comments`);
      if (ok) {
        setComments(Array.isArray(data) ? data : data.comments || []);
      } else {
        setError(data.errors?.message || "Failed to load comments");
      }
      setLoading(false);
    })();
  }, [binderId]);

  /* Create a Comment */
  async function handleAdd(e) {
    e.preventDefault();
    const content = newContent.trim();
    if (!content || posting) return;

    setPosting(true);
    setPostError("");
    const { ok, data } = await api(`/api/binders/${binderId}/comments`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });

    if (ok) {
      setComments([data, ...comments]);
      setNewContent("");
      setShowForm(false);
    } else {
      setPostError(data.errors?.message || "Could not add comment");
    }
    setPosting(false);
  }

  /* Update a Comment */
  async function handleUpdate(id) {
    const content = editContent.trim();
    if (!content) return;

    const { ok, data } = await api(`/api/comments/${id}`, {
      method: "PUT",
      body: JSON.stringify({ content }),
    });

    if (ok) {
      setComments((list) => list.map((c) => (c.id === id ? data : c)));
      setEditingId(null);
      setEditContent("");
    } else {
      alert(data.errors?.message || "Could not update comment");
    }
  }

  /* Delete a Comment */
  async function handleDelete(id) {
    if (!window.confirm("Delete this comment?")) return;
    const { ok, data } = await api(`/api/comments/${id}`, { method: "DELETE" });
    if (ok) {
      setComments((list) => list.filter((c) => c.id !== id));
    } else {
      alert(data.errors?.message || "Could not delete comment");
    }
  }

  if (loading) return <p>Loading comments…</p>;
  if (error) return <p className="error">{error}</p>;

  const canComment = !!sessionUser && sessionUser.id !== ownerId;
  const disablePost = posting || newContent.trim().length === 0;

  return (
    <div className="comments-section">
      {/* Header row: title + button */}
      <div className="comments-header-row">
        <h3 className="comments-title">Comments</h3>
        {canComment && !showForm && (
          <button
            type="button"
            className="add-comment-btn"
            onClick={() => {
              setPostError("");
              setShowForm(true);
            }}
          >
            Add Comment
          </button>
        )}
      </div>

      {/* Divider under header */}
      <div className="comments-divider" role="separator" />

      {/* Create a Comment Form */}
      {canComment && showForm && (
        <form onSubmit={handleAdd} className="comment-form">
          <textarea
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="Add a comment..."
            maxLength={500}
            required
          />
          {postError && <div className="inline-error">{postError}</div>}
          <div className="comment-form-actions">
            <button type="submit" disabled={disablePost}>
              {posting ? "Posting…" : "Post"}
            </button>
            <button
              type="button"
              className="btn-light"
              onClick={() => {
                setShowForm(false);
                setNewContent("");
                setPostError("");
              }}
              disabled={posting}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Comments List */}
      {comments.length === 0 && <p className="empty">No comments yet.</p>}
      <ul className="comments-list">
        {comments.map((c) => (
          <li key={c.id} className="comment-item">
            <div className="comment-header">
              <strong>@{c.user?.username}</strong>
              <span className="date">
                {new Date(c.createdAt).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}
              </span>
            </div>

            {editingId === c.id ? (
              <div className="edit-form">
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  autoFocus
                />
                <div className="comment-form-actions">
                  <button onClick={() => handleUpdate(c.id)}>Save</button>
                  <button
                    className="btn-light"
                    onClick={() => {
                      setEditingId(null);
                      setEditContent("");
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <p>{c.content}</p>
            )}

            {sessionUser?.id === c.userId && editingId !== c.id && (
              <div className="comment-actions">
                <button
                  onClick={() => {
                    setEditingId(c.id);
                    setEditContent(c.content);
                  }}
                >
                  Edit
                </button>
                <button onClick={() => handleDelete(c.id)}>Delete</button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
