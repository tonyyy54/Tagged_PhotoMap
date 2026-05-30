import { useState } from "react";
import { useNavigate } from "react-router-dom";
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
      alert("Registration failed");
    }
  }

  return (
    <div>
      <h1>Register</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <input
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
          />
        </div>

        <div>
          <input
            placeholder="Username"
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