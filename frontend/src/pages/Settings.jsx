import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Database,
  Cpu,
  ExternalLink,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Server,
  Layers,
  Code2,
} from 'lucide-react';
import { apiService } from '../services/api';

export default function Settings() {
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Retrain state
  const [training, setTraining] = useState(false);
  const [trainNotification, setTrainNotification] = useState(null);

  const fetchSystemInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getSystemStatus();
      setSystemInfo(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch backend configuration.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemInfo();
  }, []);

  const handleRetrain = async () => {
    setTraining(true);
    setTrainNotification(null);
    try {
      const res = await apiService.trainModel();
      setTrainNotification({
        type: 'success',
        message: `Successfully trained model on ${res.total_images_trained} face samples for ${res.students_trained?.length || 0} students!`,
      });
      fetchSystemInfo();
    } catch (err) {
      setTrainNotification({
        type: 'error',
        message: err.message || 'Model training failed.',
      });
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 tracking-tight">
          System Architecture & Settings
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Backend server diagnostics, computer vision parameters, and MySQL database connection.
        </p>
      </div>

      {/* Notifications */}
      {trainNotification && (
        <div
          className={`p-4 rounded-xl border flex items-start gap-3 text-xs ${
            trainNotification.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {trainNotification.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          )}
          <span>{trainNotification.message}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 flex items-start gap-3 text-xs">
          <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block">Connection Error</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backend & Database Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
            <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
              <Server className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                FastAPI Backend Service
              </h3>
              <span className="text-[11px] text-slate-400">
                Python 3.12 / Uvicorn ASGI Server
              </span>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">API Status:</span>
              <span className="inline-flex items-center gap-1.5 font-semibold text-emerald-600">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                {systemInfo?.status === 'online' ? 'Online & Running' : 'Offline'}
              </span>
            </div>

            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Database Engine:</span>
              <span className="font-semibold text-slate-800 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-indigo-600" />
                <span>MySQL 8.0 (`{systemInfo?.database || 'face_attendance'}`)</span>
              </span>
            </div>

            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Application Version:</span>
              <span className="font-mono text-slate-700">
                v{systemInfo?.version || '1.0.0'}
              </span>
            </div>

            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Interactive Swagger UI:</span>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="text-indigo-600 hover:text-indigo-800 font-semibold inline-flex items-center gap-1"
              >
                <span>/docs</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>

        {/* Computer Vision & LBPH Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                OpenCV & LBPH Pipeline
              </h3>
              <span className="text-[11px] text-slate-400">
                Classical Haar Cascade + Texture Histograms
              </span>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Model File (`Trainner.yml`):</span>
              <span
                className={`font-semibold ${
                  systemInfo?.model_loaded ? 'text-emerald-600' : 'text-amber-600'
                }`}
              >
                {systemInfo?.model_loaded ? 'Loaded in RAM' : 'Not Loaded / Untrained'}
              </span>
            </div>

            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Mapped Face Identities:</span>
              <span className="font-bold text-slate-800">
                {systemInfo?.mapped_identities ?? 0} students
              </span>
            </div>

            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Face Detector:</span>
              <span className="font-mono text-slate-700">
                haarcascade_frontalface_default
              </span>
            </div>

            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Distance Metric:</span>
              <span className="text-slate-700">Chi-Square (lower = closer)</span>
            </div>
          </div>

          <button
            onClick={handleRetrain}
            disabled={training}
            className="w-full mt-2 py-2 px-3 text-xs font-semibold text-white bg-slate-900 rounded-lg hover:bg-slate-800 shadow-xs transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {training && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
            <span>{training ? 'Training LBPH Model...' : 'Retrain LBPH Model Now'}</span>
          </button>
        </div>
      </div>

      {/* Tech Stack Reference Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-600" />
          <span>Full-Stack Architecture Overview</span>
        </h3>
        <p className="text-xs text-slate-500 leading-relaxed mb-4">
          This system was architected following enterprise clean code standards. The React frontend communicates strictly with the FastAPI asynchronous REST endpoints.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
              Frontend
            </span>
            <span className="font-semibold text-slate-800">React 19 + Vite</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
              Styling
            </span>
            <span className="font-semibold text-slate-800">Tailwind CSS v4</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
              Backend API
            </span>
            <span className="font-semibold text-slate-800">FastAPI + Pydantic</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">
              Database
            </span>
            <span className="font-semibold text-slate-800">MySQL 8.0</span>
          </div>
        </div>
      </div>
    </div>
  );
}
