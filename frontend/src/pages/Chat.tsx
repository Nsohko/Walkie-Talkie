import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../utils/apiClient";
import "bootstrap/dist/css/bootstrap.min.css"; // Import Bootstrap

interface ChatProps {
  username: string;
}

const Chat: React.FC<ChatProps> = ({ username }) => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState<string>("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();

  // Start session on mount
  useEffect(() => {
    const startSession = async () => {
      try {
        const response = await apiClient.post("/api/start-session", { username });
        setSessionId(response.data.sessionId);
      } catch (error) {
        console.error("Error starting session:", error);
      }
    };

    startSession();

    return () => {
      if (sessionId) {
        apiClient.post("/api/end-session", { sessionId }).catch((error) => console.error("Error ending session:", error));
      }
    };
  }, [username]);

  // Send message to backend
  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (input.trim() === "" || !sessionId) return;

    const userMessage = { sender: username, text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await apiClient.post("/api/chat", {
        sessionId,
        question: input,
      });

      const botMessage = { sender: "Chatbot", text: response.data.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error fetching chatbot response:", error);
    } finally {
      setLoading(false);
    }
  };

  // End Chat & Redirect
  const endChat = async () => {
    if (!sessionId) return;

    try {
      await apiClient.post("/api/end-chat", { sessionId, name: username });
      navigate("/admin"); // Redirect to dashboard
    } catch (error) {
      console.error("Error ending chat:", error);
    }
  };

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="d-flex flex-column vh-100 bg-light">
      <div className="bg-white shadow-sm p-3 border-bottom d-flex justify-content-between align-items-center">
        <h2 className="mb-0">Healthhack 2025</h2>
        <div>
          <button className="btn btn-secondary me-2" onClick={() => navigate("/")}>Restart Chat</button>
          <button className="btn btn-danger" onClick={endChat}>End Chat and View Dashboard</button>
        </div>
      </div>
      {/* Chat Messages (Scrollable) */}
      <div className="flex-grow-1 overflow-auto p-3" style={{ maxHeight: "80vh" }}>
        <div className="container d-flex flex-column">
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`mb-2 p-3 rounded-3 shadow-sm ${msg.sender === username ? "bg-primary text-white align-self-end" : "bg-secondary text-light align-self-start"}`} 
              style={{ maxWidth: "75%" }}
            >
              <strong>{msg.sender}:</strong> {msg.text}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Loading Indicator */}
      {loading && (
        <div className="text-center p-2">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      )}

      {/* Chat Controls & Input (Fixed at Bottom) */}
      <div 
        className="bg-white border-top p-3"
        style={{ 
          position: "fixed", 
          bottom: 0, 
          left: 0, 
          width: "100%" 
        }}
      >
        <div className="container">
          {/* Chat Input */}
          <form onSubmit={sendMessage} className="d-flex mb-2">
            <input
              type="text"
              className="form-control me-2"
              placeholder="Type a message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              required
            />
            <button className="btn btn-primary" type="submit">Send</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;
