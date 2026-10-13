import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import FileUpload from './components/FileUpload';
import MatchTable from './components/MatchTable';
import EntityDetails from './components/EntityDetails';
import LiveComparator from './components/LiveComparator';
import Statistics from './components/Statistics';
import EvaluationView from './components/EvaluationView';
import { fetchHealth, fetchStatistics, triggerMatching } from './api';
import './styles/App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [isMatching, setIsMatching] = useState(false);

  // Load initial system stats and health
  const refreshAppData = async () => {
    try {
      const [h, s] = await Promise.all([
        fetchHealth().catch(() => ({ status: 'offline', model_loaded: false })),
        fetchStatistics().catch(() => null)
      ]);
      setHealth(h);
      setStats(s);
    } catch (e) {
      console.error('Error refreshing app state:', e);
    }
  };

  useEffect(() => {
    refreshAppData();
  }, []);

  const handleRerunMatch = async () => {
    setIsMatching(true);
    try {
      await triggerMatching({ threshold: 60.0 });
      await refreshAppData();
    } catch (err) {
      console.error('Failed to rerun matching:', err);
    } finally {
      setIsMatching(false);
    }
  };

  return (
    <div className="app-layout">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
        onRerunMatch={handleRerunMatch}
        isMatching={isMatching}
      />

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard
            stats={stats}
            onNavigate={setActiveTab}
            onRerunMatch={handleRerunMatch}
            isMatching={isMatching}
          />
        )}

        {activeTab === 'upload' && (
          <FileUpload
            onResolutionComplete={refreshAppData}
          />
        )}

        {activeTab === 'matches' && (
          <MatchTable />
        )}

        {activeTab === 'entities' && (
          <EntityDetails />
        )}

        {activeTab === 'compare' && (
          <LiveComparator />
        )}

        {activeTab === 'statistics' && (
          <Statistics
            stats={stats}
          />
        )}

        {activeTab === 'evaluation' && (
          <EvaluationView />
        )}
      </main>
    </div>
  );
}
