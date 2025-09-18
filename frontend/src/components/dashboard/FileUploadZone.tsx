import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  CloudArrowUpIcon,
  DocumentIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { useAnalysis } from '../../contexts/AnalysisContext';

const FileUploadZone: React.FC = () => {
  const { t } = useTranslation();
  const { files, uploadFiles, removeFile, isUploading } = useAnalysis();
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        uploadFiles(acceptedFiles);
      }
    },
    [uploadFiles]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'text/csv': ['.csv'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif'],
    },
    maxFiles: 10,
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: true,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    onDropAccepted: () => setDragActive(false),
    onDropRejected: () => setDragActive(false),
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('excel') || type.includes('spreadsheet')) return '📊';
    if (type.includes('word') || type.includes('document')) return '📝';
    if (type.includes('powerpoint') || type.includes('presentation')) return '📈';
    if (type.includes('csv')) return '📋';
    if (type.includes('image')) return '🖼️';
    return '📁';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'uploading':
        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-400';
      case 'uploaded':
        return 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400';
      case 'error':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-700 dark:text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'uploading':
        return <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />;
      case 'uploaded':
        return <CheckCircleIcon className="w-4 h-4" />;
      case 'error':
        return <ExclamationTriangleIcon className="w-4 h-4" />;
      default:
        return <DocumentIcon className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`
          upload-zone cursor-pointer transition-all duration-300
          ${isDragActive || dragActive ? 'upload-zone-active' : ''}
          ${isUploading ? 'opacity-75 cursor-wait' : ''}
        `}
      >
        <input {...getInputProps()} />

        <motion.div
          initial={{ scale: 1 }}
          animate={{ scale: isDragActive ? 1.02 : 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 mx-auto mb-4">
            <CloudArrowUpIcon className={`w-full h-full transition-colors duration-300 ${
              isDragActive
                ? 'text-primary-600 dark:text-primary-400'
                : 'text-gray-400 dark:text-gray-500'
            }`} />
          </div>

          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            {isDragActive
              ? t('dashboard.sections.upload.dragDrop', 'اسحب وأفلت الملفات هنا')
              : t('dashboard.sections.upload.selectFiles', 'اضغط لاختيار الملفات أو اسحبها هنا')
            }
          </h3>

          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {t('dashboard.sections.upload.supportedFormats', 'الصيغ المدعومة: PDF, Excel, Word, صور')}
            <br />
            {t('dashboard.sections.upload.maxFiles', 'حتى 10 ملفات')} • حد أقصى 100 ميجابايت لكل ملف
          </p>

          <div className="flex flex-wrap gap-2 justify-center text-sm text-gray-500 dark:text-gray-400">
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">PDF</span>
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Excel</span>
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Word</span>
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">PowerPoint</span>
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">CSV</span>
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">صور</span>
          </div>
        </motion.div>
      </div>

      {/* Files List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
              الملفات المرفوعة ({files.length}/10)
            </h4>
            {files.length > 0 && (
              <button
                onClick={() => files.forEach(file => removeFile(file.id))}
                className="text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors"
              >
                مسح الكل
              </button>
            )}
          </div>

          <div className="space-y-2">
            <AnimatePresence>
              {files.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="flex items-center space-x-3 rtl:space-x-reverse p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-200"
                >
                  {/* File Icon */}
                  <div className="text-2xl">{getFileIcon(file.type)}</div>

                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 rtl:space-x-reverse">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {file.name}
                      </p>
                      <span className={`inline-flex items-center space-x-1 rtl:space-x-reverse px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.status)}`}>
                        {getStatusIcon(file.status)}
                        <span>
                          {file.status === 'uploading' && 'جارٍ الرفع...'}
                          {file.status === 'uploaded' && 'تم الرفع'}
                          {file.status === 'error' && 'خطأ'}
                        </span>
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 rtl:space-x-reverse text-xs text-gray-500 dark:text-gray-400 mt-1">
                      <span>{formatFileSize(file.size)}</span>
                      <span>•</span>
                      <span>{new Date(file.uploadedAt).toLocaleString('ar-SA')}</span>
                      {file.error && (
                        <>
                          <span>•</span>
                          <span className="text-red-500 dark:text-red-400">{file.error}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2 rtl:space-x-reverse">
                    {file.status === 'uploaded' && file.url && (
                      <button
                        onClick={() => window.open(file.url, '_blank')}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                        title="معاينة الملف"
                      >
                        <EyeIcon className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                      title="حذف الملف"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4"
            >
              <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                <span>جارٍ رفع الملفات...</span>
                <span>{files.filter(f => f.status === 'uploaded').length} / {files.length}</span>
              </div>
              <div className="progress">
                <div
                  className="progress-bar"
                  style={{
                    width: `${(files.filter(f => f.status === 'uploaded').length / files.length) * 100}%`
                  }}
                />
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Help Text */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
        <h5 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
          نصائح لأفضل النتائج:
        </h5>
        <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
          <li>• تأكد من وضوح وجودة المستندات الممسوحة</li>
          <li>• ارفع القوائم المالية الكاملة (الميزانية، قائمة الدخل، التدفقات النقدية)</li>
          <li>• يفضل رفع البيانات لأكثر من سنة مالية للمقارنة</li>
          <li>• تأكد من أن البيانات حديثة ومدققة</li>
        </ul>
      </div>
    </div>
  );
};

export default FileUploadZone;