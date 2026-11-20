import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  UserPlus,
  Upload,
  CheckCircle2,
  AlertCircle,
  Cpu,
  ArrowRight,
  RefreshCw,
  Image as ImageIcon,
  ShieldCheck,
} from 'lucide-react';
import { apiService } from '../services/api';

export default function RegisterStudent() {
  const navigate = useNavigate();

  // Form State
  const [formData, setFormData] = useState({
    student_id: '',
    name: '',
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Success Registration State
  const [registeredStudent, setRegisteredStudent] = useState(null);

  // Step 2: Photo Enrollment State
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  // Model Training State
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState(null);

  // General Notification
  const [notification, setNotification] = useState(null);

  const validateForm = () => {
    const errs = {};
    const idClean = formData.student_id.trim();
    const nameClean = formData.name.trim();

    if (!idClean) {
      errs.student_id = 'Student ID is required';
    } else if (!/^[A-Za-z0-9_-]+$/.test(idClean)) {
      errs.student_id = 'ID must only contain alphanumeric characters, hyphens, or underscores';
    }

    if (!nameClean) {
      errs.name = 'Student Name is required';
    } else if (!/^[A-Za-z\s.\-]+$/.test(nameClean)) {
      errs.name = 'Name must only contain alphabetic characters, spaces, dots, or hyphens';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setSubmitting(true);
    setNotification(null);

    try {
      const response = await apiService.createStudent({
        student_id: formData.student_id.trim(),
        name: formData.name.trim(),
      });

      setRegisteredStudent(response);
      setNotification({
        type: 'success',
        message: `Student '${response.name}' (${response.student_id}) successfully enrolled in MySQL!`,
      });
    } catch (err) {
      setNotification({
        type: 'error',
        message: err.message || 'Failed to register student.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const handleUploadImages = async () => {
    if (!registeredStudent || selectedFiles.length === 0) return;

    setUploadingImages(true);
    setUploadResult(null);

    try {
      const res = await apiService.uploadStudentImages(
        registeredStudent.student_id,
        selectedFiles
      );
      setUploadResult({
        success: true,
        message: res.message || `Uploaded ${res.saved_face_samples} face samples.`,
      });
      setSelectedFiles([]);
    } catch (err) {
      setUploadResult({
        success: false,
        message: err.message || 'Failed to upload face samples.',
      });
    } finally {
      setUploadingImages(false);
    }
  };

  const handleTrainModel = async () => {
    setTraining(true);
    setTrainResult(null);

    try {
      const res = await apiService.trainModel();
      setTrainResult({
        success: true,
        message: `Model trained on ${res.total_images_trained} face images across ${res.students_trained?.length || 0} students!`,
      });
    } catch (err) {
      setTrainResult({
        success: false,
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
          Register New Student
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Step 1: Save student metadata in MySQL. Step 2: Upload facial samples and train LBPH model.
        </p>
      </div>

      {/* Global Notifications */}
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

      {/* Grid: Registration Form (Step 1) + Face Sample Upload (Step 2) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Step 1: Student Information Form */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-slate-100">
              <span className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">
                1
              </span>
              <h3 className="text-sm font-bold text-slate-900">
                Student Profile Information
              </h3>
            </div>

            <form onSubmit={handleRegisterSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Student ID / Roll Number <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. CS101, IT2024"
                  value={formData.student_id}
                  disabled={submitting || registeredStudent !== null}
                  onChange={(e) =>
                    setFormData({ ...formData, student_id: e.target.value })
                  }
                  className={`w-full px-3 py-2 text-xs bg-slate-50 border rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:bg-white text-slate-800 ${
                    errors.student_id ? 'border-rose-300 bg-rose-50/50' : 'border-slate-200'
                  }`}
                />
                {errors.student_id && (
                  <p className="text-[11px] text-rose-500 mt-1">{errors.student_id}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Full Student Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. John Doe"
                  value={formData.name}
                  disabled={submitting || registeredStudent !== null}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className={`w-full px-3 py-2 text-xs bg-slate-50 border rounded-lg focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:bg-white text-slate-800 ${
                    errors.name ? 'border-rose-300 bg-rose-50/50' : 'border-slate-200'
                  }`}
                />
                {errors.name && (
                  <p className="text-[11px] text-rose-500 mt-1">{errors.name}</p>
                )}
              </div>

              {registeredStudent ? (
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs">
                  <span className="font-semibold block">Registered Successfully:</span>
                  <span>
                    ID: <code>{registeredStudent.student_id}</code> | Name: {registeredStudent.name}
                  </span>
                </div>
              ) : (
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full mt-2 py-2.5 px-4 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 shadow-xs transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {submitting && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                  <span>{submitting ? 'Registering in MySQL...' : 'Save Student to MySQL'}</span>
                </button>
              )}
            </form>
          </div>

          {registeredStudent && (
            <button
              type="button"
              onClick={() => {
                setRegisteredStudent(null);
                setFormData({ student_id: '', name: '' });
                setUploadResult(null);
              }}
              className="mt-6 text-xs text-slate-500 hover:text-slate-800 underline text-center"
            >
              Enroll another student
            </button>
          )}
        </div>

        {/* Step 2: Facial Sample Enrollment & Model Retraining */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-slate-100">
              <span className="w-6 h-6 rounded-full bg-slate-800 text-white flex items-center justify-center text-xs font-bold">
                2
              </span>
              <h3 className="text-sm font-bold text-slate-900">
                Face Image Enrollment & Training
              </h3>
            </div>

            <p className="text-xs text-slate-500 mb-4 leading-relaxed">
              Upload face snapshots for this student. The backend extracts grayscale face ROIs
              and saves them into <code>TrainingImage/</code>.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Select Face Images (JPEG / PNG)
                </label>
                <input
                  type="file"
                  multiple
                  accept="image/jpeg,image/png,image/jpg"
                  onChange={handleFileChange}
                  disabled={!registeredStudent || uploadingImages}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 file:cursor-pointer cursor-pointer border border-slate-200 rounded-lg p-1.5"
                />
                {selectedFiles.length > 0 && (
                  <p className="text-[11px] text-indigo-600 mt-1 font-medium">
                    {selectedFiles.length} file(s) selected
                  </p>
                )}
              </div>

              <button
                type="button"
                onClick={handleUploadImages}
                disabled={!registeredStudent || selectedFiles.length === 0 || uploadingImages}
                className="w-full py-2.5 px-4 text-xs font-semibold text-slate-800 bg-slate-100 border border-slate-200 rounded-lg hover:bg-slate-200 transition-colors flex items-center justify-center gap-2 disabled:opacity-40"
              >
                {uploadingImages && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                <Upload className="w-3.5 h-3.5" />
                <span>{uploadingImages ? 'Uploading Samples...' : 'Upload Face Samples'}</span>
              </button>

              {uploadResult && (
                <div
                  className={`p-3 rounded-lg text-xs border ${
                    uploadResult.success
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                      : 'bg-rose-50 border-rose-200 text-rose-800'
                  }`}
                >
                  {uploadResult.message}
                </div>
              )}
            </div>
          </div>

          {/* Model Retraining Trigger */}
          <div className="mt-6 pt-4 border-t border-slate-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-indigo-600" />
                <span>LBPH Model Trainer</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mb-3">
              Re-train the facial recognizer to recognize newly uploaded faces.
            </p>
            <button
              type="button"
              onClick={handleTrainModel}
              disabled={training}
              className="w-full py-2.5 px-4 text-xs font-semibold text-white bg-slate-900 rounded-lg hover:bg-slate-800 shadow-xs transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {training && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
              <span>{training ? 'Training LBPH Model...' : 'Train / Update LBPH Model'}</span>
            </button>

            {trainResult && (
              <div
                className={`mt-3 p-3 rounded-lg text-xs border ${
                  trainResult.success
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                    : 'bg-rose-50 border-rose-200 text-rose-800'
                }`}
              >
                {trainResult.message}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
