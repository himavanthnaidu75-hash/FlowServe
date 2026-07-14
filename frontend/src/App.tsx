import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Component, ReactNode, useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import { AppShell } from './components/layout/AppShell';
import { ToastContainer } from './components/ui/Toast';
import { api } from './lib/api';

import Landing from './pages/Landing';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Clients from './pages/Clients';
import Proposals from './pages/Proposals';
import Invoices from './pages/Invoices';
import TimeTracking from './pages/TimeTracking';
import Settings from './pages/Settings';
import ClientPortal from './pages/ClientPortal';
import Leads from './pages/Leads';
import Analytics from './pages/Analytics';
import Notifications from './pages/Notifications';
import Contracts from './pages/Contracts';

const queryClient = new QueryClient();

const AuthLoader = ({ children }: { children: ReactNode }) => {
  const token = useAuthStore((s) => s.token);
  const setUser = useAuthStore((s) => s.setUser);

  useEffect(() => {
    if (token) {
      api.get('/auth/me').then(({ data }) => {
        setUser(data);
      }).catch(() => {
        useAuthStore.getState().logout();
      });
    }
  }, [token, setUser]);

  return <>{children}</>;
};

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const token = useAuthStore.getState().token;
  if (!token) return <Navigate to="/auth" replace />;
  return <>{children}</>;
};

const PublicRoute = ({ children }: { children: ReactNode }) => {
  const token = useAuthStore.getState().token;
  if (token) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

class ErrorBoundary extends Component<{children: ReactNode}, {hasError: boolean}> {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-bg-primary text-white">
          <h1 className="text-4xl font-bold text-red-500 mb-4">SYSTEM FAILURE</h1>
          <p className="text-gray-400 mb-6">Something went wrong.</p>
          <button onClick={() => window.location.reload()} className="btn-primary">Reload Application</button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthLoader>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/auth" element={<PublicRoute><Auth /></PublicRoute>} />
              <Route path="/portal/:token" element={<ClientPortal />} />
              
              <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/leads" element={<Leads />} />
                <Route path="/projects" element={<Projects />} />
                <Route path="/clients" element={<Clients />} />
                <Route path="/proposals" element={<Proposals />} />
                <Route path="/invoices" element={<Invoices />} />
                <Route path="/contracts" element={<Contracts />} />
                <Route path="/time" element={<TimeTracking />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/notifications" element={<Notifications />} />
                <Route path="/settings" element={<Settings />} />
              </Route>
              
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
            <ToastContainer />
          </BrowserRouter>
        </AuthLoader>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
