import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '@/pages/Dashboard';
import MyFarms from '@/pages/MyFarms';
import Ownership from '@/pages/Ownership';
import Marketplace from '@/pages/Marketplace';
import Settlement from '@/pages/Settlement';
import AdminPanel from '@/pages/AdminPanel';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';

const App: React.FC = () => {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 overflow-y-auto p-4">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/my-farms" element={<MyFarms />} />
              <Route path="/ownership" element={<Ownership />} />
              <Route path="/marketplace" element={<Marketplace />} />
              <Route path="/settlement" element={<Settlement />} />
              <Route path="/admin" element={<AdminPanel />} />
              {/* Add more routes as needed */}
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
