import React, { useState } from "react";
import Chat from "./pages/Chat";
import Login from "./pages/Login";

function App() {
  const [loggedIn, setLoggedIn] = useState(
    !!localStorage.getItem("access_token")
  );

  const handleLogin = () => {
    setLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setLoggedIn(false);
  };

  if (!loggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div>
      <button
        onClick={handleLogout}
        style={{ position: "absolute", top: 10, right: 10 }}
      >
        Logout
      </button>
      <Chat />
    </div>
  );
}

export default App;
