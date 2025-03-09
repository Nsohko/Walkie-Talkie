import React, { useEffect, useState } from "react";
import apiClient from "../utils/apiClient";
import { useParams, useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css"; // Import Bootstrap

const PatientDetails: React.FC = () => {
    const { id } = useParams(); // Get patient ID from URL
    const navigate = useNavigate();
    const [patientData, setPatientData] = useState<any>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPatientData = async () => {
            try {
                const response = await apiClient.get(`/api/health-analysis/${id}`);
                setPatientData(response.data.health_analysis);
            } catch (err) {
                setError((err as Error).message);
            } finally {
                setLoading(false);
            }
        };

        fetchPatientData();
    }, [id]);

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading patient details...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="alert alert-danger text-center mt-4">
                <strong>Error:</strong> {error}
            </div>
        );
    }

    return (
        <div className="d-flex flex-column vh-100 bg-light">
            {/* Header Section */}
            <div className="bg-white shadow-sm p-3 border-bottom d-flex justify-content-between align-items-center">
                <h2 className="mb-0">Patient Details</h2>
                <div className="container d-flex justify-content-end">
                    <button className="btn btn-secondary me-2" onClick={() => navigate("/admin")}>Back to Dashboard</button>
                </div>
            </div>

            {/* Patient Information (Scrollable) */}
            <div className="flex-grow-1 overflow-auto p-4" style={{ maxHeight: "75vh" }}>
                <div className="container bg-white shadow-sm p-4 rounded">
                    {/* Two-Column Layout for Health Details */}
                    <div className="row g-3">
                        <div className="col-md-6">
                            <p><strong>Name:</strong> {patientData.name}</p>
                            <p><strong>Timestamp:</strong> {new Date(patientData.timestamp).toLocaleString()}</p>
                            <p><strong>Mental Health Score:</strong> {patientData.mental_health}</p>
                            <p><strong>Knowledge Score:</strong> {patientData.knowledge}</p>
                        </div>
                        <div className="col-md-6">
                            <p><strong>Physical Health Score:</strong> {patientData.physical_health}</p>
                            <p><strong>Preventive Care Score:</strong> {patientData.preventive_care}</p>
                            <p><strong>Health-Seeking Score:</strong> {patientData.health_seeking}</p>
                        </div>
                    </div>

                    {/* Unanswered Questions Section */}
                    {patientData.unanswered_questions?.length > 0 && (
                        <div className="mt-4 pt-3 border-top">
                            <h4 className="text-secondary">Unanswered Questions</h4>
                            <ul className="list-group mt-2">
                                {patientData.unanswered_questions.map((question: string, index: number) => (
                                    <li key={index} className="list-group-item">{question}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PatientDetails;
