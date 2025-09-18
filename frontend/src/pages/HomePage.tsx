import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  CpuChipIcon,
  DocumentChartBarIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  BoltIcon,
  CheckCircleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

// Components
import HeroSection from '../components/home/HeroSection';
import FeaturesSection from '../components/home/FeaturesSection';
import AnalysisTypesSection from '../components/home/AnalysisTypesSection';
import TestimonialsSection from '../components/home/TestimonialsSection';
import PricingPreview from '../components/home/PricingPreview';
import FAQSection from '../components/home/FAQSection';
import CTASection from '../components/home/CTASection';

const HomePage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <HeroSection />

      {/* Key Features */}
      <FeaturesSection />

      {/* Analysis Types Preview */}
      <AnalysisTypesSection />

      {/* How It Works Section */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {t('howItWorks.title', 'كيف تعمل المنصة')}
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              {t('howItWorks.subtitle', 'ثلاث خطوات بسيطة للحصول على تحليل مالي شامل واحترافي')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1: Upload */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-center p-8 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20"
            >
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <DocumentChartBarIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                {t('steps.upload.title', '1. أرفق المستندات')}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {t('steps.upload.description', 'ارفع القوائم المالية أو موازين المراجعة بأي صيغة (PDF, Excel, Word, صور)')}
              </p>
              <ul className="mt-4 text-sm text-gray-500 dark:text-gray-400 space-y-1">
                <li>• {t('steps.upload.feature1', 'دعم 10 ملفات بأحجام غير محدودة')}</li>
                <li>• {t('steps.upload.feature2', 'تقنية OCR للمستندات الممسوحة')}</li>
                <li>• {t('steps.upload.feature3', 'إدخال يدوي في قوالب جاهزة')}</li>
              </ul>
            </motion.div>

            {/* Step 2: Select Options */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-center p-8 rounded-2xl bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20"
            >
              <div className="w-16 h-16 bg-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <CpuChipIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                {t('steps.options.title', '2. حدد خيارات التحليل')}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {t('steps.options.description', 'اختر اللغة والقطاع والنشاط ونوع المقارنة والتحليلات المطلوبة')}
              </p>
              <ul className="mt-4 text-sm text-gray-500 dark:text-gray-400 space-y-1">
                <li>• {t('steps.options.feature1', 'أكثر من 50 قطاع و150 نشاط')}</li>
                <li>• {t('steps.options.feature2', 'مقارنات على 9 مستويات جغرافية')}</li>
                <li>• {t('steps.options.feature3', 'تحليل شامل أو تحليلات محددة')}</li>
              </ul>
            </motion.div>

            {/* Step 3: Get Results */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-center p-8 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20"
            >
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <ChartBarIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                {t('steps.results.title', '3. احصل على التحليل')}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {t('steps.results.description', 'تحليل شامل جاهز في أقل من 30 ثانية مع تقارير احترافية')}
              </p>
              <ul className="mt-4 text-sm text-gray-500 dark:text-gray-400 space-y-1">
                <li>• {t('steps.results.feature1', '180 نوع تحليل مالي')}</li>
                <li>• {t('steps.results.feature2', 'تقارير PDF, Word, Excel, PPT')}</li>
                <li>• {t('steps.results.feature3', 'رسوم بيانية تفاعلية')}</li>
              </ul>
            </motion.div>
          </div>

          {/* CTA Button */}
          <div className="text-center mt-12">
            <Link
              to="/auth"
              className="inline-flex items-center px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-full hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              {t('cta.tryNow', 'جرب الآن مجاناً')}
              <ArrowRightIcon className={`w-5 h-5 ${isRTL ? 'mr-2' : 'ml-2'}`} />
            </Link>
          </div>
        </div>
      </section>

      {/* 180 Analysis Types Highlight */}
      <section className="py-20 bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              {t('analysisTypes.title', '180 نوع تحليل مالي')}
            </h2>
            <p className="text-xl opacity-90 max-w-3xl mx-auto">
              {t('analysisTypes.subtitle', 'أشمل مجموعة تحليلات مالية في العالم - من الأساسي إلى المتقدم')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Classical Foundational */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20"
            >
              <div className="text-center">
                <div className="w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl font-bold">106</span>
                </div>
                <h3 className="text-2xl font-bold mb-4">
                  {t('categories.classical.title', 'التحليل الأساسي الكلاسيكي')}
                </h3>
                <div className="space-y-3 text-left">
                  <div className="flex items-center justify-between">
                    <span>{t('categories.classical.structural', 'التحليل الهيكلي')}</span>
                    <span className="bg-blue-500 px-2 py-1 rounded text-sm">13</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{t('categories.classical.ratios', 'النسب المالية')}</span>
                    <span className="bg-blue-500 px-2 py-1 rounded text-sm">75</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{t('categories.classical.flow', 'تحليل التدفق والحركة')}</span>
                    <span className="bg-blue-500 px-2 py-1 rounded text-sm">18</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Applied Intermediate */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20"
            >
              <div className="text-center">
                <div className="w-20 h-20 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl font-bold">21</span>
                </div>
                <h3 className="text-2xl font-bold mb-4">
                  {t('categories.intermediate.title', 'التحليل التطبيقي المتوسط')}
                </h3>
                <div className="space-y-3 text-left">
                  <div className="flex items-center justify-between">
                    <span>{t('categories.intermediate.comparison', 'المقارنة المتقدمة')}</span>
                    <span className="bg-emerald-500 px-2 py-1 rounded text-sm">3</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{t('categories.intermediate.valuation', 'التقييم والاستثمار')}</span>
                    <span className="bg-emerald-500 px-2 py-1 rounded text-sm">13</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{t('categories.intermediate.performance', 'الأداء والكفاءة')}</span>
                    <span className="bg-emerald-500 px-2 py-1 rounded text-sm">5</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Advanced Sophisticated */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20"
            >
              <div className="text-center">
                <div className="w-20 h-20 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-3xl font-bold">53</span>
                </div>
                <h3 className="text-2xl font-bold mb-4">
                  {t('categories.advanced.title', 'التحليل المتقدم والمتطور')}
                </h3>
                <div className="space-y-2 text-sm text-left">
                  <div className="flex items-center justify-between">
                    <span>{t('categories.advanced.modeling', 'النمذجة والمحاكاة')}</span>
                    <span className="bg-purple-500 px-2 py-1 rounded text-xs">11</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{t('categories.advanced.statistical', 'التحليل الإحصائي')}</span>
                    <span className="bg-purple-500 px-2 py-1 rounded text-xs">16</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{t('categories.advanced.prediction', 'التنبؤ والائتمان')}</span>
                    <span className="bg-purple-500 px-2 py-1 rounded text-xs">10</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{t('categories.advanced.risk', 'المخاطر الكمية')}</span>
                    <span className="bg-purple-500 px-2 py-1 rounded text-xs">25</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* AI Agents Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {t('aiAgents.title', 'وكلاء الذكاء الاصطناعي')}
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              {t('aiAgents.subtitle', '23 وكيل ذكاء اصطناعي مستقل يعملون معاً لتقديم تحليل مالي شامل')}
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                name: t('agents.ingestion.name', 'وكيل الاستيعاب'),
                description: t('agents.ingestion.desc', 'استخراج البيانات من جميع أنواع الملفات'),
                icon: DocumentChartBarIcon,
                color: 'blue'
              },
              {
                name: t('agents.structuring.name', 'وكيل الهيكلة'),
                description: t('agents.structuring.desc', 'تنظيف وهيكلة البيانات حسب معايير IFRS'),
                icon: CpuChipIcon,
                color: 'emerald'
              },
              {
                name: t('agents.benchmark.name', 'وكيل المقارنة المعيارية'),
                description: t('agents.benchmark.desc', 'جمع بيانات المنافسين ومتوسطات الصناعة'),
                icon: GlobeAltIcon,
                color: 'purple'
              },
              {
                name: t('agents.analysis.name', 'وكيل التحليل'),
                description: t('agents.analysis.desc', 'تنفيذ 180 نوع تحليل مالي بالتوازي'),
                icon: ChartBarIcon,
                color: 'orange'
              },
              {
                name: t('agents.narrative.name', 'وكيل السرد'),
                description: t('agents.narrative.desc', 'توليد التفسيرات والتوصيات بلغتين'),
                icon: DocumentChartBarIcon,
                color: 'pink'
              },
              {
                name: t('agents.compliance.name', 'وكيل الامتثال'),
                description: t('agents.compliance.desc', 'ضمان الامتثال والخصوصية والأمان'),
                icon: ShieldCheckIcon,
                color: 'red'
              }
            ].map((agent, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow"
              >
                <div className={`w-12 h-12 bg-${agent.color}-100 dark:bg-${agent.color}-900/20 rounded-lg flex items-center justify-center mb-4`}>
                  <agent.icon className={`w-6 h-6 text-${agent.color}-600 dark:text-${agent.color}-400`} />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {agent.name}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 text-sm">
                  {agent.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <TestimonialsSection />

      {/* Pricing Preview */}
      <PricingPreview />

      {/* FAQ */}
      <FAQSection />

      {/* Final CTA */}
      <CTASection />
    </div>
  );
};

export default HomePage;