/**
 * Integrated Analysis Manager Component
 * مكون مدير التحليلات المتكامل
 *
 * This component manages the complete financial analysis workflow:
 * - File upload and OCR processing
 * - Analysis request creation and management
 * - Real-time progress tracking
 * - Results display and export
 * - Integration with 23 AI agents and 180 analysis types
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-hot-toast';
import {
  DocumentArrowUpIcon,
  PlayIcon,
  StopIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

import { useAuth } from '../../contexts/AuthContext';
import { apiService, AnalysisRequest, AnalysisResponse, FileUploadRequest } from '../../services/api';
import LoadingSpinner from '../ui/LoadingSpinner';

// Analysis types configuration
const ANALYSIS_TYPES = [
  {
    id: 'comprehensive',
    name: 'تحليل شامل',
    nameEn: 'Comprehensive Analysis',
    description: 'تحليل كامل يشمل جميع الجوانب المالية والمخاطر والتقييم',
    descriptionEn: 'Complete analysis including all financial aspects, risks, and valuation',
    duration: '15-20 دقيقة',
    analyses: 180,
    agents: 23,
    icon: ChartBarIcon,
    color: 'bg-blue-500'
  },
  {
    id: 'quick',
    name: 'تحليل سريع',
    nameEn: 'Quick Analysis',
    description: 'تحليل سريع للمؤشرات الأساسية والمخاطر الحرجة',
    descriptionEn: 'Quick analysis of key metrics and critical risks',
    duration: '3-5 دقائق',
    analyses: 25,
    agents: 5,
    icon: ClockIcon,
    color: 'bg-green-500'
  },
  {
    id: 'risk_assessment',
    name: 'تقييم المخاطر',
    nameEn: 'Risk Assessment',
    description: 'تحليل متخصص للمخاطر الائتمانية والتشغيلية والسوقية',
    descriptionEn: 'Specialized analysis of credit, operational, and market risks',
    duration: '8-12 دقيقة',
    analyses: 45,
    agents: 8,
    icon: ExclamationTriangleIcon,
    color: 'bg-orange-500'
  },
  {
    id: 'valuation',
    name: 'تحليل التقييم',
    nameEn: 'Valuation Analysis',
    description: 'تقييم الشركة باستخدام طرق متعددة DCF والمقارنات',
    descriptionEn: 'Company valuation using multiple methods: DCF and comparables',
    duration: '10-15 دقيقة',
    analyses: 35,
    agents: 6,
    icon: DocumentTextIcon,
    color: 'bg-purple-500'
  }
];

// File types configuration
const FILE_TYPES = [
  { id: 'financial_statement', name: 'القوائم المالية', nameEn: 'Financial Statements' },
  { id: 'balance_sheet', name: 'الميزانية العمومية', nameEn: 'Balance Sheet' },
  { id: 'income_statement', name: 'قائمة الدخل', nameEn: 'Income Statement' },
  { id: 'cash_flow', name: 'قائمة التدفق النقدي', nameEn: 'Cash Flow Statement' }
];

interface UploadedFile {
  id: string;
  file: File;
  fileType: string;
  uploadProgress: number;
  processingStatus: 'uploading' | 'processing' | 'completed' | 'error';
  extractedData?: any;
  error?: string;
}

interface ActiveAnalysis {
  requestId: string;
  type: string;
  status: 'queued' | 'processing' | 'completed' | 'error';
  progress: string;
  startTime: Date;
  results?: any;
  error?: string;
}

const AnalysisManager: React.FC = () => {
  const { user } = useAuth();
  const [selectedAnalysisType, setSelectedAnalysisType] = useState<string>('comprehensive');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [activeAnalyses, setActiveAnalyses] = useState<ActiveAnalysis[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [companyData, setCompanyData] = useState<any>({});
  const [manualDataEntry, setManualDataEntry] = useState(false);
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);
  const [platformStatus, setPlatformStatus] = useState<any>(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    // Listen for analysis events
    const handleAnalysisStarted = (event: CustomEvent) => {
      const { request_id, status } = event.detail;
      setActiveAnalyses(prev => prev.map(analysis =>
        analysis.requestId === request_id
          ? { ...analysis, status: 'processing', progress: 'بدء التحليل...' }
          : analysis
      ));
    };

    const handleAnalysisCompleted = (event: CustomEvent) => {
      const { request_id, execution_time_ms } = event.detail;
      setActiveAnalyses(prev => prev.map(analysis =>
        analysis.requestId === request_id
          ? { ...analysis, status: 'completed', progress: `مكتمل في ${Math.round(execution_time_ms / 1000)} ثانية` }
          : analysis
      ));
      setIsAnalyzing(false);
      toast.success('تم إكمال التحليل بنجاح!');

      // Refresh analysis history
      loadAnalysisHistory();
    };

    const handleAnalysisError = (event: CustomEvent) => {
      const { request_id, error } = event.detail;
      setActiveAnalyses(prev => prev.map(analysis =>
        analysis.requestId === request_id
          ? { ...analysis, status: 'error', error, progress: 'فشل التحليل' }
          : analysis
      ));
      setIsAnalyzing(false);
      toast.error(`فشل التحليل: ${error}`);
    };

    const handleFileProcessed = (event: CustomEvent) => {
      const { file_id, extracted_data } = event.detail;
      setUploadedFiles(prev => prev.map(file =>
        file.id === file_id
          ? { ...file, processingStatus: 'completed', extractedData: extracted_data }
          : file
      ));
      toast.success('تم معالجة الملف بنجاح!');
    };

    const handleUploadProgress = (event: CustomEvent) => {
      const { percent, file: fileName } = event.detail;
      setUploadedFiles(prev => prev.map(file =>
        file.file.name === fileName
          ? { ...file, uploadProgress: percent }
          : file
      ));
    };

    // Add event listeners
    apiService.addEventListener('analysisStarted', handleAnalysisStarted);
    apiService.addEventListener('analysisCompleted', handleAnalysisCompleted);
    apiService.addEventListener('analysisError', handleAnalysisError);
    apiService.addEventListener('fileProcessed', handleFileProcessed);
    apiService.addEventListener('uploadProgress', handleUploadProgress);

    // Load initial data
    loadAnalysisHistory();
    loadPlatformStatus();

    // Cleanup
    return () => {
      apiService.removeEventListener('analysisStarted', handleAnalysisStarted);
      apiService.removeEventListener('analysisCompleted', handleAnalysisCompleted);
      apiService.removeEventListener('analysisError', handleAnalysisError);
      apiService.removeEventListener('fileProcessed', handleFileProcessed);
      apiService.removeEventListener('uploadProgress', handleUploadProgress);
    };
  }, []);

  const loadAnalysisHistory = async () => {
    try {
      const response = await apiService.getAnalysisHistory(1, 10);
      if (response.success) {
        setAnalysisHistory(response.data.analyses || []);
      }
    } catch (error) {
      console.error('Failed to load analysis history:', error);
    }
  };

  const loadPlatformStatus = async () => {
    try {
      const response = await apiService.getPlatformStatus();
      if (response.success) {
        setPlatformStatus(response.data);
      }
    } catch (error) {
      console.error('Failed to load platform status:', error);
    }
  };

  // File upload handling
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      // Add file to state
      const uploadedFile: UploadedFile = {
        id: fileId,
        file,
        fileType: 'financial_statement', // Default type
        uploadProgress: 0,
        processingStatus: 'uploading'
      };

      setUploadedFiles(prev => [...prev, uploadedFile]);

      try {
        // Upload file
        const uploadRequest: FileUploadRequest = {
          file,
          file_type: 'financial_statement',
          extract_text: true
        };

        const response = await apiService.uploadFile(uploadRequest);

        if (response.success) {
          setUploadedFiles(prev => prev.map(f =>
            f.id === fileId
              ? { ...f, processingStatus: 'processing', uploadProgress: 100 }
              : f
          ));
        } else {
          throw new Error(response.message);
        }

      } catch (error: any) {
        setUploadedFiles(prev => prev.map(f =>
          f.id === fileId
            ? { ...f, processingStatus: 'error', error: error.message }
            : f
        ));
        toast.error(`فشل رفع الملف: ${error.message}`);
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  // Analysis execution
  const startAnalysis = async () => {
    if (!user) {
      toast.error('يجب تسجيل الدخول أولاً');
      return;
    }

    if (uploadedFiles.length === 0 && Object.keys(companyData).length === 0) {
      toast.error('يرجى رفع ملفات أو إدخال بيانات الشركة');
      return;
    }

    try {
      setIsAnalyzing(true);

      // Prepare analysis request
      const analysisRequest: AnalysisRequest = {
        user_id: user.id,
        analysis_type: selectedAnalysisType as any,
        data_source: uploadedFiles.length > 0 ? 'file_upload' : 'manual_entry',
        company_data: {
          files: uploadedFiles.map(f => ({ id: f.id, type: f.fileType, data: f.extractedData })),
          manual_data: companyData,
          analysis_options: {
            include_charts: true,
            include_recommendations: true,
            language: 'ar'
          }
        },
        priority: selectedAnalysisType === 'quick' ? 8 : 5
      };

      const response = await apiService.requestAnalysis(analysisRequest);

      if (response.success) {
        const newAnalysis: ActiveAnalysis = {
          requestId: response.data.request_id,
          type: selectedAnalysisType,
          status: 'queued',
          progress: 'في الانتظار...',
          startTime: new Date()
        };

        setActiveAnalyses(prev => [...prev, newAnalysis]);
        toast.success('تم إرسال طلب التحليل بنجاح');
      } else {
        throw new Error(response.message);
      }

    } catch (error: any) {
      setIsAnalyzing(false);
      toast.error(`فشل في بدء التحليل: ${error.message}`);
    }
  };

  const cancelAnalysis = async (requestId: string) => {
    try {
      const response = await apiService.cancelAnalysis(requestId);
      if (response.success) {
        setActiveAnalyses(prev => prev.filter(a => a.requestId !== requestId));
        toast.success('تم إلغاء التحليل');
      }
    } catch (error: any) {
      toast.error(`فشل في إلغاء التحليل: ${error.message}`);
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const updateFileType = (fileId: string, newType: string) => {
    setUploadedFiles(prev => prev.map(f =>
      f.id === fileId ? { ...f, fileType: newType } : f
    ));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'processing': return 'text-blue-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircleIcon;
      case 'processing': return ClockIcon;
      case 'error': return ExclamationTriangleIcon;
      default: return ClockIcon;
    }
  };

  return (
    <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8\">
      {/* Header */}
      <div className=\"mb-8\">
        <h1 className=\"text-3xl font-bold text-gray-900 dark:text-white mb-2\">
          مدير التحليلات المالية المتكامل
        </h1>
        <p className=\"text-gray-600 dark:text-gray-400\">
          منصة تحليل مالي ذكية مدعومة بـ 23 وكيل ذكي و 180 نوع تحليل مالي
        </p>

        {/* Platform Status */}
        {platformStatus && (
          <div className=\"mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg\">
            <div className=\"flex items-center justify-between\">
              <div className=\"flex items-center space-x-2 rtl:space-x-reverse\">
                <div className={`w-3 h-3 rounded-full ${
                  platformStatus.platform_status === 'healthy' ? 'bg-green-500' :
                  platformStatus.platform_status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
                }`}></div>
                <span className=\"text-sm font-medium\">
                  حالة المنصة: {platformStatus.platform_status === 'healthy' ? 'صحية' : 'متدهورة'}
                </span>
              </div>
              <div className=\"text-sm text-gray-500\">
                تحليلات نشطة: {platformStatus.platform_metrics?.active_analyses || 0} |
                اتصالات: {platformStatus.platform_metrics?.websocket_connections || 0}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className=\"grid lg:grid-cols-3 gap-8\">
        {/* Left Panel - Configuration */}
        <div className=\"lg:col-span-2 space-y-6\">
          {/* Analysis Type Selection */}
          <div className=\"bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6\">
            <h2 className=\"text-xl font-semibold mb-4\">نوع التحليل</h2>
            <div className=\"grid md:grid-cols-2 gap-4\">
              {ANALYSIS_TYPES.map((type) => {
                const Icon = type.icon;
                return (
                  <motion.div
                    key={type.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                      selectedAnalysisType === type.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedAnalysisType(type.id)}
                  >
                    <div className=\"flex items-start space-x-3 rtl:space-x-reverse\">
                      <div className={`p-2 rounded-lg ${type.color} text-white`}>
                        <Icon className=\"w-6 h-6\" />
                      </div>
                      <div className=\"flex-1\">
                        <h3 className=\"font-semibold text-gray-900 dark:text-white\">
                          {type.name}
                        </h3>
                        <p className=\"text-sm text-gray-600 dark:text-gray-400 mt-1\">
                          {type.description}
                        </p>
                        <div className=\"flex items-center justify-between mt-2 text-xs text-gray-500\">
                          <span>المدة: {type.duration}</span>
                          <span>{type.analyses} تحليل • {type.agents} وكيل</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* File Upload Section */}
          <div className=\"bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6\">
            <h2 className=\"text-xl font-semibold mb-4\">رفع الملفات المالية</h2>

            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isDragActive
                  ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
              }`}
            >
              <input {...getInputProps()} />
              <DocumentArrowUpIcon className=\"w-12 h-12 text-gray-400 mx-auto mb-4\" />
              <p className=\"text-lg font-medium text-gray-900 dark:text-white mb-2\">
                {isDragActive ? 'أفلت الملفات هنا' : 'اسحب الملفات هنا أو انقر للاختيار'}
              </p>
              <p className=\"text-sm text-gray-500\">
                PDF, Excel, أو صور (حتى 10 ميجابايت لكل ملف)
              </p>
            </div>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
              <div className=\"mt-6 space-y-4\">
                <h3 className=\"font-medium text-gray-900 dark:text-white\">الملفات المرفوعة</h3>
                {uploadedFiles.map((file) => {
                  const StatusIcon = getStatusIcon(file.processingStatus);
                  return (
                    <div key={file.id} className=\"border border-gray-200 dark:border-gray-700 rounded-lg p-4\">
                      <div className=\"flex items-center justify-between mb-2\">
                        <div className=\"flex items-center space-x-3 rtl:space-x-reverse\">
                          <StatusIcon className={`w-5 h-5 ${getStatusColor(file.processingStatus)}`} />
                          <span className=\"font-medium text-gray-900 dark:text-white\">
                            {file.file.name}
                          </span>
                        </div>
                        <button
                          onClick={() => removeFile(file.id)}
                          className=\"text-red-500 hover:text-red-700\"
                        >
                          <TrashIcon className=\"w-4 h-4\" />
                        </button>
                      </div>

                      <div className=\"flex items-center justify-between\">
                        <select
                          value={file.fileType}
                          onChange={(e) => updateFileType(file.id, e.target.value)}
                          className=\"text-sm border border-gray-300 rounded px-2 py-1\"
                        >
                          {FILE_TYPES.map(type => (
                            <option key={type.id} value={type.id}>{type.name}</option>
                          ))}
                        </select>

                        <span className={`text-sm ${getStatusColor(file.processingStatus)}`}>
                          {file.processingStatus === 'uploading' && `${file.uploadProgress}%`}
                          {file.processingStatus === 'processing' && 'جاري المعالجة...'}
                          {file.processingStatus === 'completed' && 'مكتمل'}
                          {file.processingStatus === 'error' && file.error}
                        </span>
                      </div>

                      {file.processingStatus === 'uploading' && (
                        <div className=\"mt-2 w-full bg-gray-200 rounded-full h-2\">
                          <div
                            className=\"bg-blue-600 h-2 rounded-full transition-all duration-300\"
                            style={{ width: `${file.uploadProgress}%` }}
                          ></div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Manual Data Entry Toggle */}
            <div className=\"mt-6 pt-6 border-t border-gray-200 dark:border-gray-700\">
              <label className=\"flex items-center space-x-2 rtl:space-x-reverse\">
                <input
                  type=\"checkbox\"
                  checked={manualDataEntry}
                  onChange={(e) => setManualDataEntry(e.target.checked)}
                  className=\"rounded border-gray-300\"
                />
                <span className=\"text-sm text-gray-700 dark:text-gray-300\">
                  إدخال البيانات يدوياً (بدلاً من رفع الملفات)
                </span>
              </label>
            </div>
          </div>

          {/* Manual Data Entry */}
          {manualDataEntry && (
            <div className=\"bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6\">
              <h2 className=\"text-xl font-semibold mb-4\">إدخال البيانات المالية</h2>
              <div className=\"grid md:grid-cols-2 gap-4\">
                <div>
                  <label className=\"block text-sm font-medium mb-2\">إجمالي الأصول</label>
                  <input
                    type=\"number\"
                    className=\"w-full border border-gray-300 rounded-lg px-3 py-2\"
                    placeholder=\"0\"
                    value={companyData.totalAssets || ''}
                    onChange={(e) => setCompanyData(prev => ({ ...prev, totalAssets: e.target.value }))}
                  />
                </div>
                <div>
                  <label className=\"block text-sm font-medium mb-2\">إجمالي الخصوم</label>
                  <input
                    type=\"number\"
                    className=\"w-full border border-gray-300 rounded-lg px-3 py-2\"
                    placeholder=\"0\"
                    value={companyData.totalLiabilities || ''}
                    onChange={(e) => setCompanyData(prev => ({ ...prev, totalLiabilities: e.target.value }))}
                  />
                </div>
                <div>
                  <label className=\"block text-sm font-medium mb-2\">الإيرادات</label>
                  <input
                    type=\"number\"
                    className=\"w-full border border-gray-300 rounded-lg px-3 py-2\"
                    placeholder=\"0\"
                    value={companyData.revenue || ''}
                    onChange={(e) => setCompanyData(prev => ({ ...prev, revenue: e.target.value }))}
                  />
                </div>
                <div>
                  <label className=\"block text-sm font-medium mb-2\">صافي الربح</label>
                  <input
                    type=\"number\"
                    className=\"w-full border border-gray-300 rounded-lg px-3 py-2\"
                    placeholder=\"0\"
                    value={companyData.netIncome || ''}
                    onChange={(e) => setCompanyData(prev => ({ ...prev, netIncome: e.target.value }))}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Start Analysis Button */}
          <div className=\"bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6\">
            <button
              onClick={startAnalysis}
              disabled={isAnalyzing || (uploadedFiles.length === 0 && Object.keys(companyData).length === 0)}
              className=\"w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 rtl:space-x-reverse\"
            >
              {isAnalyzing ? (
                <>
                  <LoadingSpinner size=\"small\" />
                  <span>جاري التحليل...</span>
                </>
              ) : (
                <>
                  <PlayIcon className=\"w-5 h-5\" />
                  <span>بدء التحليل</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Panel - Status & History */}
        <div className=\"space-y-6\">
          {/* Active Analyses */}
          <div className=\"bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6\">
            <h2 className=\"text-xl font-semibold mb-4\">التحليلات النشطة</h2>
            {activeAnalyses.length === 0 ? (
              <p className=\"text-gray-500 text-center py-4\">لا توجد تحليلات نشطة</p>
            ) : (
              <div className=\"space-y-4\">
                {activeAnalyses.map((analysis) => {
                  const StatusIcon = getStatusIcon(analysis.status);
                  const analysisType = ANALYSIS_TYPES.find(t => t.id === analysis.type);

                  return (
                    <div key={analysis.requestId} className=\"border border-gray-200 dark:border-gray-700 rounded-lg p-4\">
                      <div className=\"flex items-center justify-between mb-2\">
                        <div className=\"flex items-center space-x-2 rtl:space-x-reverse\">
                          <StatusIcon className={`w-5 h-5 ${getStatusColor(analysis.status)}`} />
                          <span className=\"font-medium\">{analysisType?.name}</span>
                        </div>
                        {analysis.status === 'processing' && (
                          <button
                            onClick={() => cancelAnalysis(analysis.requestId)}
                            className=\"text-red-500 hover:text-red-700\"
                          >
                            <StopIcon className=\"w-4 h-4\" />
                          </button>
                        )}
                      </div>

                      <p className={`text-sm ${getStatusColor(analysis.status)}`}>
                        {analysis.progress}
                      </p>

                      <p className=\"text-xs text-gray-500 mt-1\">
                        بدأ في: {analysis.startTime.toLocaleTimeString('ar-SA')}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Analysis History */}
          <div className=\"bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6\">
            <h2 className=\"text-xl font-semibold mb-4\">سجل التحليلات</h2>
            {analysisHistory.length === 0 ? (
              <p className=\"text-gray-500 text-center py-4\">لا يوجد سجل تحليلات</p>
            ) : (
              <div className=\"space-y-3\">
                {analysisHistory.slice(0, 5).map((analysis, index) => (
                  <div key={index} className=\"flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg\">
                    <div>
                      <p className=\"font-medium text-sm\">{analysis.type}</p>
                      <p className=\"text-xs text-gray-500\">{analysis.date}</p>
                    </div>
                    <div className=\"flex space-x-2 rtl:space-x-reverse\">
                      <button className=\"text-blue-600 hover:text-blue-800\">
                        <EyeIcon className=\"w-4 h-4\" />
                      </button>
                      <button className=\"text-green-600 hover:text-green-800\">
                        <ArrowDownTrayIcon className=\"w-4 h-4\" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisManager;