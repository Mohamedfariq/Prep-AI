import React from 'react';
import ReactDOM from 'react-dom/client';
import { Navigate, RouterProvider, createBrowserRouter } from 'react-router-dom';
import './styles.css';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AppLayout } from './layouts/AppLayout';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Companies } from './pages/Companies';
import { CompanyDetail } from './pages/CompanyDetail';
import { Practice } from './pages/Practice';
import { PersonalizedOA } from './pages/PersonalizedOA';
import { Assessment } from './pages/Assessment';
import { Interview } from './pages/Interview';
import { SkillProfile } from './pages/SkillProfile';
import { Performance } from './pages/Performance';
import { Recommendations } from './pages/Recommendations';
import { QuestionBank } from './pages/QuestionBank';
import { Settings } from './pages/Settings';

const router = createBrowserRouter([
  { path: '/', element: <Navigate to="/dashboard" replace /> },
  { path: '/login', element: <Login /> },
  { path: '/register', element: <Register /> },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'companies', element: <Companies /> },
      { path: 'companies/:companyId', element: <CompanyDetail /> },
      { path: 'practice', element: <Practice /> },
      { path: 'personalized-oa', element: <PersonalizedOA /> },
      { path: 'personalized-oa/:assessmentId', element: <Assessment /> },
      { path: 'interview', element: <Interview /> },
      { path: 'skill-profile', element: <SkillProfile /> },
      { path: 'performance', element: <Performance /> },
      { path: 'recommendations', element: <Recommendations /> },
      { path: 'question-bank', element: <QuestionBank /> },
      { path: 'settings', element: <Settings /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </React.StrictMode>,
);
