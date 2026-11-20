# Face Recognition Attendance System — React Frontend

A modern, responsive React + Vite SaaS dashboard for automated biometric attendance management, integrated directly with the FastAPI + MySQL backend.

---

## 1. Features
- **User Authentication:** Modern Login (`/login`) and Register (`/register`) pages with client-side validation, password visibility toggle, remember-me support, JWT token persistence, and automatic session restoration.
- **Protected Routing:** Unauthenticated visitors are automatically redirected to `/login`. Authenticated users are prevented from returning to `/login` or `/register` and can log out from the Navbar or Sidebar.
- **Dashboard Overview:** Real-time statistics (Total Enrolled, Present Today, Absent Today, Attendance Rate) and today's verified attendance live feed.
- **Student Management:** Full student directory, search filter by name or roll number, student profile view, and deletion with cascading removal of dataset images.
- **Student Enrollment:** Student registration form with strict validation, multi-photo face sample uploader, and one-click LBPH model retraining trigger.
- **Biometric Face Recognition:** Drag-and-drop facial snapshot uploader, client image preview, configurable LBPH distance threshold slider, real-time result cards, and duplicate attendance prevention alerts.
- **Attendance Records:** Daily calendar filter, presence summary counters, and historical student attendance timeline queries.
- **System Architecture & Settings:** Live backend health status, MySQL connection details, computer vision parameters, and model retrain controls.

---

## 2. Technology Stack
- **Framework:** React 19 + Vite
- **Routing:** React Router DOM v7
- **Authentication:** JWT Access Tokens, React Context API (`AuthContext`), Protected & Public Route guards
- **Styling:** Tailwind CSS v4
- **Icons:** Lucide React
- **HTTP Client:** Axios (centralized in `src/services/api.js` with Bearer token interceptor)

---

## 3. Getting Started

### Prerequisites
- Node.js (v18+ or v24+)
- Running FastAPI backend on `http://127.0.0.1:8000`

### Installation
```bash
cd frontend
npm install
```

### Environment Configuration
Ensure `.env` exists in `frontend/`:
```ini
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### Running the Development Server
```bash
npm run dev
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173) in your browser.

---

## 4. Production Build
```bash
npm run build
npm run preview
```
