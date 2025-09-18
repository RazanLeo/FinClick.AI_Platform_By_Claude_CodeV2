import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

// Types
interface AnalysisFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: string;
  status: 'uploading' | 'uploaded' | 'processing' | 'processed' | 'error';
  url?: string;
  error?: string;
}

interface AnalysisOptions {
  language: 'ar' | 'en';
  sector: string;
  activity: string;
  entityType: string;
  comparisonType: string;
  analysisTypes: string[];
  reportFormats: string[];
}

interface AnalysisResult {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  startedAt: string;
  completedAt?: string;
  options: AnalysisOptions;
  files: AnalysisFile[];
  results?: {
    summary: any;
    analyses: any[];
    charts: any[];
    reports: string[];
  };
  error?: string;
}

interface AnalysisContextType {
  currentAnalysis: AnalysisResult | null;
  files: AnalysisFile[];
  options: AnalysisOptions;
  isUploading: boolean;
  isAnalyzing: boolean;

  // File management
  uploadFiles: (files: File[]) => Promise<void>;
  removeFile: (fileId: string) => void;
  clearFiles: () => void;

  // Options management
  updateOptions: (newOptions: Partial<AnalysisOptions>) => void;
  resetOptions: () => void;

  // Analysis management
  startAnalysis: () => Promise<void>;
  getAnalysisResult: (analysisId: string) => Promise<AnalysisResult>;
  cancelAnalysis: () => void;

  // History
  getAnalysisHistory: () => any;
  recentAnalyses: AnalysisResult[];
}

// Default options
const defaultOptions: AnalysisOptions = {
  language: 'ar',
  sector: '',
  activity: '',
  entityType: '',
  comparisonType: 'industry',
  analysisTypes: ['comprehensive'],
  reportFormats: ['pdf'],
};

// Create context
const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

