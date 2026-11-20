import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Calendar,
  Search,
  RefreshCw,
  Clock,
  UserCheck,
  UserX,
  History,
  Filter,
  AlertCircle,
  Users,
} from 'lucide-react';
import DataTable from '../components/DataTable';
import StatCard from '../components/StatCard';
import { apiService } from '../services/api';

export default function Attendance() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialStudentId = searchParams.get('student_id') || '';

  // Mode: 'date' or 'student'
  const [viewMode, setViewMode] = useState(initialStudentId ? 'student' : 'date');

  // Date Filter State (default to today: YYYY-MM-DD)
  const todayStr = new Date().toISOString().split('T')[0];
  const [selectedDate, setSelectedDate] = useState(todayStr);

  // Student Filter State
  const [studentQuery, setStudentQuery] = useState(initialStudentId);

  // Data & State
  const [attendanceSummary, setAttendanceSummary] = useState(null);
  const [studentHistoryRecords, setStudentHistoryRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAttendanceByDate = async (dateStr) => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getAttendanceByDate(dateStr);
      setAttendanceSummary(data);
    } catch (err) {
      setError(err.message || `Failed to fetch attendance for ${dateStr}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchStudentHistory = async (studentId) => {
    if (!studentId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const records = await apiService.getStudentAttendanceHistory(studentId.trim());
      setStudentHistoryRecords(records || []);
    } catch (err) {
      setError(err.message || `Failed to fetch attendance history for student ${studentId}`);
      setStudentHistoryRecords([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (viewMode === 'date') {
      fetchAttendanceByDate(selectedDate);
    } else if (viewMode === 'student' && studentQuery.trim()) {
      fetchStudentHistory(studentQuery);
    }
  }, [viewMode, selectedDate]);

  const handleStudentSearchSubmit = (e) => {
    e.preventDefault();
    if (studentQuery.trim()) {
      fetchStudentHistory(studentQuery);
    }
  };

  const dateColumns = [
    {
      key: 'student_id',
      label: 'Student ID',
      render: (row) => (
        <span className="font-mono font-semibold text-xs bg-slate-100 text-slate-800 px-2.5 py-1 rounded-md border border-slate-200">
          {row.student_id}
        </span>
      ),
    },
    {
      key: 'student_name',
      label: 'Student Name',
      render: (row) => (
        <span className="font-medium text-slate-900">{row.student_name || '—'}</span>
      ),
    },
    {
      key: 'attendance_date',
      label: 'Date',
      render: (row) => (
        <span className="text-xs text-slate-500 font-mono">{row.attendance_date}</span>
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

  const studentHistoryColumns = [
    {
      key: 'attendance_date',
      label: 'Session Date',
      render: (row) => (
        <div className="flex items-center gap-2 text-xs font-mono font-semibold text-slate-800">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <span>{row.attendance_date}</span>
        </div>
      ),
    },
    {
      key: 'attendance_time',
      label: 'Time Verified',
      render: (row) => (
        <div className="flex items-center gap-1.5 text-xs text-slate-500 font-mono">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{row.attendance_time}</span>
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Recorded Status',
      render: (row) => (
        <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          {row.status}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Attendance Logs & Historical Records
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Query verified presence records from MySQL by calendar date or individual student.
          </p>
        </div>

        {/* View Mode Toggle Buttons */}
        <div className="inline-flex p-1 bg-white border border-slate-200 rounded-xl shadow-2xs">
          <button
            onClick={() => {
              setViewMode('date');
              setSearchParams({});
            }}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 ${
              viewMode === 'date'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>By Date</span>
          </button>
          <button
            onClick={() => setViewMode('student')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all flex items-center gap-2 ${
              viewMode === 'student'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>By Student</span>
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 flex items-start gap-3 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block">Query Error</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* View Mode 1: Query by Calendar Date */}
      {viewMode === 'date' && (
        <div className="space-y-6">
          {/* Date Picker Bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5 shrink-0">
                <Filter className="w-3.5 h-3.5 text-indigo-600" />
                <span>Select Date:</span>
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500 font-medium text-slate-800"
              />
              <button
                onClick={() => setSelectedDate(todayStr)}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium px-2 py-1 rounded hover:bg-indigo-50 transition-colors"
              >
                Today
              </button>
            </div>

            <button
              onClick={() => fetchAttendanceByDate(selectedDate)}
              className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh Date</span>
            </button>
          </div>

          {/* Metric Summary Cards for Selected Date */}
          {attendanceSummary && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <StatCard
                title="Total Enrolled"
                value={attendanceSummary.total_students}
                icon={Users}
                color="indigo"
                subtext={`Status on ${attendanceSummary.date}`}
              />
              <StatCard
                title="Present"
                value={attendanceSummary.total_present}
                icon={UserCheck}
                color="emerald"
                subtext="Verified via face recognition"
              />
              <StatCard
                title="Absent"
                value={attendanceSummary.total_absent}
                icon={UserX}
                color="rose"
                subtext="Not marked for this date"
              />
            </div>
          )}

          {/* Attendance Table */}
          <DataTable
            columns={dateColumns}
            data={attendanceSummary?.records || []}
            loading={loading}
            emptyMessage={`No attendance entries for ${selectedDate}`}
            emptySubtext="Use Face Recognition to mark attendance for enrolled students on this date."
          />
        </div>
      )}

      {/* View Mode 2: Student Attendance History */}
      {viewMode === 'student' && (
        <div className="space-y-6">
          {/* Search Form */}
          <form
            onSubmit={handleStudentSearchSubmit}
            className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center gap-3"
          >
            <div className="relative flex-1 w-full">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Enter Student ID (e.g. CS101, ME101)..."
                value={studentQuery}
                onChange={(e) => setStudentQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500 font-medium text-slate-800"
              />
            </div>
            <button
              type="submit"
              className="w-full sm:w-auto px-5 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 shadow-xs transition-colors"
            >
              Search History
            </button>
          </form>

          {/* Student History Table */}
          <DataTable
            columns={studentHistoryColumns}
            data={studentHistoryRecords}
            loading={loading}
            emptyMessage={
              studentQuery
                ? `No attendance history found for student '${studentQuery}'`
                : 'Enter a Student ID to inspect historical attendance'
            }
            emptySubtext="Once students are recognized, their attendance history will be listed chronologically."
          />
        </div>
      )}
    </div>
  );
}
