import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  HomeIcon,
  DocumentArrowUpIcon,
  CogIcon,
  PlayIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';

// Components
import QuickStats from '../components/dashboard/QuickStats';
import FileUploadZone from '../components/dashboard/FileUploadZone';
import AnalysisOptionsForm from '../components/dashboard/AnalysisOptionsForm';
import RecentAnalyses from '../components/dashboard/RecentAnalyses';

// Hooks
import { useAuth } from '../contexts/AuthContext';
import { useAnalysis } from '../contexts/AnalysisContext';

const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { currentAnalysis, isAnalyzing } = useAnalysis();
  const [activeTab, setActiveTab] = useState<'upload' | 'options' | 'analysis' | 'results'>('upload');

  const tabs = [
    {
      id: 'upload' as const,
      name: 'رفع الملفات',
      icon: DocumentArrowUpIcon,
      description: 'ارفع القوائم المالية والمستندات'
    },
    {
      id: 'options' as const,
      name: 'خيارات التحليل',
      icon: CogIcon,
      description: 'حدد القطاع ونوع التحليل المطلوب'
    },
    {
      id: 'analysis' as const,
      name: 'بدء التحليل',
      icon: PlayIcon,
      description: 'ابدأ عملية التحليل المالي'
    },
    {
      id: 'results' as const,
      name: 'النتائج والتقارير',
      icon: EyeIcon,
      description: 'اعرض النتائج وحمل التقارير'
    }
  ];

  const getTabStatus = (tabId: string) => {
    // Logic to determine if tab is completed, active, or disabled
    switch (tabId) {
      case 'upload':
        return 'active';
      case 'options':
        return 'active';
      case 'analysis':
        return 'active';
      case 'results':
        return currentAnalysis ? 'active' : 'disabled';
      default:
        return 'disabled';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-3 rtl:space-x-reverse mb-2">
            <HomeIcon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {t('dashboard.title', 'لوحة التحكم')}
            </h1>
          </div>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            {user ? `${t('dashboard.welcome', 'مرحباً بك')} ${user.firstName}!` : t('dashboard.welcome', 'مرحباً بك في FinClick.AI')}
          </p>
        </motion.div>

        {/* Quick Stats */}
        <QuickStats />

        {/* Navigation Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-soft border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="grid grid-cols-1 md:grid-cols-4">
              {tabs.map((tab, index) => {
                const status = getTabStatus(tab.id);
                const isActive = activeTab === tab.id;
                const isCompleted = status === 'completed';
                const isDisabled = status === 'disabled';

                return (
                  <motion.button
                    key={tab.id}
                    whileHover={!isDisabled ? { scale: 1.02 } : undefined}
                    whileTap={!isDisabled ? { scale: 0.98 } : undefined}
                    onClick={() => !isDisabled && setActiveTab(tab.id)}
                    disabled={isDisabled}
                    className={`relative p-6 text-center transition-all duration-200 border-b-4 ${
                      isActive
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : isCompleted
                        ? 'border-green-500 bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30'
                        : isDisabled
                        ? 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50 cursor-not-allowed opacity-50'
                        : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="flex flex-col items-center">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-3 ${
                        isActive
                          ? 'bg-primary-500 text-white'
                          : isCompleted
                          ? 'bg-green-500 text-white'
                          : isDisabled
                          ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                      }`}>
                        <tab.icon className="w-6 h-6" />
                      </div>
                      <h3 className={`font-semibold mb-1 ${
                        isActive
                          ? 'text-primary-700 dark:text-primary-300'
                          : isCompleted
                          ? 'text-green-700 dark:text-green-300'
                          : isDisabled
                          ? 'text-gray-500 dark:text-gray-400'
                          : 'text-gray-900 dark:text-white'
                      }`}>
                        {tab.name}
                      </h3>
                      <p className={`text-xs ${
                        isDisabled
                          ? 'text-gray-400 dark:text-gray-500'
                          : 'text-gray-600 dark:text-gray-300'
                      }`}>
                        {tab.description}
                      </p>
                    </div>

                    {/* Step number */}
                    <div className={`absolute top-2 right-2 w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center ${
                      isActive
                        ? 'bg-primary-500 text-white'
                        : isCompleted
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                    }`}>
                      {isCompleted ? '✓' : index + 1}
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* Content Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="grid lg:grid-cols-3 gap-8"
        >
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-soft border border-gray-200 dark:border-gray-700 p-6">
              {/* Tab Content Header */}
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {tabs.find(tab => tab.id === activeTab)?.name}
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  {tabs.find(tab => tab.id === activeTab)?.description}
                </p>
              </div>

              {/* Tab Content */}
              <div className="min-h-[400px]">
                {activeTab === 'upload' && <FileUploadZone />}
                {activeTab === 'options' && <AnalysisOptionsForm />}
                {activeTab === 'analysis' && (
                  <div className="text-center py-12">
                    {isAnalyzing ? (
                      <div>
                        <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                          جارٍ التحليل...
                        </h3>
                        <p className="text-gray-600 dark:text-gray-300">
                          وكلاء الذكاء الاصطناعي يعملون على تحليل بياناتك المالية
                        </p>
                      </div>
                    ) : (
                      <div>
                        <PlayIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                          جاهز لبدء التحليل
                        </h3>
                        <p className="text-gray-600 dark:text-gray-300 mb-6">
                          تأكد من رفع الملفات وتحديد خيارات التحليل قبل البدء
                        </p>
                        <button className="btn btn-primary btn-lg">
                          <PlayIcon className="w-5 h-5 mr-2" />
                          بدء التحليل
                        </button>
                      </div>
                    )}
                  </div>
                )}
                {activeTab === 'results' && (
                  <div className="text-center py-12">
                    {currentAnalysis ? (
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                          نتائج التحليل
                        </h3>
                        {/* Results content would go here */}
                      </div>
                    ) : (
                      <div>
                        <EyeIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                          لا توجد نتائج بعد
                        </h3>
                        <p className="text-gray-600 dark:text-gray-300">
                          ابدأ تحليل جديد لعرض النتائج هنا
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Progress Overview */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-soft border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                تقدم التحليل
              </h3>
              <div className="space-y-3">
                {tabs.map((tab, index) => {
                  const status = getTabStatus(tab.id);
                  return (
                    <div key={tab.id} className="flex items-center space-x-3 rtl:space-x-reverse">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                        status === 'completed'
                          ? 'bg-green-500 text-white'
                          : activeTab === tab.id
                          ? 'bg-primary-500 text-white'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                      }`}>
                        {status === 'completed' ? '✓' : index + 1}
                      </div>
                      <span className={`text-sm ${
                        status === 'disabled'
                          ? 'text-gray-500 dark:text-gray-400'
                          : 'text-gray-900 dark:text-white'
                      }`}>
                        {tab.name}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Recent Analyses */}
            <RecentAnalyses />

            {/* Help & Support */}
            <div className="bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-xl p-6 border border-primary-100 dark:border-primary-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                تحتاج مساعدة؟
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
                فريق الدعم الفني متاح لمساعدتك في أي وقت
              </p>
              <div className="space-y-2">
                <button className="w-full btn btn-outline btn-sm text-left">
                  📚 مركز المساعدة
                </button>
                <button className="w-full btn btn-outline btn-sm text-left">
                  💬 الدردشة المباشرة
                </button>
                <button className="w-full btn btn-outline btn-sm text-left">
                  📧 التواصل عبر البريد
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardPage;