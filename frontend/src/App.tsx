import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Welcome from './pages/Welcome';
import TopPage from './pages/TopPage/TopPage';
import { HelmetProvider } from "react-helmet-async";
import WelcomePage from './pages/WelcomePage/WelcomePage';
import QuestionPage from './pages/QuestionPage/Question';

const App: React.FC = () => {
  return (
    <HelmetProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route path="/TopPage" element={<TopPage />} />
          <Route path="/WelcomePage" element={<WelcomePage />} />
          <Route path="/QuestionPage" element={<QuestionPage />} />
        </Routes>
      </Router>
    </HelmetProvider>
  );
};

export default App;