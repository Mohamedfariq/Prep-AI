import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import type { User } from '../types/api';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string, remember: boolean) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

interface RegisterPayload {
  name: string;
  email: string;
  graduation_year: number;
  branch: string;
  password: string;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('prepai_token') || sessionStorage.getItem('prepai_token');
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get('/api/auth/me')
      .then((response) => setUser(response.data))
      .catch(() => {
        localStorage.removeItem('prepai_token');
        sessionStorage.removeItem('prepai_token');
      })
      .finally(() => setLoading(false));
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      async login(email, password, remember) {
        const response = await api.post('/api/auth/login', { email, password, remember });
        const storage = remember ? localStorage : sessionStorage;
        storage.setItem('prepai_token', response.data.access_token);
        setUser(response.data.user);
      },
      async register(payload) {
        const response = await api.post('/api/auth/register', payload);
        localStorage.setItem('prepai_token', response.data.access_token);
        setUser(response.data.user);
      },
      logout() {
        localStorage.removeItem('prepai_token');
        sessionStorage.removeItem('prepai_token');
        setUser(null);
      },
    }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside AuthProvider');
  return value;
}
