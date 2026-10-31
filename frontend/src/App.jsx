import { useState } from "react";

import Login from "./Login";
import Chat from "./Chat";
import Documents from "./Documents";

function App() {
  const [token, setToken] = useState(
    localStorage.getItem("token")
  );

  const [page, setPage] = useState("chat");

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  if (!token) {
    return <Login onLogin={setToken} />;
  }

  return (
    <div>
      <h1>Enterprise RAG Document Assistant</h1>

      <button onClick={() => setPage("chat")}>
        Chat
      </button>

      <button onClick={() => setPage("documents")}>
        Documents
      </button>

      <button onClick={logout}>
        Logout
      </button>

      <hr />

      {page === "chat" && (
        <Chat
          token={token}
          onLogout={logout}
        />
      )}

      {page === "documents" && (
        <Documents token={token} />
      )}
    </div>
  );
}

export default App;