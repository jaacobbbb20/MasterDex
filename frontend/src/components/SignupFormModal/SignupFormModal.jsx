import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { useModal } from "../../context/Modal";
import { thunkSignup } from "../../redux/session";
import "./SignupForm.css";

function SignupFormModal() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { closeModal } = useModal();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      return setErrors({ confirmPassword: "Passwords must match" });
    }

    const serverResponse = await dispatch(
      thunkSignup({ email, username, password, confirmPassword, firstName, lastName })
    );

    if (serverResponse?.errors) {
      setErrors(serverResponse.errors);
    } else {
      closeModal();
      navigate("/");      // Redirect to landing page
    }
  };

  return (
    <div className="form-page">
      <h1 className="sign-up-text">Sign Up</h1>
      <form onSubmit={handleSubmit} className="signup-form">
        <label className="input-label">
          First Name
          <input
            type="text"
            value={firstName}
            className="input-field"
            onChange={(e) => {
              setFirstName(e.target.value);
              if (errors.firstName) setErrors({ ...errors, firstName: null });
            }}
            required
          />
        </label>
        {errors.firstName && <p className="error-text">{errors.firstName}</p>}

        <label className="input-label">
          Last Name
          <input
            type="text"
            value={lastName}
            className="input-field"
            onChange={(e) => {
              setLastName(e.target.value);
              if (errors.lastName) setErrors({ ...errors, lastName: null });
            }}
            required
          />
        </label>
        {errors.lastName && <p className="error-text">{errors.lastName}</p>}

        <label className="input-label">
          Email
          <input
            type="email"
            value={email}
            className="input-field"
            onChange={(e) => {
              setEmail(e.target.value);
              if (errors.email) setErrors({ ...errors, email: null });
            }}
            required
          />
        </label>
        {errors.email && <p className="error-text">{errors.email}</p>}

        <label className="input-label">
          Username
          <input
            type="text"
            value={username}
            className="input-field"
            onChange={(e) => {
              setUsername(e.target.value);
              if (errors.username) setErrors({ ...errors, username: null });
            }}
            required
          />
        </label>
        {errors.username && <p className="error-text">{errors.username}</p>}

        <label className="input-label">
          Password
          <input
            type="password"
            value={password}
            className="input-field"
            onChange={(e) => {
              setPassword(e.target.value);
              if (errors.password) setErrors({ ...errors, password: null });
            }}
            required
          />
        </label>
        {errors.password && <p className="error-text">{errors.password}</p>}

        <label className="input-label">
          Confirm Password
          <input
            type="password"
            value={confirmPassword}
            className="input-field"
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              if (errors.confirmPassword)
                setErrors({ ...errors, confirmPassword: null });
            }}
            required
          />
        </label>
        {errors.confirmPassword && (
          <p className="error-text">{errors.confirmPassword}</p>
        )}

        {errors.server && <p className="error-text">{errors.server}</p>}

        <button type="submit" className="submit-button">
          Sign Up
        </button>
      </form>
    </div>
  );
}

export default SignupFormModal;
