import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  CalendarDaysIcon,
  TrendingUpIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';

import { useAnalysis } from '../../contexts/AnalysisContext';
import { useAuth } from '../../contexts/AuthContext';

const QuickStats: React.FC = () => {
  const { t } = useTranslation();
  const { recentAnalyses } = useAnalysis();
  const { user } = useAuth();

  // Calculate stats
  const totalAnalyses = recentAnalyses.length;
  const completedAnalyses = recentAnalyses.filter(a => a.status === 'completed').length;
  const successRate = totalAnalyses > 0 ? Math.round((completedAnalyses / totalAnalyses) * 100) : 0;

  // Calculate average time (mock data for now)
  const avgTimeSeconds = 28;

  // Get this month's analyses
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  const thisMonthAnalyses = recentAnalyses.filter(analysis => {
    const analysisDate = new Date(analysis.startedAt);
    return analysisDate.getMonth() === currentMonth && analysisDate.getFullYear() === currentYear;
  }).length;

  // Get user's subscription plan
  const subscriptionPlan = user?.subscription?.plan || 'free';
  const planLimits = {
    free: { monthly: 3, total: '∞' },
    professional: { monthly: 50, total: '∞' },
    enterprise: { monthly: '∞', total: '∞' }
  };

  const stats = [
    {
      id: 'total',
      title: t('dashboard.quickStats.totalAnalyses', 'إجمالي التحليلات'),
      value: totalAnalyses.toString(),
      icon: ChartBarIcon,
      color: 'blue',
      change: '+12%',
      changeType: 'positive' as const,
    },
    {
      id: 'thisMonth',
      title: t('dashboard.quickStats.thisMonth', 'هذا الشهر'),
      value: `${thisMonthAnalyses}/${planLimits[subscriptionPlan as keyof typeof planLimits]?.monthly}`,
      icon: CalendarDaysIcon,
      color: 'green',
      change: `${thisMonthAnalyses} من ${planLimits[subscriptionPlan as keyof typeof planLimits]?.monthly}`,
      changeType: 'neutral' as const,
    },
    {
      id: 'successRate',
      title: t('dashboard.quickStats.successRate', 'معدل النجاح'),
      value: `${successRate}%`,
      icon: CheckCircleIcon,
      color: 'emerald',
      change: '+2%',
      changeType: 'positive' as const,
    },
    {
      id: 'avgTime',
      title: t('dashboard.quickStats.avgTime', 'متوسط الوقت'),
      value: `${avgTimeSeconds}ث`,
      icon: ClockIcon,
      color: 'purple',
      change: '-3ث',
      changeType: 'positive' as const,
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  return (
    <div className="mb-8">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {stats.map((stat) => (
          <motion.div
            key={stat.id}
            variants={itemVariants}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700 hover:shadow-medium transition-shadow duration-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 rtl:space-x-reverse mb-2">
                  <div className={`p-2 rounded-lg bg-${stat.color}-100 dark:bg-${stat.color}-900/20`}>
                    <stat.icon className={`w-5 h-5 text-${stat.color}-600 dark:text-${stat.color}-400`} />
                  </div>
                </div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                  {stat.title}
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stat.value}
                </p>
                <div className="flex items-center mt-2">
                  <span
                    className={`text-xs font-medium ${
                      stat.changeType === 'positive'
                        ? 'text-green-600 dark:text-green-400'
                        : stat.changeType === 'negative'
                        ? 'text-red-600 dark:text-red-400'
                        : 'text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    {stat.change}
                  </span>
                  {stat.changeType === 'positive' && (
                    <TrendingUpIcon className="w-3 h-3 text-green-600 dark:text-green-400 ml-1" />
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="mt-6 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/10 dark:to-blue-900/10 rounded-xl p-6 border border-primary-100 dark:border-primary-800"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              إجراءات سريعة
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">
              ابدأ تحليل جديد أو تصفح تحليلاتك السابقة
            </p>
          </div>
          <div className="flex space-x-3 rtl:space-x-reverse">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn btn-primary btn-sm"
            >
              <ChartBarIcon className="w-4 h-4 mr-2" />
              تحليل جديد
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn btn-outline btn-sm"
            >
              <DocumentTextIcon className="w-4 h-4 mr-2" />
              التحليلات السابقة
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Subscription Status */}
      {user && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-4 bg-white dark:bg-gray-800 rounded-xl p-4 shadow-soft border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 rtl:space-x-reverse">
              <div className={`w-3 h-3 rounded-full ${
                user.subscription.status === 'active' ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <div>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  خطة {subscriptionPlan === 'free' ? 'مجانية' : subscriptionPlan === 'professional' ? 'احترافية' : 'مؤسسية'}
                </span>
                <span className={`ml-2 text-xs px-2 py-1 rounded-full ${
                  user.subscription.status === 'active'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                    : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                }`}>
                  {user.subscription.status === 'active' ? 'نشطة' : 'غير نشطة'}
                </span>
              </div>
            </div>
            {subscriptionPlan === 'free' && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
              >
                ترقية الخطة
              </motion.button>
            )}
          </div>

          {subscriptionPlan !== 'enterprise' && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                <span>الاستخدام الشهري</span>
                <span>{thisMonthAnalyses} / {planLimits[subscriptionPlan as keyof typeof planLimits]?.monthly}</span>
              </div>
              <div className="progress">
                <div
                  className="progress-bar"
                  style={{
                    width: `${subscriptionPlan === 'free' ? (thisMonthAnalyses / 3) * 100 : (thisMonthAnalyses / 50) * 100}%`
                  }}
                />
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default QuickStats;