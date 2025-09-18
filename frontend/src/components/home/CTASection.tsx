import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  ArrowRightIcon,
  SparklesIcon,
  CheckCircleIcon,
  PlayIcon,
} from '@heroicons/react/24/outline';

const CTASection: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  const benefits = [
    'ابدأ في دقائق - لا حاجة لبطاقة ائتمانية',
    'احصل على 3 تحليلات مجانية شهرياً',
    'وصول فوري لـ50 نوع تحليل أساسي',
    'دعم كامل باللغة العربية',
    'تقارير احترافية جاهزة للاستخدام',
  ];

  const stats = [
    { number: '10,000+', label: 'مستخدم راضٍ' },
    { number: '98%', label: 'معدل رضا العملاء' },
    { number: '< 30', label: 'ثانية للنتائج' },
    { number: '24/7', label: 'دعم فني' },
  ];

  return (
    <section className="relative py-20 overflow-hidden">
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-blue-800"></div>

      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-full h-full bg-grid-pattern"></div>
      </div>

      {/* Floating Elements */}
      <div className="absolute top-10 left-10 w-32 h-32 bg-white/5 rounded-full blur-xl"></div>
      <div className="absolute bottom-10 right-10 w-40 h-40 bg-white/5 rounded-full blur-xl"></div>
      <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-white/5 rounded-full blur-xl"></div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Content */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
          >
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 rtl:space-x-reverse bg-white/10 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-medium mb-6">
              <SparklesIcon className="w-4 h-4" />
              <span>ابدأ رحلتك في التحليل المالي الذكي</span>
            </div>

            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
              جاهز لتحويل
              <br />
              <span className="text-yellow-300">تحليلك المالي؟</span>
            </h2>

            <p className="text-xl text-white/90 leading-relaxed mb-8 max-w-xl">
              انضم إلى آلاف المحللين الماليين والمستثمرين الذين يثقون في FinClick.AI لاتخاذ قرارات مالية ذكية ومدروسة
            </p>

            {/* Benefits */}
            <div className="space-y-3 mb-8">
              {benefits.map((benefit, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="flex items-center space-x-3 rtl:space-x-reverse"
                >
                  <CheckCircleIcon className="w-5 h-5 text-green-400 flex-shrink-0" />
                  <span className="text-white/90">{benefit}</span>
                </motion.div>
              ))}
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 mb-8">
              <Link
                to="/auth?mode=register"
                className="inline-flex items-center justify-center px-8 py-4 bg-white text-primary-600 font-semibold rounded-xl hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-105 group"
              >
                <span>ابدأ مجاناً الآن</span>
                <ArrowRightIcon className={`w-5 h-5 transition-transform group-hover:translate-x-1 ${isRTL ? 'mr-2 rtl-flip' : 'ml-2'}`} />
              </Link>

              <button className="inline-flex items-center justify-center px-8 py-4 bg-transparent border-2 border-white text-white font-semibold rounded-xl hover:bg-white hover:text-primary-600 transition-all duration-200 group">
                <PlayIcon className={`w-5 h-5 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                <span>شاهد العرض التوضيحي</span>
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center space-x-4 rtl:space-x-reverse text-sm text-white/70">
              <span>✨ بدء فوري</span>
              <span>🔒 آمن ومحمي</span>
              <span>📞 دعم عربي كامل</span>
            </div>
          </motion.div>

          {/* Visual/Stats */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative"
          >
            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-6 mb-8">
              {stats.map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center border border-white/20"
                >
                  <div className="text-3xl md:text-4xl font-bold text-white mb-2">
                    {stat.number}
                  </div>
                  <div className="text-white/80 text-sm">
                    {stat.label}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Interactive Demo Preview */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20"
            >
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-white">تجربة سريعة</h4>
                <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-3 rtl:space-x-reverse">
                  <div className="w-8 h-8 bg-green-400 rounded-full flex items-center justify-center">
                    <CheckCircleIcon className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-white/90 text-sm">رفع الملفات</span>
                </div>

                <div className="flex items-center space-x-3 rtl:space-x-reverse">
                  <div className="w-8 h-8 bg-green-400 rounded-full flex items-center justify-center">
                    <CheckCircleIcon className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-white/90 text-sm">معالجة البيانات</span>
                </div>

                <div className="flex items-center space-x-3 rtl:space-x-reverse">
                  <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center animate-pulse">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                  <span className="text-white/90 text-sm">تحليل البيانات...</span>
                </div>
              </div>

              <div className="mt-4 p-3 bg-white/5 rounded-lg">
                <div className="text-xs text-white/70 mb-1">الوقت المتوقع</div>
                <div className="text-2xl font-bold text-white">28 ثانية</div>
              </div>
            </motion.div>

            {/* Floating Success Message */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="absolute -top-4 -right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-medium"
            >
              ✅ 180 تحليل مكتمل!
            </motion.div>
          </motion.div>
        </div>

        {/* Bottom Text */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-center mt-16"
        >
          <p className="text-white/70 text-sm max-w-2xl mx-auto">
            بالنقر على "ابدأ مجاناً الآن"، فإنك توافق على
            <Link to="/terms" className="text-white hover:text-yellow-300 underline mx-1">شروط الاستخدام</Link>
            و
            <Link to="/privacy" className="text-white hover:text-yellow-300 underline mx-1">سياسة الخصوصية</Link>
            الخاصة بنا
          </p>
        </motion.div>
      </div>
    </section>
  );
};

export default CTASection;