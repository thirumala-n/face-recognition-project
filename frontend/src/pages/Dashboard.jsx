import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  UserCheck,
  UserX,
  Percent,
  ScanFace,
  UserPlus,
  ArrowRight,
  RefreshCw,
  AlertTriangle,
  Clock,
} from 'lucide-react';
import StatCard from '../components/StatCard';
import DataTable from '../components/DataTable';
import { apiService } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalStudents: 0,
    presentToday: 0,
    absentToday: 0,
    attendanceRate: 0,
  });
  const [todayRecords, setTodayRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const fetchDashboardData = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      // Fetch today's attendance summary and all registered students
      const [todayData, studentsList] = await Promise.all([
        apiService.getTodayAttendance().catch(() => null),
        apiService.getStudents().catch(() => []),
      ]);

      const totalStudents = studentsList ? studentsList.length : 0;
      const presentCount = todayData ? todayData.total_present : 0;
      const absentCount = totalStudents > presentCount ? totalStudents - presentCount : (todayData ? todayData.total_absent : 0);
      const rate = totalStudents > 0 ? Math.round((presentCount / totalStudents) * 100) : 0;

      setStats({
        totalStudents,
        presentToday: presentCount,
        absentToday: absentCount,
        attendanceRate: rate,
      });

      if (todayData && Array.isArray(todayData.records)) {
        setTodayRecords(todayData.records);
      } else {
        setTodayRecords([]);
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const tableColumns = [
    {
      key: 'student_id',
      label: 'Student ID',
      render: (row) => (
        <span className="font-semibold text-slate-900 font-mono text-xs bg-slate-100 px-2 py-1 rounded">
          {row.student_id}
        </span>
      ),
    },
    {
      key: 'student_name',
      label: 'Student Name',
      render: (row) => (
        <span className="font-medium text-slate-800">
          {row.student_name || '—'}
        </span>
      ),
    },
    {
      key: 'attendance_time',
      label: 'Time Logged',
      render: (row) => (
        <div className="flex items-center gap-1.5 text-xs text-slate-500">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{row.attendance_time && row.status === 'Present' ? row.attendance_time : '—'}</span>
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: (row) => (
        <span
          className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full ${
            row.status === 'Present'
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              : 'bg-slate-100 text-slate-600 border border-slate-200'
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              row.status === 'Present' ? 'bg-emerald-500' : 'bg-slate-400'
            }`}
          />
          {row.status}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-8">
      {/* Top Banner & Refresh */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            System Overview
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time biometric attendance metrics powered by OpenCV & MySQL.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchDashboardData(true)}
            disabled={refreshing}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <Link
            to="/recognition"
            className="inline-flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 shadow-xs transition-colors"
          >
            <ScanFace className="w-3.5 h-3.5" />
            <span>Scan Face</span>
          </Link>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 flex items-start gap-3 text-xs">
          <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block">API Connection Warning</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Students"
          value={loading ? '...' : stats.totalStudents}
          icon={Users}
          color="indigo"
          subtext="Enrolled in MySQL database"
        />
        <StatCard
          title="Present Today"
          value={loading ? '...' : stats.presentToday}
          icon={UserCheck}
          color="emerald"
          badgeText="Verified"
          subtext="Marked via facial recognition"
        />
        <StatCard
          title="Absent Today"
          value={loading ? '...' : stats.absentToday}
          icon={UserX}
          color="rose"
          subtext="Unverified student count"
        />
        <StatCard
          title="Attendance Rate"
          value={loading ? '...' : `${stats.attendanceRate}%`}
          icon={Percent}
          color="blue"
          subtext="Overall daily presence"
        />
      </div>

      {/* Quick Actions Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/register-student"
          className="group p-5 bg-white rounded-xl border border-slate-200 hover:border-indigo-300 hover:shadow-xs transition-all flex items-center justify-between"
        >
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <UserPlus className="w-5 h-5" />
            </div>
            <div>
              <span className="text-sm font-semibold text-slate-900 block group-hover:text-indigo-600 transition-colors">
                Register New Student
              </span>
              <span className="text-xs text-slate-500">
                Enroll student metadata and face photos
              </span>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-1 transition-all" />
        </Link>

        <Link
          to="/recognition"
          className="group p-5 bg-white rounded-xl border border-slate-200 hover:border-indigo-300 hover:shadow-xs transition-all flex items-center justify-between"
        >
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <ScanFace className="w-5 h-5" />
            </div>
            <div>
              <span className="text-sm font-semibold text-slate-900 block group-hover:text-blue-600 transition-colors">
                Recognize & Mark
              </span>
              <span className="text-xs text-slate-500">
                Upload image to verify face with LBPH
              </span>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
        </Link>

        <Link
          to="/attendance"
          className="group p-5 bg-white rounded-xl border border-slate-200 hover:border-indigo-300 hover:shadow-xs transition-all flex items-center justify-between"
        >
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <span className="text-sm font-semibold text-slate-900 block group-hover:text-emerald-600 transition-colors">
                Attendance Logs
              </span>
              <span className="text-xs text-slate-500">
                Inspect history and filter records by date
              </span>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 group-hover:translate-x-1 transition-all" />
        </Link>
      </div>

      {/* Today's Attendance Table Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">
              Today's Attendance Feed
            </h3>
            <p className="text-xs text-slate-500">
              Live attendance records logged today with deduplication.
            </p>
          </div>
          <Link
            to="/attendance"
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <DataTable
          columns={tableColumns}
          data={todayRecords}
          loading={loading}
          emptyMessage="No attendance records for today yet"
          emptySubtext="Use the 'Scan Face' page to recognize student faces and mark attendance."
        />
      </div>
    </div>
  );
}
