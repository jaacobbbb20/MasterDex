import "./LandingPage.css";
import { useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { useState } from "react";
import CreateBinderModal from "../CreateBinderModal/CreateBinderModal";

const topCards = [
  {
    id: 1,
    name: "Pikachu Illustrator",
    value: "5,275,000",
    image: "https://i.pinimg.com/originals/29/0f/df/290fdf94a6e44975e17c6a1531b0c9b2.jpg",
    details: "Awarded to winners of a Japanese illustration contest, very rare."
  },
  {
    id: 2,
    name: "1st Edition Shadowless Charizard",
    value: "420,000",
    image: "https://images.pokemontcg.io/base1/4_hires.png",
    details: "Iconic Base Set card, highly sought after by collectors."
  },
  {
    id: 3,
    name: "Trophy Pikachu No.1 Trainer",
    value: "250,000",
    image: "https://images.getcardbase.com/82lxcul30bwoe71fob2ffil56snp",
    details: "Awarded to winners of the 1997-1998 Lizardon Mega Battle Tournament."
  },
  {
    id: 4,
    name: "Kangaskhan Parent/Child Promo",
    value: "150,000",
    image: "https://images.production.sportscardinvestor.com/6973_6653_15110_115-L",
    details: "Given to participants of a family event in Japan, very limited."
  },
  {
    id: 5,
    name: "Blastoise Test Print",
    value: "360,000",
    image: "https://images.pokemontcg.io/base1/2_hires.png",
    details: "Prototype card from early Pokémon TCG development."
  },
];

const LandingPage = () => {
  const navigate = useNavigate();
  const sessionUser = useSelector((state) => state.session.user);
  const [showBinderModal, setShowBinderModal] = useState(false);

  return (
    <div className="landing-page">
      <section className="hero">
        <h1>Track All of Your Pokemon Cards</h1>
        <p>Organize your cards, track your collections, and connect with other collectors.</p>

        <div className="hero-line"></div>

        <div className="hero-features">
          <div className="feature-column">
            <div className="feature-item">Card Management: Add, view, and edit your cards.</div>
            <div className="feature-item">Binders: Organize cards into binders and track collections.</div>
          </div>
          <div className="feature-column">
            <div className="feature-item">Social: Follow other collectors and see their collections.</div>
            <div className="feature-item">Comments: Leave and read comments on other user&apos; binders.</div>
          </div>
        </div>
      </section>

      {sessionUser && (
        <section className="binder-actions">
          <button
            className="create-binder-btn"
            onClick={() => setShowBinderModal(true)}
          >
            Create Binder
          </button>

          {showBinderModal && (
            <CreateBinderModal onClose={() => setShowBinderModal(false)} />
          )}

          <button
            className="view-binders-btn"
            onClick={() => navigate(`/profiles/${sessionUser.id}`)}
          >
            View Your Binders
          </button>
        </section>
      )}

      <section className="top-cards">
        <h2>Top 5 Most Valuable Cards</h2>
        <div className="card-list">
          {topCards.map((card) => (
            <div key={card.id} className="card">
              <img src={card.image} alt={card.name} />
              <h3>{card.name}</h3>
              <p>Value: ${card.value}</p>
              <p>{card.details}</p>
            </div>
          ))}
        </div>
      </section>

      <footer>
        <p>&copy; 2025 MasterDex. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
