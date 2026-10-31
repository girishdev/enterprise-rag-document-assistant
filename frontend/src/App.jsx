import { useState } from "react";
import Login from "./Login";
import Chat from "./Chat";

function App() {
  const [token, setToken] = useState(
    localStorage.getItem("token")
  );

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  if (!token) {
    return <Login onLogin={setToken} />;
  }

  return (
    <Chat
      token={token}
      onLogout={logout}
    />
  );
}

export default App;