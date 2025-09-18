import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  PlayIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  SparklesIcon,
  ChartBarIcon,
  CpuChipIcon,
  GlobeAltIcon,
} from '@heroicons/react/24/outline';

const HeroSection: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  const features = [
    {
      icon: ChartBarIcon,
      text: t('hero.features.0', '180 نوع تحليل مالي متطور'),
    },
    {
      icon: CpuChipIcon,
      text: t('hero.features.1', '23 وكيل ذكاء اصطناعي مستقل'),
    },
    {
      icon: SparklesIcon,
      text: t('hero.features.2', 'تحليل فوري في أقل من 30 ثانية'),
    },
    {
      icon: GlobeAltIcon,
      text: t('hero.features.3', 'دعم 50+ قطاع و150+ نشاط'),
    },
  ];

  const stats = [
    {
      number: '180+',
      label: 'تحليل مالي',
      description: 'أنواع التحليل المتاحة',
    },
    {
      number: '23',
      label: 'وكيل ذكي',
      description: 'يعملون بالتوازي',
    },
    {
      number: '< 30',
      label: 'ثانية',
      description: 'زمن التحليل',
    },
    {
      number: '50+',
      label: 'قطاع',
      description: 'مدعوم في المنصة',
    },
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-gray-50 via-white to-primary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Background Elements */}
      <div className="absolute inset-0">
        {/* Gradient Orbs */}
        <div className="absolute top-20 left-10 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-primary-500/5 to-blue-500/5 rounded-full blur-3xl"></div>

        {/* Grid Pattern */}
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>

        {/* Floating Elements */}
        <div className="absolute top-1/4 left-1/4">
          <motion.div
            animate={{ y: [0, -20, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="w-8 h-8 bg-primary-500 rounded-lg opacity-20"
          ></motion.div>
        </div>
        <div className="absolute top-3/4 right-1/4">
          <motion.div
            animate={{ y: [0, -15, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            className="w-6 h-6 bg-blue-500 rounded-full opacity-20"
          ></motion.div>
        </div>
        <div className="absolute top-1/2 right-1/6">
          <motion.div
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="w-12 h-12 border-2 border-primary-500 rounded-lg opacity-10"
          ></motion.div>
        </div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-12 gap-12 items-center">
          {/* Hero Content */}
          <div className="lg:col-span-7">
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center space-x-2 rtl:space-x-reverse bg-primary-100 dark:bg-primary-900/20 text-primary-800 dark:text-primary-200 px-4 py-2 rounded-full text-sm font-medium mb-8"
            >
              <SparklesIcon className="w-4 h-4" />
              <span>أول منصة ذكاء اصطناعي للتحليل المالي في المنطقة العربية</span>
            </motion.div>

            {/* Main Title */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6"
            >
              <span className="gradient-text">FinClick.AI</span>
              <br />
              <span className="text-gray-900 dark:text-white">
                {t('hero.title', 'منصة التحليل المالي الذكي الثورية')}
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 leading-relaxed mb-8 max-w-3xl"
            >
              {t('hero.subtitle', 'أول منصة ذكاء اصطناعي متكاملة للتحليل المالي في المنطقة العربية تقدم 180 نوع تحليل مالي شامل ومتطور')}
            </motion.p>

            {/* Key Features */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="grid sm:grid-cols-2 gap-4 mb-10"
            >
              {features.map((feature, index) => (
                <div key={index} className="flex items-center space-x-3 rtl:space-x-reverse">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
                    <feature.icon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                  </div>
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    {feature.text}
                  </span>
                </div>
              ))}
            </motion.div>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4"
            >
              <Link
                to="/auth?mode=register"
                className="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:from-primary-600 hover:to-primary-700 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-105 group"
              >
                <span>{t('hero.cta.primary', 'ابدأ التحليل المجاني')}</span>
                <ArrowRightIcon className={`w-5 h-5 transition-transform group-hover:translate-x-1 ${isRTL ? 'mr-2 rtl-flip' : 'ml-2'}`} />
              </Link>

              <button className="inline-flex items-center justify-center px-8 py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-semibold rounded-xl border-2 border-gray-200 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-500 transition-all duration-200 hover:scale-105 group">
                <PlayIcon className={`w-5 h-5 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                <span>{t('hero.cta.secondary', 'شاهد عرض توضيحي')}</span>
              </button>
            </motion.div>

            {/* Social Proof */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="mt-12 flex items-center space-x-6 rtl:space-x-reverse"
            >
              <div className="flex items-center space-x-2 rtl:space-x-reverse text-sm text-gray-600 dark:text-gray-400">
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
                <span>مجاني للبدء</span>
              </div>
              <div className="flex items-center space-x-2 rtl:space-x-reverse text-sm text-gray-600 dark:text-gray-400">
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
                <span>بدون التزام</span>
              </div>
              <div className="flex items-center space-x-2 rtl:space-x-reverse text-sm text-gray-600 dark:text-gray-400">
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
                <span>نتائج فورية</span>
              </div>
            </motion.div>
          </div>

          {/* Hero Visual */}
          <div className="lg:col-span-5">
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.3 }}
              className="relative"
            >
              {/* Main Dashboard Preview */}
              <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 rtl:space-x-reverse">
                      <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                        <span className="text-primary-600 font-bold text-sm">F</span>
                      </div>
                      <span className="text-white font-semibold">FinClick.AI</span>
                    </div>
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                      <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                      <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                    </div>
                  </div>
                </div>

                {/* Content Preview */}
                <div className="p-6 space-y-6">
                  {/* Upload Area */}
                  <div className="border-2 border-dashed border-primary-300 dark:border-primary-600 rounded-lg p-6 text-center bg-primary-50 dark:bg-primary-900/10">
                    <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                      <svg className="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <p className="text-sm text-primary-700 dark:text-primary-300 font-medium">
                      ارفع القوائم المالية هنا
                    </p>
                  </div>

                  {/* Analysis Options */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">القطاع</label>
                      <div className="h-8 bg-gray-100 dark:bg-gray-700 rounded border"></div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">النشاط</label>
                      <div className="h-8 bg-gray-100 dark:bg-gray-700 rounded border"></div>
                    </div>
                  </div>

                  {/* Start Button */}
                  <button className="w-full py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-lg hover:from-primary-600 hover:to-primary-700 transition-all duration-200">
                    بدء التحليل
                  </button>
                </div>
              </div>

              {/* Floating Stats */}
              <div className="absolute -bottom-8 -left-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 min-w-[200px]">
                <div className="flex items-center space-x-3 rtl:space-x-reverse">
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                    <CheckCircleIcon className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white">تحليل مكتمل</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">في 28 ثانية</p>
                  </div>
                </div>
              </div>

              <div className="absolute -top-4 -right-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-3">
                <div className="flex items-center space-x-2 rtl:space-x-reverse">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300">23 وكيل نشط</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8"
        >
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
                className="text-3xl md:text-4xl font-bold gradient-text mb-2"
              >
                {stat.number}
              </motion.div>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {stat.label}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {stat.description}
              </p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;