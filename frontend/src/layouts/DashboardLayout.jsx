import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';

const ROUTE_TITLES = {
  '/': 'Attendance Overview & Metrics',
  '/dashboard': 'Attendance Overview & Metrics',
  '/students': 'Student Directory',
  '/register-student': 'Register New Student',
  '/recognition': 'Live Face Recognition & Attendance',
  '/attendance': 'Daily & Historical Attendance Logs',
  '/settings': 'System Settings & Architecture',
};

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const currentTitle = ROUTE_TITLES[location.pathname] || 'Dashboard';

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar Navigation */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-h-screen">
        <Navbar
          onMenuToggle={() => setSidebarOpen(true)}
          pageTitle={currentTitle}
        />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
