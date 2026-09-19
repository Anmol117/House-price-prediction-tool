import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { PredictionForm } from './components/PredictionForm';
import { ModelInfo } from './components/ModelInfo';

export const App: React.FC = () => {
  return (
    <div className="app-layout">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<PredictionForm />} />
          <Route path="/about" element={<ModelInfo />} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="footer-container">
          <p>© {new Date().getFullYear()} HomeValuate AI — House Price Prediction Engine</p>
          <p className="footer-subtext">Powered by FastAPI, scikit-learn & React</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
