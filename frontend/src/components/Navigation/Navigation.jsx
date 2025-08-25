// src/components/Navigation/index.jsx (your file)
import { useSelector } from "react-redux";
import { NavLink } from "react-router-dom";
import ProfileButton from "./ProfileButton";
import OpenModalMenuItem from "./OpenModalMenuItem";
import LoginFormModal from "../LoginFormModal";
import SignupFormModal from "../SignupFormModal";
import SearchBar from "../SearchBar";
import "./Navigation.css";

function Navigation() {
  const sessionUser = useSelector((state) => state.session.user);

  return (
    <nav className="navbar">
      {/* Left: Logo */}
      <div className="nav-left">
        <NavLink to="/" className="nav-logo">
          MasterDex
        </NavLink>
      </div>

      {/* Center: Search */}
      <div className="nav-center">
        <SearchBar />
      </div>

      {/* Right: User Actions */}
      <div className="nav-right">
        {sessionUser ? (
          <ProfileButton user={sessionUser} />
        ) : (
          <>
            <OpenModalMenuItem
              itemText="Log In"
              modalComponent={<LoginFormModal />}
              className="btn btn-primary"
            />
            <OpenModalMenuItem
              itemText="Sign Up"
              modalComponent={<SignupFormModal />}
              className="btn btn-primary"
            />
          </>
        )}
      </div>
    </nav>
  );
}

export default Navigation;
