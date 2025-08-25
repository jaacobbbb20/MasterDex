import { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { useModal } from "../../context/Modal";
import { thunkLogin /*, thunkAuthenticate*/ } from "../../redux/session";
import "./LoginForm.css";

function LoginFormModal() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { closeModal } = useModal();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setEmail("");
    setPassword("");
    setErrors({});
    setSubmitting(false);
  }, []);

  const handleSuccess = () => {
    closeModal();
    navigate("/");
  };

  const handleLogin = async (credentials) => {
    setErrors({});
    setSubmitting(true);
    try {
      const user = await dispatch(thunkLogin(credentials)).unwrap();

      if (!user) throw new Error("Login failed");
      handleSuccess();
    } catch (err) {
      const fieldErrors =
        typeof err === "string"
          ? { server: err }
          : err?.errors || err || { server: "Login failed. Please try again." };
      setErrors(fieldErrors);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (submitting) return;
    handleLogin({ email, password });
  };

  const handleDemoLogin = () => {
    if (submitting) return;
    handleLogin({ email: "demo@aa.io", password: "password" });
  };

  return (
    <div className="form-page">
      <h1 className="log-in-text">Log In</h1>
      <form onSubmit={handleSubmit} className="login-form" noValidate>
        {errors.server && <p className="error-text">{errors.server}</p>}

        <label className="input-label">
          Email
          <input
            type="email"
            className="input-field"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (errors.email || errors.server) setErrors({ ...errors, email: null, server: null });
            }}
            autoComplete="email"
            required
          />
        </label>
        {errors.email && <p className="error-text">{errors.email}</p>}

        <label className="input-label">
          Password
          <input
            type="password"
            className="input-field"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (errors.password || errors.server) setErrors({ ...errors, password: null, server: null });
            }}
            autoComplete="current-password"
            required
          />
        </label>
        {errors.password && <p className="error-text">{errors.password}</p>}

        <button type="submit" className="submit-button" disabled={submitting}>
          {submitting ? "Signing in…" : "Log In"}
        </button>

        <button type="button" onClick={handleDemoLogin} className="demo-user" disabled={submitting}>
          {submitting ? "Please wait…" : "Demo User"}
        </button>
      </form>
    </div>
  );
}

export default LoginFormModal;
