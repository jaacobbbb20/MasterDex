import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./CreateBinderModal.css";

const CreateBinderModal = ({ onClose }) => {
  const [sets, setSets] = useState([]);
  const [selectedSet, setSelectedSet] = useState("");
  const [customNameChecked] = useState(false);
  const [customName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const getCSRFToken = () => {
    const c = document.cookie.split("; ").find((x) => x.startsWith("csrf_token="));
    return c ? decodeURIComponent(c.split("=")[1]) : null;
  };

  // Fetch full set info (with totals, logos, etc.)
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/sets", {
          credentials: "include",
        });
        if (!res.ok) throw new Error("Failed to fetch sets");
        const data = await res.json();
        setSets(data.data || data || []);
      } catch (err) {
        console.error("Error fetching sets:", err);
      }
    })();
  }, []);

  const setMap = useMemo(() => {
    const m = new Map();
    sets.forEach((s) => m.set(s.id, s));
    return m;
  }, [sets]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedSet) return;

    const setObj = setMap.get(selectedSet);
    const nameToSend = customNameChecked
      ? customName.trim()
      : (setObj?.name || "").trim();

    if (!nameToSend) return;

    setSubmitting(true);
    try {
      const res = await fetch("/api/binders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        credentials: "include",
        body: JSON.stringify({
          name: nameToSend,
          description: "",
          set_id: setObj.id,
          set_name: setObj.name,
          set_symbol: setObj.symbol || null,
          set_logo: setObj.image || null,
          printed_total: setObj.printed_total,
          total_in_set: setObj.total_in_set,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        console.error("Binder creation failed:", err);
        setSubmitting(false);
        return;
      }

      const newBinderRes = await res.json();
      const newBinder = newBinderRes.binder;
      onClose();
      navigate(`/binders/${newBinder.id}`);
    } catch (err) {
      console.error("Error creating binder:", err);
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal-content">
        <h2>Create a New Binder</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Choose a Set:
            <select
              value={selectedSet}
              onChange={(e) => setSelectedSet(e.target.value)}
              required
            >
              <option value="">-- Select a Set --</option>
              {sets.map((set) => (
                <option key={set.id} value={set.id}>
                  {set.name} ({set.total_in_set || "?"} cards)
                </option>
              ))}
            </select>
          </label>

          <div className="modal-buttons">
            <button type="submit" className="create-btn" disabled={submitting}>
              {submitting ? "Creating..." : "Create Binder"}
            </button>
            <button type="button" className="cancel-btn" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateBinderModal;
