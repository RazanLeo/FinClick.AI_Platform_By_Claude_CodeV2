/**
 * Enhanced API Service for FinClick.AI Platform
 * خدمة API محسّنة لمنصة FinClick.AI
 *
 * This service manages all API communications between frontend and backend services.
 * تدير هذه الخدمة جميع اتصالات API بين الواجهة الأمامية وخدمات الخلفية.
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

// Types for API communication
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
  warnings?: string[];
  metadata?: any;
}

export interface AnalysisRequest {
  user_id: string;
  analysis_type: 'comprehensive' | 'quick' | 'risk_assessment' | 'valuation';
  data_source: string;
  company_data: any;
  analysis_options?: any;
  priority?: number;
}

export interface AnalysisResponse {
  request_id: string;
  status: 'queued' | 'processing' | 'completed' | 'error';
  results?: any;
  execution_time_ms?: number;
  errors?: string[];
  warnings?: string[];
  progress?: string;
  estimated_completion_time?: string;
}

export interface FileUploadRequest {
  file: File;
  file_type: 'financial_statement' | 'balance_sheet' | 'income_statement' | 'cash_flow';
  company_id?: string;
  extract_text?: boolean;
}

export interface FileUploadResponse {
  file_id: string;
  filename: string;
  file_size: number;
  upload_url?: string;
  extracted_text?: string;
  extracted_data?: any;
  processing_status: 'uploaded' | 'processing' | 'completed' | 'error';
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  analyses_per_month: number;
  features: string[];
  is_popular?: boolean;
}

export interface UserSubscription {
  plan_id: string;
  status: 'active' | 'inactive' | 'cancelled' | 'past_due';
  current_period_start: string;
  current_period_end: string;
  analyses_used: number;
  analyses_remaining: number;
}

class ApiService {
  private client: AxiosInstance;
  private websocket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor() {
    // Create axios instance with base configuration
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });

    this.setupInterceptors();
    this.initializeWebSocket();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add request timestamp
        config.headers['X-Request-Timestamp'] = new Date().toISOString();

        // Add user agent info
        config.headers['X-User-Agent'] = navigator.userAgent;

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error) => {
        // Handle common error responses
        if (error.response) {
          const { status, data } = error.response;

          switch (status) {
            case 401:
              // Unauthorized - redirect to login
              localStorage.removeItem('auth_token');
              window.location.href = '/auth?mode=login';
              toast.error('Session expired. Please login again.');
              break;

            case 403:
              // Forbidden
              toast.error('Access denied. Insufficient permissions.');
              break;

            case 429:
              // Rate limited
              toast.error('Too many requests. Please try again later.');
              break;

            case 500:
              // Server error
              toast.error('Server error. Please try again later.');
              break;

            default:
              // Other errors
              const message = data?.message || 'An unexpected error occurred';
              toast.error(message);
          }
        } else if (error.request) {
          // Network error
          toast.error('Network error. Please check your connection.');
        }

        return Promise.reject(error);
      }
    );
  }

  private initializeWebSocket(): void {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    const userId = this.getCurrentUserId();

    if (!userId) return;

    try {
      this.websocket = new WebSocket(`${wsUrl}/ws/${userId}`);

      this.websocket.onopen = () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.websocket.onclose = () => {
        console.log('❌ WebSocket disconnected');
        this.reconnectWebSocket();
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
    }
  }

  private reconnectWebSocket(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000; // Exponential backoff

      setTimeout(() => {
        console.log(`Attempting WebSocket reconnection (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.initializeWebSocket();
      }, delay);
    }
  }

  private handleWebSocketMessage(data: any): void {
    // Handle different types of WebSocket messages
    switch (data.type) {
      case 'analysis_started':
        toast.success('Analysis started processing');
        // Emit custom event for components to listen
        window.dispatchEvent(new CustomEvent('analysisStarted', { detail: data }));
        break;

      case 'analysis_completed':
        toast.success('Analysis completed successfully');
        window.dispatchEvent(new CustomEvent('analysisCompleted', { detail: data }));
        break;

      case 'analysis_error':
        toast.error(`Analysis failed: ${data.error}`);
        window.dispatchEvent(new CustomEvent('analysisError', { detail: data }));
        break;

      case 'file_processed':
        toast.success('File processed successfully');
        window.dispatchEvent(new CustomEvent('fileProcessed', { detail: data }));
        break;

      default:
        console.log('Received WebSocket message:', data);
    }
  }

  private getCurrentUserId(): string | null {
    // Get user ID from stored user data
    const userData = localStorage.getItem('user_data');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        return user.id;
      } catch (error) {
        return null;
      }
    }
    return null;
  }

  // Authentication API methods
  async login(credentials: { email: string; password: string; remember?: boolean }): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/api/auth/login', credentials);
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Login failed' };
    }
  }

  async register(userData: any): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/api/auth/register', userData);
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Registration failed' };
    }
  }

  async logout(): Promise<ApiResponse> {
    try {
      await this.client.post('/api/auth/logout');
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');

      // Close WebSocket connection
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }

      return { success: true };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Logout failed' };
    }
  }

  async refreshToken(): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/api/auth/refresh');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Token refresh failed' };
    }
  }

  async forgotPassword(email: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/api/auth/forgot-password', { email });
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Request failed' };
    }
  }

  async resetPassword(token: string, password: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/api/auth/reset-password', { token, password });
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Password reset failed' };
    }
  }

  // User Profile API methods
  async getProfile(): Promise<ApiResponse> {
    try {
      const response = await this.client.get('/api/auth/profile');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to get profile' };
    }
  }

  async updateProfile(profileData: any): Promise<ApiResponse> {
    try {
      const response = await this.client.put('/api/auth/profile', profileData);
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Profile update failed' };
    }
  }

  // Analysis API methods
  async requestAnalysis(request: AnalysisRequest): Promise<ApiResponse<AnalysisResponse>> {
    try {
      const response = await this.client.post('/api/analysis/request', request);
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Analysis request failed' };
    }
  }

  async getAnalysisStatus(requestId: string): Promise<ApiResponse<AnalysisResponse>> {
    try {
      const response = await this.client.get(`/api/analysis/status/${requestId}`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to get analysis status' };
    }
  }

  async getAnalysisHistory(page: number = 1, limit: number = 20): Promise<ApiResponse> {
    try {
      const response = await this.client.get('/api/analysis/history', {
        params: { page, limit }
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to get analysis history' };
    }
  }

  async cancelAnalysis(requestId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post(`/api/analysis/cancel/${requestId}`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to cancel analysis' };
    }
  }

  // File Upload API methods
  async uploadFile(request: FileUploadRequest): Promise<ApiResponse<FileUploadResponse>> {
    try {
      const formData = new FormData();
      formData.append('file', request.file);
      formData.append('file_type', request.file_type);
      if (request.company_id) {
        formData.append('company_id', request.company_id);
      }
      if (request.extract_text !== undefined) {
        formData.append('extract_text', request.extract_text.toString());
      }

      const response = await this.client.post('/api/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
          // Emit upload progress event
          window.dispatchEvent(new CustomEvent('uploadProgress', {
            detail: { percent: percentCompleted, file: request.file.name }
          }));
        },
      });

      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'File upload failed' };
    }
  }

  async getFileStatus(fileId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.get(`/api/files/status/${fileId}`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to get file status' };
    }
  }

  async deleteFile(fileId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.delete(`/api/files/${fileId}`);
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to delete file' };
    }
  }

  // Subscription API methods
  async getSubscriptionPlans(): Promise<ApiResponse<SubscriptionPlan[]>> {
    try {
      const response = await this.client.get('/api/subscription/plans');
      return { success: true, data: response.data.plans };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to get subscription plans' };
    }
  }

  async getUserSubscription(): Promise<ApiResponse<UserSubscription>> {
    try {
      const response = await this.client.get('/api/subscription/current');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to get subscription' };
    }
  }

  async createSubscription(planId: string, paymentMethodId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/api/subscription/create', {
        plan_id: planId,
        payment_method_id: paymentMethodId
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Subscription creation failed' };
    }
  }

  async cancelSubscription(): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/api/subscription/cancel');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Subscription cancellation failed' };
    }
  }

  async updatePaymentMethod(paymentMethodId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.put('/api/subscription/payment-method', {
        payment_method_id: paymentMethodId
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Payment method update failed' };
    }
  }

  // Platform Status API methods
  async getPlatformStatus(): Promise<ApiResponse> {
    try {
      const response = await this.client.get('/api/platform/status');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to get platform status' };
    }
  }

  async getSystemHealth(): Promise<ApiResponse> {
    try {
      const response = await this.client.get('/health');
      return { success: true, data: response.data };
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || 'Failed to get system health' };
    }
  }

  // Utility methods
  sendWebSocketMessage(message: any): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    }
  }

  // Event listeners for WebSocket messages
  addEventListener(eventType: string, callback: (event: CustomEvent) => void): void {
    window.addEventListener(eventType, callback as EventListener);
  }

  removeEventListener(eventType: string, callback: (event: CustomEvent) => void): void {
    window.removeEventListener(eventType, callback as EventListener);
  }

  // Cleanup method
  cleanup(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }
}

// Create and export singleton instance
export const apiService = new ApiService();

// Export types for use in components
export type {
  ApiResponse,
  AnalysisRequest,
  AnalysisResponse,
  FileUploadRequest,
  FileUploadResponse,
  SubscriptionPlan,
  UserSubscription
};

export default apiService;