import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

interface LoginProps {
  setUsername: (username: string) => void;
}

const Login: React.FC<LoginProps> = ({ setUsername }) => {
  const [name, setName] = useState<string>("");
  const navigate = useNavigate();

  const handleLogin = () => {
    if (name.trim() === "") return; // Prevent empty names

    setUsername(name);
    navigate(name === "admin" ? "/admin" : "/chat");
  };

  return (
    <div className="d-flex flex-column align-items-center justify-content-center vh-100 bg-light">
      <div className="container bg-white p-4 rounded-3 shadow-lg text-center" style={{ maxWidth: "400px" }}>
        <h2 className="mb-4">Login</h2>
        <input
          type="text"
          className="form-control mb-3"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <button
          onClick={handleLogin}
          className="btn btn-primary w-100 shadow-sm"
        >
          Login
        </button>
      </div>
    </div>
  );
};

export default Login;
