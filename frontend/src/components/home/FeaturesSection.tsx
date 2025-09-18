import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  CpuChipIcon,
  ChartBarIcon,
  GlobeAltIcon,
  BoltIcon,
  LanguageIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

const FeaturesSection: React.FC = () => {
  const { t } = useTranslation();

  const features = [
    {
      icon: CpuChipIcon,
      title: t('features.items.aiPowered.title', 'مدعوم بالذكاء الاصطناعي'),
      description: t('features.items.aiPowered.description', '23 وكيل ذكاء اصطناعي مستقل يعملون بالتوازي لتحليل بياناتك المالية بدقة عالية وسرعة فائقة'),
      color: 'blue',
      gradient: 'from-blue-500 to-indigo-600',
    },
    {
      icon: ChartBarIcon,
      title: t('features.items.comprehensive.title', 'تحليل شامل ومتطور'),
      description: t('features.items.comprehensive.description', '180 نوع تحليل مالي يغطي جميع جوانب الأداء المالي من الأساسي إلى المتقدم والمتطور'),
      color: 'emerald',
      gradient: 'from-emerald-500 to-teal-600',
    },
    {
      icon: GlobeAltIcon,
      title: t('features.items.multiSector.title', 'متعدد القطاعات والأنشطة'),
      description: t('features.items.multiSector.description', 'دعم أكثر من 50 قطاع و150 نشاط مختلف مع مقارنات معيارية دقيقة لكل قطاع'),
      color: 'purple',
      gradient: 'from-purple-500 to-pink-600',
    },
    {
      icon: BoltIcon,
      title: t('features.items.instantResults.title', 'نتائج فورية'),
      description: t('features.items.instantResults.description', 'احصل على تحليل مالي شامل ومفصل في أقل من 30 ثانية مع تقارير احترافية جاهزة للعرض'),
      color: 'orange',
      gradient: 'from-orange-500 to-red-600',
    },
    {
      icon: LanguageIcon,
      title: t('features.items.multilingual.title', 'دعم متعدد اللغات'),
      description: t('features.items.multilingual.description', 'واجهة وتقارير باللغتين العربية والإنجليزية مع دعم كامل للاتجاه من اليمين إلى اليسار'),
      color: 'cyan',
      gradient: 'from-cyan-500 to-blue-600',
    },
    {
      icon: ShieldCheckIcon,
      title: t('features.items.secure.title', 'آمن ومتوافق'),
      description: t('features.items.secure.description', 'حماية عالية للبيانات مع التوافق مع معايير الأمان العالمية وقوانين حماية البيانات'),
      color: 'green',
      gradient: 'from-green-500 to-emerald-600',
    },
    {
      icon: DocumentTextIcon,
      title: t('features.items.flexible.title', 'مرونة في الاستخدام'),
      description: t('features.items.flexible.description', 'دعم جميع أنواع الملفات المالية مع إمكانية الرفع المتعدد والإدخال اليدوي'),
      color: 'indigo',
      gradient: 'from-indigo-500 to-purple-600',
    },
    {
      icon: SparklesIcon,
      title: t('features.items.professional.title', 'تقارير احترافية'),
      description: t('features.items.professional.description', 'تقارير مصممة بمعايير عالمية قابلة للتصدير بصيغ متعددة مع رسوم بيانية تفاعلية'),
      color: 'primary',
      gradient: 'from-primary-500 to-yellow-500',
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
        duration: 0.6,
      },
    },
  };

  return (
    <section className="py-20 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            {t('features.title', 'لماذا FinClick.AI؟')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            {t('features.subtitle', 'اكتشف المزايا التي تجعل منصتنا الخيار الأول للمحللين الماليين والمستثمرين')}
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="group relative"
            >
              <div className="relative bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-soft hover:shadow-medium transition-all duration-300 border border-gray-100 dark:border-gray-700 hover:border-primary-200 dark:hover:border-primary-800 h-full">
                {/* Background Gradient */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity duration-300`}></div>

                {/* Icon */}
                <div className={`relative w-14 h-14 bg-gradient-to-br ${feature.gradient} rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>

                {/* Content */}
                <div className="relative">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-300">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                    {feature.description}
                  </p>
                </div>

                {/* Hover Effect */}
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary-500 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="text-center mt-16"
        >
          <div className="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/10 dark:to-blue-900/10 rounded-2xl p-8 border border-primary-100 dark:border-primary-800">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              جاهز لتجربة المستقبل؟
            </h3>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-6 max-w-2xl mx-auto">
              انضم إلى آلاف المحللين الماليين والمستثمرين الذين يثقون في FinClick.AI لاتخاذ قرارات مالية ذكية
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn btn-primary btn-lg"
              >
                ابدأ تجربتك المجانية
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn btn-outline btn-lg"
              >
                تصفح المزيد من المميزات
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturesSection;