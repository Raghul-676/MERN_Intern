import React, { useState } from "react";
import { api } from "../api/client";

export default function Login({ onLogin }) {
  const [mode, setMode] = useState("login"); // "login" or "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    if (!email || !password) return;
    setLoading(true);
    try {
      const body = new URLSearchParams();
      body.append("username", email);   // FastAPI OAuth2PasswordRequestForm
      body.append("password", password);

      const res = await api.post("/auth/login", body, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const token = res.data.access_token;
      localStorage.setItem("access_token", token);
      if (onLogin) onLogin();
    } catch (e) {
      console.error(e);
      setError("Login failed. Check email/password.");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    if (!email || !password) return;
    setLoading(true);
    try {
      await api.post("/auth/register", {
        email,
        password,   // backend will always set role="user"
      });
      alert("User created. You can login now.");
      setMode("login");
    } catch (e) {
      console.error(e);
      setError("Registration failed. Maybe email already exists.");
    } finally {
      setLoading(false);
    }
  };

  const isLogin = mode === "login";

  return (
    <div style={{ padding: "1rem", maxWidth: 400, margin: "0 auto" }}>
      <h2>{isLogin ? "Login" : "New User Registration"}</h2>

      <div style={{ marginBottom: "0.5rem" }}>
        <button
          type="button"
          onClick={() => setMode("login")}
          disabled={isLogin}
        >
          Login
        </button>
        <button
          type="button"
          onClick={() => setMode("register")}
          disabled={!isLogin}
          style={{ marginLeft: "0.5rem" }}
        >
          New User
        </button>
      </div>

      <form onSubmit={isLogin ? handleLogin : handleRegister}>
        <div style={{ marginBottom: "0.5rem" }}>
          <label>
            Email
            <input
              type="email"
              style={{ width: "100%" }}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </label>
        </div>

        <div style={{ marginBottom: "0.5rem" }}>
          <label>
            Password
            <input
              type="password"
              style={{ width: "100%" }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </label>
        </div>

        {error && (
          <div style={{ color: "red", marginBottom: "0.5rem" }}>{error}</div>
        )}

        <button type="submit" disabled={loading}>
          {loading
            ? isLogin
              ? "Logging in..."
              : "Creating..."
            : isLogin
            ? "Login"
            : "Create account"}
        </button>
      </form>
    </div>
  );
}
