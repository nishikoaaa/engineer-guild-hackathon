import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Welcome from './pages/Welcome';
import TopPage from './pages/TopPage/TopPage';
import { HelmetProvider } from "react-helmet-async";
import QuestionPage from './pages/Question';
import SummarySpeech from './components/SummarySpeech';

const App: React.FC = () => {
  return (
    <HelmetProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route path="/TopPage" element={<TopPage />} />
          <Route path="/QuestionPage" element={<QuestionPage />} />
          <Route path="/SummarySpeech" element={<SummarySpeech />} />
        </Routes>
      </Router>
    </HelmetProvider>
  );
};

export default App;