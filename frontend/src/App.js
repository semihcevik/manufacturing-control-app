
import React, { useState } from 'react';
import './index.css';
import logo from './assets/images/Baykar-Logo.svg';
import { Route, Routes, useNavigate, useLocation } from 'react-router-dom';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import { getDepartmentList } from './services/departmentService';
import { login } from './services/authService';

function App() {
  const [departmentInfo, setDepartmentInfo] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  const isLoginPage = location.pathname === '/';

  const handleLogin = async (username, password) => {
    try {
      const { access: accessToken } = await login(username, password);
      localStorage.setItem('accessToken', accessToken);
      const departmentData = await getDepartmentList(accessToken);
      setDepartmentInfo(departmentData);
      navigate('/dashboard', { state: { departmentData } });
    } catch (error) {
      throw error;
    }
  };

  return (
    <div className={`app-container ${isLoginPage ? 'login-page' : 'dashboard-page'}`}>
      <header className="app-header">
     
      </header>
      <div className="container">
        <div className="login-box-wrapper">
          <div className="login-box">
            
          <div className="logo">
            <img src={logo} alt="Baykar Logo" className="logo-img" />
          </div>

            <Routes>
              <Route path="/" element={<LoginForm onLogin={handleLogin} />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
