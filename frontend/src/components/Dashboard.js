// src/components/Dashboard.js

import React from 'react';
import { useLocation } from 'react-router-dom';
import '../styles/Dashboard.css';
import PlaneManufacturing from './PlaneManufacturing';
import PartManufacturing from './PartManufacturing';
import logo from '../assets/images/Baykar-Logo.svg';

const Dashboard = () => {
  const location = useLocation();
  const { departmentData } = location.state || {};

  if (!departmentData) {
    return <p>No department information available.</p>;
  }

  const { username, isAssemblyTeam, departments } = departmentData;

  const accessibleDepartment = departments ? departments.find((dept) => dept.isAccess) : null;

  let departmentMessage = '';
  let customMessage = '';

  if (isAssemblyTeam) {
    departmentMessage = "You're on Assembly Team";
  } else if (accessibleDepartment) {
    departmentMessage = `You're on ${accessibleDepartment.department_name}`;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard">
        <div className="logo">
          <img src={logo} alt="Baykar Logo" className="logo-img" />
        </div>

        <p>{departmentMessage}</p>
        {customMessage && <p>{customMessage}</p>}
        {isAssemblyTeam && <PlaneManufacturing token={localStorage.getItem('accessToken')} />}
        {accessibleDepartment && <PartManufacturing token={localStorage.getItem('accessToken')} />}
      </div>
    </div>
  );
};

export default Dashboard;
