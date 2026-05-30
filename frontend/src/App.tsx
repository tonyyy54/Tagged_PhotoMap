import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import UploadPage from "./pages/UploadPage";
import MapPage from "./pages/MapPage";
import ProtectedRoute from "./components/ProtectedRoute";

// http://localhost:5173/login
function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<Navigate to="/login" />} />

        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/register"
          element={<RegisterPage />}
        />

        <Route element={<ProtectedRoute />}>
          <Route
            path="/upload"
            element={<UploadPage />}
          />

          <Route
            path="/map"
            element={<MapPage />}
          />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;
