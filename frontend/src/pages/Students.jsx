import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Search,
  UserPlus,
  Trash2,
  Calendar,
  AlertCircle,
  RefreshCw,
  CheckCircle2,
  Clock,
  History,
} from 'lucide-react';
import DataTable from '../components/DataTable';
import { apiService } from '../services/api';

export default function Students() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);

  // Modal State for Delete Confirmation
  const [studentToDelete, setStudentToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchStudents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getStudents();
      setStudents(data || []);
    } catch (err) {
      setError(err.message || 'Failed to retrieve students from MySQL.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  const handleDeleteConfirm = async () => {
    if (!studentToDelete) return;
    setDeleting(true);
    try {
      const result = await apiService.deleteStudent(studentToDelete.student_id);
      setNotification({
        type: 'success',
        message: result.message || `Student ${studentToDelete.student_id} successfully deleted.`,
      });
      setStudents((prev) => prev.filter((s) => s.student_id !== studentToDelete.student_id));
      setStudentToDelete(null);
    } catch (err) {
      setNotification({
        type: 'error',
        message: err.message || 'Failed to delete student.',
      });
    } finally {
      setDeleting(false);
      setTimeout(() => setNotification(null), 5000);
    }
  };

  const filteredStudents = students.filter((s) => {
    const q = searchQuery.toLowerCase();
    return (
      (s.student_id && s.student_id.toLowerCase().includes(q)) ||
      (s.name && s.name.toLowerCase().includes(q))
    );
  });

  const columns = [
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
      key: 'name',
      label: 'Student Name',
      render: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-700 font-semibold text-xs flex items-center justify-center shrink-0">
            {row.name ? row.name.charAt(0).toUpperCase() : 'S'}
          </div>
          <div>
            <span className="font-medium text-slate-900 block">{row.name}</span>
            <span className="text-[11px] text-slate-400">ID #{row.id}</span>
          </div>
        </div>
      ),
    },
    {
      key: 'created_at',
      label: 'Enrolled On',
      render: (row) => {
        const dateStr = row.created_at
          ? new Date(row.created_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
            })
          : '—';
        return (
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>{dateStr}</span>
          </div>
        );
      },
    },
    {
      key: 'actions',
      label: 'Actions',
      className: 'text-right',
      render: (row) => (
        <div className="flex items-center justify-end gap-2">
          <Link
            to={`/attendance?student_id=${encodeURIComponent(row.student_id)}`}
            className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
            title="View Attendance History"
          >
            <History className="w-4 h-4" />
          </Link>
          <button
            onClick={() => setStudentToDelete(row)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
            title="Delete Student"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Student Management
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            View, search, and manage registered student profiles in MySQL.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchStudents}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
          <Link
            to="/register-student"
            className="inline-flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 shadow-xs transition-colors"
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>Add Student</span>
          </Link>
        </div>
      </div>

      {/* Notifications */}
      {notification && (
        <div
          className={`p-4 rounded-xl border flex items-start gap-3 text-xs ${
            notification.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {notification.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          )}
          <span>{notification.message}</span>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 flex items-start gap-3 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block">Error Loading Data</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Search Bar & Count Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-xs">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by student name or roll number..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all text-slate-800"
          />
        </div>
        <div className="text-xs text-slate-500 px-2">
          Showing <span className="font-semibold text-slate-800">{filteredStudents.length}</span> of{' '}
          <span className="font-semibold text-slate-800">{students.length}</span> students
        </div>
      </div>

      {/* Student Data Table */}
      <DataTable
        columns={columns}
        data={filteredStudents}
        loading={loading}
        emptyMessage={
          searchQuery
            ? 'No students match your search criteria'
            : 'No students registered in MySQL yet'
        }
        emptySubtext={
          searchQuery
            ? 'Try clearing the search query or verifying the student ID.'
            : 'Click "Add Student" above to register your first student record.'
        }
      />

      {/* Delete Confirmation Modal */}
      {studentToDelete && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mb-4">
              <Trash2 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900">
              Confirm Student Deletion
            </h3>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Are you sure you want to delete{' '}
              <strong className="text-slate-800">{studentToDelete.name}</strong> (ID:{' '}
              <code className="text-indigo-600 bg-indigo-50 px-1 py-0.5 rounded">
                {studentToDelete.student_id}
              </code>
              )? This will permanently remove their records and facial training samples from disk.
            </p>

            <div className="mt-6 flex items-center justify-end gap-3">
              <button
                onClick={() => setStudentToDelete(null)}
                disabled={deleting}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={deleting}
                className="px-4 py-2 text-xs font-semibold text-white bg-rose-600 rounded-lg hover:bg-rose-700 shadow-xs transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {deleting && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                <span>{deleting ? 'Deleting...' : 'Delete Student'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
