import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { register } from "../api/authApi";

function RegisterPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(
    e: React.FormEvent
  ) {
    e.preventDefault();

    try {
      await register({
        email,
        username,
        password,
      });

      alert("Registration successful");

      navigate("/login");
    } catch (error) {
      console.error(error);
      const detail = axios.isAxiosError(error) ? error.response?.data?.detail : null;
      const message = typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item.msg).join("\n")
          : "Cannot connect to backend";
      alert(`Registration failed: ${message}`);
    }
  }

  return (
    <div>
      <h1>Register</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
          />
        </div>

        <div>
          <input
            placeholder="Username"
            minLength={2}
            required
            value={username}
            onChange={(e) =>
              setUsername(e.target.value)
            }
          />
        </div>

        <div>
          <input
            type="password"
            placeholder="Password"
            minLength={8}
            required
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
          />
        </div>

        <button type="submit">
          Register
        </button>
      </form>

      <button onClick={() => navigate("/login")}>
        Back to login
      </button>

    </div>
  );
}

export default RegisterPage;
