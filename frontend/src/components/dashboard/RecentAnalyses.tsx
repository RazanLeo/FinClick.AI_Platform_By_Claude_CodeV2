import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  ClockIcon,
  DocumentTextIcon,
  ChartBarIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

interface AnalysisItem {
  id: string;
  companyName: string;
  analysisType: string;
  status: 'completed' | 'processing' | 'failed';
  createdAt: string;
  completedAt?: string;
  sector: string;
  reportSize: string;
  analysisCount: number;
}

const RecentAnalyses: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  // Mock data - في التطبيق الحقيقي، ستأتي هذه البيانات من API
  const recentAnalyses: AnalysisItem[] = [
    {
      id: '1',
      companyName: 'شركة أرامكو السعودية',
      analysisType: 'comprehensive',
      status: 'completed',
      createdAt: '2024-01-15T10:30:00Z',
      completedAt: '2024-01-15T10:30:25Z',
      sector: 'energy',
      reportSize: '2.4 MB',
      analysisCount: 180
    },
    {
      id: '2',
      companyName: 'البنك الأهلي السعودي',
      analysisType: 'financial_performance',
      status: 'completed',
      createdAt: '2024-01-14T14:15:00Z',
      completedAt: '2024-01-14T14:15:28Z',
      sector: 'banking',
      reportSize: '1.8 MB',
      analysisCount: 106
    },
    {
      id: '3',
      companyName: 'شركة سابك',
      analysisType: 'risk_analysis',
      status: 'processing',
      createdAt: '2024-01-14T09:45:00Z',
      sector: 'chemicals',
      reportSize: '-',
      analysisCount: 21
    },
    {
      id: '4',
      companyName: 'شركة الاتصالات السعودية',
      analysisType: 'comprehensive',
      status: 'completed',
      createdAt: '2024-01-13T16:20:00Z',
      completedAt: '2024-01-13T16:20:22Z',
      sector: 'telecommunications',
      reportSize: '3.1 MB',
      analysisCount: 180
    },
    {
      id: '5',
      companyName: 'مجموعة تداول السعودية',
      analysisType: 'market_analysis',
      status: 'failed',
      createdAt: '2024-01-12T11:10:00Z',
      sector: 'financial_services',
      reportSize: '-',
      analysisCount: 53
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20 dark:text-green-400';
      case 'processing':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'failed':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-700 dark:text-gray-400';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return t('analysis.status.completed', 'مكتمل');
      case 'processing':
        return t('analysis.status.processing', 'قيد المعالجة');
      case 'failed':
        return t('analysis.status.failed', 'فشل');
      default:
        return status;
    }
  };

  const getAnalysisTypeText = (type: string) => {
    switch (type) {
      case 'comprehensive':
        return t('analysis.type.comprehensive', 'تحليل شامل');
      case 'financial_performance':
        return t('analysis.type.financial_performance', 'الأداء المالي');
      case 'risk_analysis':
        return t('analysis.type.risk_analysis', 'تحليل المخاطر');
      case 'market_analysis':
        return t('analysis.type.market_analysis', 'تحليل السوق');
      default:
        return type;
    }
  };

  const getSectorText = (sector: string) => {
    const sectorMap: { [key: string]: string } = {
      'energy': t('sectors.energy', 'الطاقة'),
      'banking': t('sectors.banking', 'البنوك'),
      'chemicals': t('sectors.chemicals', 'الكيماويات'),
      'telecommunications': t('sectors.telecommunications', 'الاتصالات'),
      'financial_services': t('sectors.financial_services', 'الخدمات المالية')
    };
    return sectorMap[sector] || sector;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) {
      return t('time.justNow', 'الآن');
    } else if (diffInHours < 24) {
      return t('time.hoursAgo', `منذ ${diffInHours} ساعة`);
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return t('time.daysAgo', `منذ ${diffInDays} يوم`);
    }
  };

  const getAnalysisTime = (createdAt: string, completedAt?: string) => {
    if (!completedAt) return '-';
    const created = new Date(createdAt);
    const completed = new Date(completedAt);
    const diffInSeconds = Math.floor((completed.getTime() - created.getTime()) / 1000);
    return `${diffInSeconds} ${t('time.seconds', 'ثانية')}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
            <ClockIcon className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {t('dashboard.recentAnalyses', 'التحليلات الأخيرة')}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('dashboard.last5Analyses', 'آخر 5 تحليلات مالية')}
            </p>
          </div>
        </div>

        <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
          {t('common.viewAll', 'عرض الكل')}
        </button>
      </div>

      {/* Analyses List */}
      <div className="space-y-4">
        {recentAnalyses.map((analysis, index) => (
          <motion.div
            key={analysis.id}
            initial={{ opacity: 0, x: isRTL ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="group p-4 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center justify-between">
              {/* Main Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3 rtl:space-x-reverse mb-2">
                  <BuildingOfficeIcon className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {analysis.companyName}
                  </h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(analysis.status)}`}>
                    {getStatusText(analysis.status)}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs text-gray-600 dark:text-gray-400">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2 rtl:space-x-reverse">
                      <ChartBarIcon className="w-4 h-4" />
                      <span>{getAnalysisTypeText(analysis.analysisType)}</span>
                    </div>
                    <div className="flex items-center space-x-2 rtl:space-x-reverse">
                      <span className="w-4 h-4 text-center">🏢</span>
                      <span>{getSectorText(analysis.sector)}</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center space-x-2 rtl:space-x-reverse">
                      <ClockIcon className="w-4 h-4" />
                      <span>{formatDate(analysis.createdAt)}</span>
                    </div>
                    <div className="flex items-center space-x-2 rtl:space-x-reverse">
                      <span className="w-4 h-4 text-center">📊</span>
                      <span>{analysis.analysisCount} {t('common.analysis', 'تحليل')}</span>
                    </div>
                  </div>
                </div>

                {/* Analysis Time (for completed analyses) */}
                {analysis.status === 'completed' && analysis.completedAt && (
                  <div className="mt-2 flex items-center space-x-2 rtl:space-x-reverse text-xs text-green-600 dark:text-green-400">
                    <span>⚡</span>
                    <span>{t('analysis.completedIn', 'اكتمل في')} {getAnalysisTime(analysis.createdAt, analysis.completedAt)}</span>
                  </div>
                )}

                {/* Processing indicator */}
                {analysis.status === 'processing' && (
                  <div className="mt-2 flex items-center space-x-2 rtl:space-x-reverse text-xs text-yellow-600 dark:text-yellow-400">
                    <div className="w-3 h-3 border-2 border-yellow-600 border-t-transparent rounded-full animate-spin" />
                    <span>{t('analysis.processing', 'قيد المعالجة...')}</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              {analysis.status === 'completed' && (
                <div className="flex items-center space-x-2 rtl:space-x-reverse opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title={t('common.view', 'عرض')}
                  >
                    <EyeIcon className="w-5 h-5" />
                  </button>
                  <button
                    className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                    title={t('common.download', 'تحميل')}
                  >
                    <ArrowDownTrayIcon className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty state (if no analyses) */}
      {recentAnalyses.length === 0 && (
        <div className="text-center py-8">
          <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            {t('dashboard.noAnalyses', 'لا توجد تحليلات حتى الآن')}
          </h4>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            {t('dashboard.startFirstAnalysis', 'ابدأ أول تحليل مالي لك')}
          </p>
        </div>
      )}

      {/* Footer Stats */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">
              {recentAnalyses.filter(a => a.status === 'completed').length}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {t('stats.completed', 'مكتمل')}
            </p>
          </div>
          <div>
            <p className="text-lg font-semibold text-yellow-600">
              {recentAnalyses.filter(a => a.status === 'processing').length}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {t('stats.processing', 'قيد المعالجة')}
            </p>
          </div>
          <div>
            <p className="text-lg font-semibold text-gray-900 dark:text-white">
              {recentAnalyses.reduce((sum, a) => sum + (a.analysisCount || 0), 0)}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {t('stats.totalAnalysisTypes', 'إجمالي الأنواع')}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default RecentAnalyses;