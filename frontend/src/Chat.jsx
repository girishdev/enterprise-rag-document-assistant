import { useEffect, useState } from "react";
import {
  getConversations,
  getMessages,
} from "./api";

const API_URL = import.meta.env.VITE_API_URL;

export default function Chat({ token }) {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);

    async function loadConversations() {
      try {
        const data = await getConversations(token);

        setConversations(
          Array.isArray(data) ? data : []
        );
      } catch (error) {
        console.error(error);
        setConversations([]);
      }
    }

  useEffect(() => {
    loadConversations();
  }, []);

  async function selectConversation(id) {
    setConversationId(id);

    const data = await getMessages(token, id);
    setMessages(data);
  }

  async function sendMessage() {
    setReply("");

    const response = await fetch(
      `${API_URL}/chat/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
      }
    );

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();

      if (done) break;

      const text = decoder.decode(value);

      for (const line of text.split("\n")) {
        if (!line.startsWith("data: ")) continue;

        const data = line.replace("data: ", "");

        if (data.startsWith("[DONE:")) {
          const id = data
            .replace("[DONE:", "")
            .replace("]", "");

          setConversationId(id);

          await loadConversations();

          const updatedMessages =
            await getMessages(token, id);

          setMessages(updatedMessages);

          setReply("");

          continue;
        }

        setReply((prev) => prev + data);
      }
    }

    setMessage("");
  }

  return (
    <div>
      <h2>Enterprise RAG Document Assistant</h2>

      <hr />

      <h3>Conversations</h3>

      {conversations.map((conversation) => (
        <button
          key={conversation.id}
          onClick={() =>
            selectConversation(conversation.id)
          }
        >
          {conversation.title || "Conversation"}
        </button>
      ))}

      <hr />

      <h3>Messages</h3>

      {messages.map((item) => (
        <p key={item.id}>
          <strong>{item.role}:</strong>{" "}
          {item.content}
        </p>
      ))}

      {reply && (
        <p>
          <strong>assistant:</strong> {reply}
        </p>
      )}

      <input
        value={message}
        placeholder="Ask something..."
        onChange={(e) => setMessage(e.target.value)}
      />

      <button
        onClick={sendMessage}
        disabled={!message.trim()}
      >
        Send
      </button>
    </div>
  );
}