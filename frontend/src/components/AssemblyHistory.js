// src/components/AssemblyHistory.js

import React, { useEffect, useState } from 'react';
import '../styles/PlaneManufacturing.css';
import { fetchAssemblyHistory } from '../services/planeManufactureService';

const AssemblyHistory = ({ token, refresh }) => {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const historyData = await fetchAssemblyHistory(token);
        setHistory(historyData);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchHistory();
  }, [token, refresh]); // Add 'refresh' as a dependency

  if (error) {
    return <p>{error}</p>;
  }

  if (history.length === 0) {
    return <p>Loading assembly history...</p>;
  }

  return (
    <div className="assembly-history">
      <h2>Assembly History</h2>
      <table className="plane-table">
        <thead>
          <tr>
            <th>Plane Name</th>
            <th>Used Parts</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {history.map((entry, index) => (
            <tr key={index}>
              <td>{entry.plane_name}</td>
              <td>{entry.used_parts}</td>
              <td>{entry.date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AssemblyHistory;
