import React from 'react';
import { ReturnIQDashboardEnhanced } from './dashboard-enhanced';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ToastProvider } from './context/ToastContext';
import { ToastContainer } from './components/Toast';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <div className="App">
          <ReturnIQDashboardEnhanced />
          <ToastContainer />
        </div>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
