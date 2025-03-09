import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Chat from "./pages/Chat";
import AdminDashboard from "./pages/Dashboard";
import PatientDetails from "./pages/PatientDetails";

const App: React.FC = () => {
  const [username, setUsername] = useState<string | null>(null);

  return (
    <Router>
      <Routes>
        {/* Login Route */}
        <Route path="/" element={<Login setUsername={setUsername} />} />

        {/* Redirect to Chat or Admin based on login */}
        <Route
          path="/chat"
          element={username && username !== "admin" ? <Chat username={username} /> : <Navigate to="/" />}
        />
        <Route
          path="/admin"
          element= {<AdminDashboard/>}
        />
        <Route
          path="/patient/:id"
          element={<PatientDetails />}
        />
      </Routes>
    </Router>
  );
};

export default App;
