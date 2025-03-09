import React, { useState, useEffect } from "react";
import apiClient from "../utils/apiClient";
import "bootstrap/dist/css/bootstrap.min.css"; // Ensure Bootstrap is imported
import { useNavigate } from "react-router-dom";

const AdminDashboard: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>(""); // Search term state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch data from backend on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiClient.get("/api/data");
        setData(response.data.data); // Assuming the API response contains `data`
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to load data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filtered data based on search term
  const filteredData = data.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="d-flex flex-column align-items-center justify-content-center vh-100 bg-light">
      <div className="container bg-white p-4 rounded-3 shadow-lg" style={{ maxWidth: "800px", width: "90%" }}>
        <h2 className="text-center mb-4">Admin Dashboard</h2>
        <p className="text-center text-muted mb-4">Monitor patient history.</p>

        {/* Search Bar */}
        <div className="mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="Search by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Loading Indicator */}
        {loading && (
          <div className="text-center">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && <div className="alert alert-danger">{error}</div>}

        {/* Data Table */}
        {!loading && !error && filteredData.length > 0 && (
          <div className="table-responsive">
            <table className="table table-striped table-hover">
              <thead className="table-dark">
                <tr>
                  <th>Name</th>
                  <th>Timestamp</th>
                  <th>Mental Health</th>
                  <th>Knowledge</th>
                  <th>Physical Health</th>
                  <th>Preventive Care</th>
                  <th>Health Seeking</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((item, _) => (
                  <tr key={item.id} onClick={() => navigate(`/patient/${item.id}`)} style={{ cursor: "pointer" }}>
                    <td>{item.name}</td>
                    <td>{new Date(item.timestamp).toLocaleString()}</td>
                    <td>{item.mental_health}</td>
                    <td>{item.knowledge}</td>
                    <td>{item.physical_health}</td>
                    <td>{item.preventive_care}</td>
                    <td>{item.health_seeking}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* No Data Message */}
        {!loading && !error && filteredData.length === 0 && (
          <p className="text-center text-muted">No matching records found.</p>
        )}

        {/* Admin Controls */}
        <div className="d-flex justify-content-center mt-4">
          <button className="btn btn-secondary me-2" onClick={() => navigate("/")}>Logout</button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
