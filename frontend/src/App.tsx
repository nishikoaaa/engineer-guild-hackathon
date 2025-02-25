import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import TopPage from './pages/TopPage/TopPage';
import { HelmetProvider } from "react-helmet-async";
import WelcomePage from './pages/WelcomePage/WelcomePage';

const App: React.FC = () => {
  return (
    <HelmetProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/TopPage" element={<TopPage />} />
          <Route path="/WelcomePage" element={<WelcomePage />} />
        </Routes>
      </Router>
    </HelmetProvider>
  );
};

export default App;