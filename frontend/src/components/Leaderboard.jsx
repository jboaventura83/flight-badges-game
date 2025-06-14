import React, { useEffect, useState } from "react";

export default function Leaderboard() {
  const [scores, setScores] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/leaderboard/")
      .then((res) => res.json())
      .then((data) => setScores(data))
      .catch(console.error);
  }, []);

  return (
    <div style={{
      position: "absolute",
      top: 10,
      right: 10,
      background: "rgba(0, 0, 0, 0.7)",
      color: "white",
      padding: 10,
      borderRadius: 5,
      maxWidth: 250,
      zIndex: 1000
    }}>
      <h4>🏆 Leaderboard</h4>
      <ol>
        {scores.map(({ user_name, score }) => (
          <li key={user_name}>
            {user_name}: {score} pts
          </li>
        ))}
      </ol>
    </div>
  );
}