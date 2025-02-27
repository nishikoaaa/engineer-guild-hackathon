import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Welcome from './pages/Welcome';
import TopPage from './pages/TopPage/TopPage';
import { HelmetProvider } from "react-helmet-async";
import QuestionPage from './pages/Question';
import SummarySpeech from './components/SummarySpeech';
import { FlashProvider } from './contexts/FlashProvider';

const App: React.FC = () => {
  return (
    <HelmetProvider>
      <FlashProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/TopPage" element={<TopPage />} />
            <Route path="/QuestionPage" element={<QuestionPage />} />
            <Route path="/SummarySpeech" element={<SummarySpeech />} />
          </Routes>
        </Router>
      </FlashProvider>
    </HelmetProvider>
  );
};

export default App;