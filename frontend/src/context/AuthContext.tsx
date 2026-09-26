import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface TokenData {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  role: string;
  tenant_id: string;
}

interface User {
  user_id: string;
  email: string;
  role: string;
  tenant_id: string;
  tenant_name?: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  tenantId: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [tenantId, setTenantId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing token on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedTenantId = localStorage.getItem('tenant_id');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedTenantId && storedUser) {
      setToken(storedToken);
      setTenantId(storedTenantId);
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data: TokenData = await response.json();

      // Store auth data
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('tenant_id', data.tenant_id);
      localStorage.setItem('user', JSON.stringify({
        user_id: data.user_id,
        email: data.email,
        role: data.role,
        tenant_id: data.tenant_id,
      }));

      // Update state
      setToken(data.access_token);
      setTenantId(data.tenant_id);
      setUser({
        user_id: data.user_id,
        email: data.email,
        role: data.role,
        tenant_id: data.tenant_id,
      });
      setIsAuthenticated(true);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('tenant_id');
    localStorage.removeItem('user');

    setToken(null);
    setTenantId(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        user,
        token,
        tenantId,
        login,
        logout,
        loading,
        error,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