// API client
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  withCredentials: true,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Analysis API functions
const analysisAPI = {
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/analysis/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteFile: async (fileId: string) => {
    await api.delete(`/analysis/files/${fileId}`);
  },

  startAnalysis: async (options: AnalysisOptions, fileIds: string[]) => {
    const response = await api.post('/analysis/start', {
      options,
      fileIds,
    });
    return response.data;
  },

  getAnalysis: async (analysisId: string) => {
    const response = await api.get(`/analysis/${analysisId}`);
    return response.data;
  },

  cancelAnalysis: async (analysisId: string) => {
    await api.post(`/analysis/${analysisId}/cancel`);
  },

  getHistory: async () => {
    const response = await api.get('/analysis/history');
    return response.data;
  },

  downloadReport: async (analysisId: string, format: string) => {
    const response = await api.get(`/analysis/${analysisId}/download/${format}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Analysis Provider Component
interface AnalysisProviderProps {
  children: ReactNode;
}

export const AnalysisProvider: React.FC<AnalysisProviderProps> = ({ children }) => {
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  const [files, setFiles] = useState<AnalysisFile[]>([]);
  const [options, setOptions] = useState<AnalysisOptions>(defaultOptions);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const queryClient = useQueryClient();

  // Get recent analyses
  const { data: recentAnalyses = [] } = useQuery(
    'analysisHistory',
    analysisAPI.getHistory,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  // File upload mutation
  const uploadMutation = useMutation(analysisAPI.uploadFile, {
    onSuccess: (data, file) => {
      const newFile: AnalysisFile = {
        id: data.id,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString(),
        status: 'uploaded',
        url: data.url,
      };
      setFiles(prev => [...prev, newFile]);
      toast.success(`تم رفع ${file.name} بنجاح`);
    },
    onError: (error: any, file) => {
      const errorFile: AnalysisFile = {
        id: `error-${Date.now()}`,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString(),
        status: 'error',
        error: error.response?.data?.message || 'خطأ في رفع الملف',
      };
      setFiles(prev => [...prev, errorFile]);
      toast.error(`خطأ في رفع ${file.name}`);
    },
  });

  // Analysis start mutation
  const startAnalysisMutation = useMutation(
    () => {
      const fileIds = files.filter(f => f.status === 'uploaded').map(f => f.id);
      return analysisAPI.startAnalysis(options, fileIds);
    },
    {
      onSuccess: (data) => {
        setCurrentAnalysis(data);
        setIsAnalyzing(true);
        toast.success('تم بدء التحليل بنجاح');

        // Poll for updates
        const pollInterval = setInterval(async () => {
          try {
            const updatedAnalysis = await analysisAPI.getAnalysis(data.id);
            setCurrentAnalysis(updatedAnalysis);

            if (updatedAnalysis.status === 'completed' || updatedAnalysis.status === 'failed') {
              setIsAnalyzing(false);
              clearInterval(pollInterval);

              if (updatedAnalysis.status === 'completed') {
                toast.success('اكتمل التحليل بنجاح');
              } else {
                toast.error('فشل في التحليل');
              }

              queryClient.invalidateQueries('analysisHistory');
            }
          } catch (error) {
            clearInterval(pollInterval);
            setIsAnalyzing(false);
            toast.error('خطأ في متابعة التحليل');
          }
        }, 2000);
      },
      onError: (error: any) => {
        const message = error.response?.data?.message || 'خطأ في بدء التحليل';
        toast.error(message);
      },
    }
  );

  // Context methods
  const uploadFiles = async (filesToUpload: File[]) => {
    if (files.length + filesToUpload.length > 10) {
      toast.error('يمكن رفع 10 ملفات كحد أقصى');
      return;
    }

    setIsUploading(true);

    try {
      for (const file of filesToUpload) {
        // Add file with uploading status
        const uploadingFile: AnalysisFile = {
          id: `uploading-${Date.now()}-${Math.random()}`,
          name: file.name,
          size: file.size,
          type: file.type,
          uploadedAt: new Date().toISOString(),
          status: 'uploading',
        };
        setFiles(prev => [...prev, uploadingFile]);

        // Upload file
        await uploadMutation.mutateAsync(file);

        // Remove uploading file
        setFiles(prev => prev.filter(f => f.id !== uploadingFile.id));
      }
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));

    // Delete from server if uploaded
    const file = files.find(f => f.id === fileId);
    if (file && file.status === 'uploaded') {
      analysisAPI.deleteFile(fileId).catch(() => {
        // Silent fail - file might already be deleted
      });
    }
  };

  const clearFiles = () => {
    setFiles([]);
  };

  const updateOptions = (newOptions: Partial<AnalysisOptions>) => {
    setOptions(prev => ({ ...prev, ...newOptions }));
  };

  const resetOptions = () => {
    setOptions(defaultOptions);
  };

  const startAnalysis = async () => {
    if (files.length === 0) {
      toast.error('يرجى رفع ملف واحد على الأقل');
      return;
    }

    if (!options.sector || !options.activity) {
      toast.error('يرجى تحديد القطاع والنشاط');
      return;
    }

    await startAnalysisMutation.mutateAsync();
  };

  const getAnalysisResult = async (analysisId: string) => {
    return await analysisAPI.getAnalysis(analysisId);
  };

  const cancelAnalysis = () => {
    if (currentAnalysis) {
      analysisAPI.cancelAnalysis(currentAnalysis.id);
      setCurrentAnalysis(null);
      setIsAnalyzing(false);
      toast.success('تم إلغاء التحليل');
    }
  };

  const getAnalysisHistory = () => {
    return queryClient.getQueryData('analysisHistory');
  };

  const contextValue: AnalysisContextType = {
    currentAnalysis,
    files,
    options,
    isUploading,
    isAnalyzing,
    uploadFiles,
    removeFile,
    clearFiles,
    updateOptions,
    resetOptions,
    startAnalysis,
    getAnalysisResult,
    cancelAnalysis,
    getAnalysisHistory,
    recentAnalyses,
  };

  return (
    <AnalysisContext.Provider value={contextValue}>
      {children}
    </AnalysisContext.Provider>
  );
};

export const useAnalysis = (): AnalysisContextType => {
  const context = useContext(AnalysisContext);
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  return context;
};

export default AnalysisContext;