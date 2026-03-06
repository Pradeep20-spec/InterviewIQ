import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi, User } from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = sessionStorage.getItem('interviewiq_token');
      const savedUser = sessionStorage.getItem('interviewiq_user');

      if (token && savedUser) {
        try {
          // Validate token with backend
          const result = await authApi.getMe();
          if (result.success && result.data) {
            setUser(result.data);
          } else {
            // Token invalid — use saved user data as fallback (offline mode)
            setUser(JSON.parse(savedUser));
          }
        } catch {
          // Backend unreachable — use cached user
          setUser(JSON.parse(savedUser));
        }
      }
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const result = await authApi.login(email, password);
    if (result.success && result.data) {
      sessionStorage.setItem('interviewiq_token', result.data.token);
      sessionStorage.setItem('interviewiq_user', JSON.stringify(result.data.user));
      setUser(result.data.user);
      return { success: true };
    }
    return { success: false, error: result.error || 'Login failed' };
  };

  const register = async (name: string, email: string, password: string) => {
    const result = await authApi.register(name, email, password);
    if (result.success && result.data) {
      sessionStorage.setItem('interviewiq_token', result.data.token);
      sessionStorage.setItem('interviewiq_user', JSON.stringify(result.data.user));
      setUser(result.data.user);
      return { success: true };
    }
    return { success: false, error: result.error || 'Registration failed' };
  };

  const logout = () => {
    sessionStorage.removeItem('interviewiq_token');
    sessionStorage.removeItem('interviewiq_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
