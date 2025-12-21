import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="container">
      <header className="header">
        <h1>DiffServ Network Simulation</h1>
        <p>Advanced Traffic Simulation & Analysis Dashboard</p>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
