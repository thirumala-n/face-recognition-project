import React, { useState, useRef } from 'react';
import {
  ScanFace,
  Upload,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Sliders,
  RefreshCw,
  HelpCircle,
  FileCheck,
} from 'lucide-react';
import { apiService } from '../services/api';

export default function FaceRecognition() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [threshold, setThreshold] = useState(60.0);
  const [showThresholdSettings, setShowThresholdSettings] = useState(false);
  const [recognizing, setRecognizing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [recentScans, setRecentScans] = useState([]);

  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file (JPEG or PNG).');
      return;
    }
    setError(null);
    setResult(null);
    setSelectedFile(file);

    const reader = new FileReader();
    reader.onload = () => {
      setPreviewUrl(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleRecognize = async () => {
    if (!selectedFile) {
      setError('Please select or upload an image first.');
      return;
    }

    setRecognizing(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiService.recognizeAndMarkAttendance(selectedFile, threshold);
      setResult(response);

      // Append to local session recent scans
      setRecentScans((prev) => [
        {
          id: Date.now(),
          time: new Date().toLocaleTimeString(),
          result: response,
          fileName: selectedFile.name,
        },
        ...prev.slice(0, 4),
      ]);
    } catch (err) {
      setError(err.message || 'Face recognition request failed.');
    } finally {
      setRecognizing(false);
    }
  };

  const resetSelection = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Page Title & Explanation */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Biometric Face Recognition
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Upload a facial photo to execute real-time Haar Cascade localization & LBPH matching.
          </p>
        </div>
        <button
          onClick={() => setShowThresholdSettings(!showThresholdSettings)}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors self-start"
        >
          <Sliders className="w-3.5 h-3.5 text-indigo-600" />
          <span>Recognition Threshold ({threshold})</span>
        </button>
      </div>

      {/* Threshold Setting Drawer */}
      {showThresholdSettings && (
        <div className="p-4 bg-white rounded-xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800">
              LBPH Distance Cutoff Threshold: {threshold}
            </span>
            <span className="text-[11px] text-slate-500 font-normal">
              Lower distance = Closer histogram match (0.0 is identical)
            </span>
          </div>
          <input
            type="range"
            min="30"
            max="100"
            step="1"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-full accent-indigo-600 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400">
            <span>30 (Strict match)</span>
            <span>60 (Recommended default)</span>
            <span>100 (Permissive)</span>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 flex items-start gap-3 text-xs">
          <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block">Recognition Error</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Main Grid: Upload Zone (Left) & Recognition Result (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Upload & Preview Card (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
              <ScanFace className="w-4 h-4 text-indigo-600" />
              <span>Face Image Input</span>
            </h3>

            {/* Drag & Drop Area */}
            {!previewUrl ? (
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-200 rounded-xl p-10 text-center hover:border-indigo-400 hover:bg-slate-50/50 transition-all cursor-pointer flex flex-col items-center justify-center min-h-[280px]"
              >
                <div className="w-14 h-14 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
                  <Upload className="w-6 h-6" />
                </div>
                <p className="text-sm font-semibold text-slate-800">
                  Drag and drop face image here
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  or click to browse from device (JPEG or PNG)
                </p>
                <span className="mt-4 px-3 py-1 bg-slate-100 text-slate-600 text-[11px] font-medium rounded-full">
                  Max file size: 10MB
                </span>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative rounded-xl overflow-hidden border border-slate-200 bg-slate-950 flex items-center justify-center max-h-[340px]">
                  <img
                    src={previewUrl}
                    alt="Face Preview"
                    className="object-contain max-h-[340px] w-full"
                  />
                  <button
                    onClick={resetSelection}
                    className="absolute top-3 right-3 px-2.5 py-1 text-xs font-semibold bg-slate-900/80 text-white rounded-lg hover:bg-slate-900 backdrop-blur-xs transition-colors"
                  >
                    Change Image
                  </button>
                </div>
                <p className="text-xs text-slate-500 truncate">
                  Selected file: <strong className="text-slate-800">{selectedFile?.name}</strong>
                </p>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/jpg"
              onChange={(e) => handleFileSelect(e.target.files?.[0])}
              className="hidden"
            />
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100">
            <button
              onClick={handleRecognize}
              disabled={!selectedFile || recognizing}
              className="w-full py-3 px-4 text-xs font-bold uppercase tracking-wider text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 shadow-sm transition-all flex items-center justify-center gap-2 disabled:opacity-40"
            >
              {recognizing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing Computer Vision Pipeline...</span>
                </>
              ) : (
                <>
                  <ScanFace className="w-4 h-4" />
                  <span>Recognize Face & Mark Attendance</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Output Verdict Card (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">
              Recognition Outcome
            </h3>

            {!result && !recognizing && (
              <div className="py-12 text-center text-slate-400">
                <HelpCircle className="w-10 h-10 mx-auto mb-2 text-slate-300" />
                <p className="text-xs font-medium">Awaiting image verification</p>
                <p className="text-[11px] text-slate-400 mt-1 max-w-xs mx-auto">
                  Upload an image and click recognize to view real-time LBPH prediction and MySQL attendance status.
                </p>
              </div>
            )}

            {recognizing && (
              <div className="py-12 text-center">
                <RefreshCw className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-3" />
                <p className="text-xs font-semibold text-slate-800">
                  Executing Haar Cascade & LBPH
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Extracting face ROI and computing histogram distance...
                </p>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                {/* Status Indicator Pill */}
                <div
                  className={`p-4 rounded-xl border flex items-start gap-3 ${
                    result.recognized && result.attendance_marked
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                      : result.recognized && !result.attendance_marked
                      ? 'bg-amber-50 border-amber-200 text-amber-900'
                      : 'bg-rose-50 border-rose-200 text-rose-900'
                  }`}
                >
                  {result.recognized && result.attendance_marked ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                  ) : result.recognized && !result.attendance_marked ? (
                    <Clock className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                  ) : (
                    <XCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                  )}

                  <div>
                    <span className="text-xs font-bold block uppercase tracking-wider">
                      {result.recognized && result.attendance_marked
                        ? 'Attendance Marked'
                        : result.recognized
                        ? 'Already Marked Today'
                        : 'Unknown Individual'}
                    </span>
                    <span className="text-xs leading-relaxed mt-0.5 block">
                      {result.message}
                    </span>
                  </div>
                </div>

                {/* Recognized Student Details Table */}
                {result.recognized && (
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-2.5 text-xs">
                    <div className="flex justify-between py-1 border-b border-slate-200/60">
                      <span className="text-slate-500">Student Name:</span>
                      <strong className="text-slate-900 text-sm font-bold">
                        {result.student_name}
                      </strong>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-200/60">
                      <span className="text-slate-500">Student ID:</span>
                      <code className="text-indigo-600 font-bold bg-indigo-50 px-1.5 py-0.5 rounded">
                        {result.student_id}
                      </code>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-200/60">
                      <span className="text-slate-500">LBPH Distance:</span>
                      <span className="font-semibold text-slate-800">
                        {result.confidence_distance}
                      </span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span className="text-slate-500">Configured Threshold:</span>
                      <span className="text-slate-600 font-mono">
                        {result.threshold}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Recent Session Scans */}
          {recentScans.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                Recent Scans (Current Session)
              </h4>
              <div className="space-y-2">
                {recentScans.map((scan) => (
                  <div
                    key={scan.id}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 text-xs border border-slate-100"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileCheck className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="font-medium text-slate-800 truncate">
                        {scan.result.student_name || 'Unknown Face'}
                      </span>
                    </div>
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        scan.result.recognized
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {scan.time}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
