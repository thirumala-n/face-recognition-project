import React, { useState, useEffect } from 'react';
import { Menu, Calendar, UserCheck, AlertCircle, LogOut } from 'lucide-react';
import { apiService } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ onMenuToggle, pageTitle = 'Dashboard' }) {
  const { user, logout } = useAuth();
  const [systemStatus, setSystemStatus] = useState({ online: false, db: '' });

  useEffect(() => {
    let isMounted = true;
    const checkHealth = async () => {
      try {
        const data = await apiService.getSystemStatus();
        if (isMounted) {
          setSystemStatus({ online: true, db: data.database || 'MySQL' });
        }
      } catch {
        if (isMounted) {
          setSystemStatus({ online: false, db: '' });
        }
      }
    };
    checkHealth();
    const timer = setInterval(checkHealth, 30000);
    return () => {
      isMounted = false;
      clearInterval(timer);
    };
  }, []);

  const todayStr = new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const getInitials = (name) => {
    if (!name) return 'AD';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 lg:px-8 flex items-center justify-between">
      {/* Left: Mobile hamburger & Page Title */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100"
          aria-label="Toggle navigation"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-lg font-bold text-slate-900 tracking-tight">
            {pageTitle}
          </h1>
        </div>
      </div>

      {/* Right: Date, Backend Status, User avatar & Logout */}
      <div className="flex items-center gap-3 sm:gap-5">
        {/* Current Date Display */}
        <div className="hidden sm:flex items-center gap-2 text-xs font-medium text-slate-500 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <span>{todayStr}</span>
        </div>

        {/* Backend Status Badge */}
        <div
          className={`hidden md:flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border ${
            systemStatus.online
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-rose-50 text-rose-700 border-rose-200'
          }`}
          title={
            systemStatus.online
              ? `Connected to MySQL: ${systemStatus.db}`
              : 'Cannot connect to FastAPI at http://127.0.0.1:8000'
          }
        >
          <span
            className={`w-2 h-2 rounded-full ${
              systemStatus.online ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
            }`}
          />
          <span>{systemStatus.online ? 'API Online' : 'API Offline'}</span>
        </div>

        {/* Profile Avatar & Logout */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-700 to-slate-900 text-white flex items-center justify-center font-semibold text-xs shadow-2xs">
            {getInitials(user?.full_name)}
          </div>
          <div className="hidden sm:block text-left">
            <span className="text-xs font-semibold text-slate-800 block leading-tight truncate max-w-[120px]">
              {user?.full_name || 'Administrator'}
            </span>
            <span className="text-[10px] text-slate-400 block truncate max-w-[120px]">
              @{user?.username || 'admin'}
            </span>
          </div>
          <button
            onClick={logout}
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors ml-1"
            title="Sign Out"
            aria-label="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
