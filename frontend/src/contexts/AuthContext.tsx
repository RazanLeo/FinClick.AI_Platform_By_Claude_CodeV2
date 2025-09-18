import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiService, ApiResponse } from '../services/api';
import toast from 'react-hot-toast';

// Types
interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  company?: string;
  phone?: string;
  role: 'user' | 'admin';
  subscription: {
    plan: 'free' | 'professional' | 'enterprise';
    status: 'active' | 'inactive' | 'cancelled';
    expiresAt?: string;
  };
  preferences: {
    language: 'ar' | 'en';
    theme: 'light' | 'dark' | 'system';
    notifications: boolean;
  };
  createdAt: string;
  updatedAt: string;
}

interface LoginCredentials {
  email: string;
  password: string;
  remember?: boolean;
}

interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  company?: string;
  phone?: string;
  agreeToTerms: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, password: string) => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  refreshUser: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth API functions using the integrated API service
const authAPI = {
  login: async (credentials: LoginCredentials) => {
    const response = await apiService.login(credentials);
    if (response.success) {
      return response.data;
    }
    throw new Error(response.message || 'Login failed');
  },

  register: async (data: RegisterData) => {
    const response = await apiService.register(data);
    if (response.success) {
      return response.data;
    }
    throw new Error(response.message || 'Registration failed');
  },

  logout: async () => {
    const response = await apiService.logout();
    if (!response.success) {
      throw new Error(response.message || 'Logout failed');
    }
  },

  forgotPassword: async (email: string) => {
    const response = await apiService.forgotPassword(email);
    if (response.success) {
      return response.data;
    }
    throw new Error(response.message || 'Password reset request failed');
  },

  resetPassword: async (token: string, password: string) => {
    const response = await apiService.resetPassword(token, password);
    if (response.success) {
      return response.data;
    }
    throw new Error(response.message || 'Password reset failed');
  },

  getUser: async (): Promise<User> => {
    const response = await apiService.getProfile();
    if (response.success) {
      return response.data.user;
    }
    throw new Error(response.message || 'Failed to get user profile');
  },

  updateProfile: async (data: Partial<User>) => {
    const response = await apiService.updateProfile(data);
    if (response.success) {
      return response.data;
    }
    throw new Error(response.message || 'Profile update failed');
  },

  refreshToken: async () => {
    const response = await apiService.refreshToken();
    if (response.success) {
      return response.data;
    }
    throw new Error(response.message || 'Token refresh failed');
  },
};

// Auth Provider Component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const queryClient = useQueryClient();

  // Check for existing auth token on mount
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      queryClient.invalidateQueries('user');
    }
  }, [queryClient]);

  // User query
  const {
    data: userData,
    isLoading,
    error,
  } = useQuery(
    'user',
    authAPI.getUser,
    {
      enabled: !!localStorage.getItem('auth_token'),
      retry: false,
      onSuccess: (data) => {
        setUser(data);
      },
      onError: () => {
        localStorage.removeItem('auth_token');
        setUser(null);
      },
    }
  );

  // Login mutation
  const loginMutation = useMutation(authAPI.login, {
    onSuccess: (data) => {
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('user_data', JSON.stringify(data.user));
      setUser(data.user);
      queryClient.setQueryData('user', data.user);
      toast.success('تم تسجيل الدخول بنجاح');
    },
    onError: (error: any) => {
      const message = error.message || 'خطأ في تسجيل الدخول';
      toast.error(message);
    },
  });

  // Register mutation
  const registerMutation = useMutation(authAPI.register, {
    onSuccess: (data) => {
      localStorage.setItem('auth_token', data.access_token);
      localStorage.setItem('user_data', JSON.stringify(data.user));
      setUser(data.user);
      queryClient.setQueryData('user', data.user);
      toast.success('تم إنشاء الحساب بنجاح');
    },
    onError: (error: any) => {
      const message = error.message || 'خطأ في إنشاء الحساب';
      toast.error(message);
    },
  });

  // Logout mutation
  const logoutMutation = useMutation(authAPI.logout, {
    onSettled: () => {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      setUser(null);
      queryClient.clear();
      // Cleanup API service
      apiService.cleanup();
      toast.success('تم تسجيل الخروج بنجاح');
    },
  });

  // Forgot password mutation
  const forgotPasswordMutation = useMutation(authAPI.forgotPassword, {
    onSuccess: () => {
      toast.success('تم إرسال رابط استعادة كلمة المرور إلى بريدك الإلكتروني');
    },
    onError: (error: any) => {
      const message = error.message || 'خطأ في إرسال رابط الاستعادة';
      toast.error(message);
    },
  });

  // Reset password mutation
  const resetPasswordMutation = useMutation(
    ({ token, password }: { token: string; password: string }) =>
      authAPI.resetPassword(token, password),
    {
      onSuccess: () => {
        toast.success('تم تغيير كلمة المرور بنجاح');
      },
      onError: (error: any) => {
        const message = error.message || 'خطأ في تغيير كلمة المرور';
        toast.error(message);
      },
    }
  );

  // Update profile mutation
  const updateProfileMutation = useMutation(authAPI.updateProfile, {
    onSuccess: (data) => {
      setUser(data.user);
      queryClient.setQueryData('user', data.user);
      toast.success('تم تحديث الملف الشخصي بنجاح');
    },
    onError: (error: any) => {
      const message = error.message || 'خطأ في تحديث الملف الشخصي';
      toast.error(message);
    },
  });

  // Context methods
  const login = async (credentials: LoginCredentials) => {
    await loginMutation.mutateAsync(credentials);
  };

  const register = async (data: RegisterData) => {
    await registerMutation.mutateAsync(data);
  };

  const logout = () => {
    logoutMutation.mutate();
  };

  const forgotPassword = async (email: string) => {
    await forgotPasswordMutation.mutateAsync(email);
  };

  const resetPassword = async (token: string, password: string) => {
    await resetPasswordMutation.mutateAsync({ token, password });
  };

  const updateProfile = async (data: Partial<User>) => {
    await updateProfileMutation.mutateAsync(data);
  };

  const refreshUser = async () => {
    await queryClient.invalidateQueries('user');
  };

  const contextValue: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    updateProfile,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;