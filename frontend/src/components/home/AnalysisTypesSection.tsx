import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChartBarIcon,
  AcademicCapIcon,
  BeakerIcon,
  CpuChipIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

const AnalysisTypesSection: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  const [activeCategory, setActiveCategory] = useState(0);

  const categories = [
    {
      id: 'classical',
      title: t('analysisTypes.categories.classical.title', 'التحليل الأساسي الكلاسيكي'),
      count: 106,
      description: t('analysisTypes.categories.classical.description', 'التحليلات المالية الأساسية والتقليدية'),
      icon: ChartBarIcon,
      color: 'blue',
      gradient: 'from-blue-500 to-indigo-600',
      subcategories: [
        {
          title: t('analysisTypes.categories.classical.subcategories.structural.title', 'التحليل الهيكلي'),
          count: 13,
          description: t('analysisTypes.categories.classical.subcategories.structural.description', 'تحليل هيكل القوائم المالية'),
          items: [
            'تحليل الهيكل العمودي للميزانية العمومية',
            'تحليل الهيكل الأفقي للميزانية العمومية',
            'تحليل هيكل قائمة الدخل',
            'تحليل هيكل قائمة التدفق النقدي',
            'تحليل التغيرات في حقوق الملكية',
            'تحليل هيكل رأس المال العامل',
            'تحليل التوزيع القطاعي للإيرادات',
            'تحليل هيكل التكاليف التشغيلية',
            'تحليل هيكل الأصول الثابتة',
            'تحليل هيكل الالتزامات طويلة الأجل',
            'تحليل مكونات الربحية',
            'تحليل هيكل المصروفات الإدارية',
            'تحليل التوزيع الجغرافي للأعمال'
          ]
        },
        {
          title: t('analysisTypes.categories.classical.subcategories.ratios.title', 'النسب المالية'),
          count: 75,
          description: t('analysisTypes.categories.classical.subcategories.ratios.description', 'جميع النسب المالية التقليدية'),
          items: [
            'نسب السيولة (15 نسبة)',
            'نسب الربحية (18 نسبة)',
            'نسب النشاط والكفاءة (12 نسبة)',
            'نسب الرافعة المالية (10 نسب)',
            'نسب السوق (8 نسب)',
            'نسب التشغيل (7 نسب)',
            'نسب النمو (5 نسب)'
          ]
        },
        {
          title: t('analysisTypes.categories.classical.subcategories.flow.title', 'تحليل التدفق والحركة'),
          count: 18,
          description: t('analysisTypes.categories.classical.subcategories.flow.description', 'تحليل التدفقات النقدية والحركة'),
          items: [
            'تحليل التدفق النقدي التشغيلي',
            'تحليل التدفق النقدي الاستثماري',
            'تحليل التدفق النقدي التمويلي',
            'تحليل دورة تحويل النقد',
            'تحليل حركة المخزون',
            'تحليل حركة الذمم المدينة',
            'تحليل حركة الذمم الدائنة',
            'تحليل معدل دوران الأصول',
            'تحليل الاحتياجات التمويلية',
            'تحليل مصادر واستخدامات الأموال',
            'تحليل التغيرات في رأس المال العامل',
            'تحليل كفاءة إدارة النقد',
            'تحليل التوزيعات النقدية',
            'تحليل الاستثمارات الرأسمالية',
            'تحليل هيكل التمويل',
            'تحليل السيولة النقدية المتاحة',
            'تحليل التدفق الحر للنقد',
            'تحليل قدرة توليد النقد'
          ]
        }
      ]
    },
    {
      id: 'intermediate',
      title: t('analysisTypes.categories.intermediate.title', 'التحليل التطبيقي المتوسط'),
      count: 21,
      description: t('analysisTypes.categories.intermediate.description', 'التحليلات المالية التطبيقية المتوسطة'),
      icon: AcademicCapIcon,
      color: 'emerald',
      gradient: 'from-emerald-500 to-teal-600',
      subcategories: [
        {
          title: t('analysisTypes.categories.intermediate.subcategories.comparison.title', 'المقارنة المتقدمة'),
          count: 3,
          description: t('analysisTypes.categories.intermediate.subcategories.comparison.description', 'مقارنات معيارية متقدمة'),
          items: [
            'المقارنة مع المنافسين المباشرين',
            'المقارنة مع متوسطات الصناعة',
            'التحليل المعياري متعدد المستويات'
          ]
        },
        {
          title: t('analysisTypes.categories.intermediate.subcategories.valuation.title', 'التقييم والاستثمار'),
          count: 13,
          description: t('analysisTypes.categories.intermediate.subcategories.valuation.description', 'تحليلات التقييم والاستثمار'),
          items: [
            'تقييم الشركة بالتدفق النقدي المخصوم',
            'تقييم الشركة بالقيمة الدفترية',
            'تقييم الشركة بمضاعفات السوق',
            'تحليل العائد على الاستثمار',
            'تحليل العائد على رأس المال المستثمر',
            'تحليل القيمة الاقتصادية المضافة',
            'تحليل نمو الأرباح المتوقع',
            'تحليل معدل النمو المستدام',
            'تحليل كفاءة استخدام رأس المال',
            'تحليل جودة الأرباح',
            'تحليل العوائد المعدلة بالمخاطر',
            'تحليل فترة الاسترداد',
            'تحليل صافي القيمة الحالية'
          ]
        },
        {
          title: t('analysisTypes.categories.intermediate.subcategories.performance.title', 'الأداء والكفاءة'),
          count: 5,
          description: t('analysisTypes.categories.intermediate.subcategories.performance.description', 'تحليل الأداء والكفاءة'),
          items: [
            'تحليل الأداء التشغيلي',
            'تحليل كفاءة الإدارة',
            'تحليل الأداء المالي المتكامل',
            'تحليل الإنتاجية والفعالية',
            'مؤشرات الأداء الرئيسية (KPIs)'
          ]
        }
      ]
    },
    {
      id: 'advanced',
      title: t('analysisTypes.categories.advanced.title', 'التحليل المتقدم والمتطور'),
      count: 53,
      description: t('analysisTypes.categories.advanced.description', 'التحليلات المالية المتقدمة والمتطورة'),
      icon: BeakerIcon,
      color: 'purple',
      gradient: 'from-purple-500 to-pink-600',
      subcategories: [
        {
          title: t('analysisTypes.categories.advanced.subcategories.modeling.title', 'النمذجة والمحاكاة'),
          count: 11,
          description: t('analysisTypes.categories.advanced.subcategories.modeling.description', 'نماذج مالية ومحاكاة'),
          items: [
            'نمذجة التدفق النقدي المستقبلي',
            'نماذج تقييم الخيارات المالية',
            'نمذجة مونت كارلو للمخاطر',
            'نماذج السيناريوهات المتعددة',
            'نمذجة الحساسية للمتغيرات',
            'النماذج التنبؤية للأداء',
            'نمذجة هيكل رأس المال الأمثل',
            'نماذج التسعير المتقدمة',
            'نمذجة دورات الأعمال',
            'نماذج المحاكاة الديناميكية',
            'النمذجة المالية المتكاملة'
          ]
        },
        {
          title: t('analysisTypes.categories.advanced.subcategories.statistical.title', 'التحليل الإحصائي'),
          count: 16,
          description: t('analysisTypes.categories.advanced.subcategories.statistical.description', 'تحليلات إحصائية متقدمة'),
          items: [
            'التحليل الإحصائي الوصفي',
            'تحليل الانحدار المتعدد',
            'تحليل الارتباط والتباين',
            'اختبارات الفرضيات الإحصائية',
            'التحليل العاملي',
            'تحليل السلاسل الزمنية',
            'التحليل التجميعي (Cluster Analysis)',
            'تحليل التمييز',
            'التحليل اللامعلمي',
            'تحليل البقاء الإحصائي',
            'النماذج الخطية المعممة',
            'التحليل البايزي',
            'تحليل البيانات الطولية',
            'التحليل متعدد المتغيرات',
            'تحليل الشذوذ الإحصائي',
            'اختبارات الاستقرار الإحصائي'
          ]
        },
        {
          title: t('analysisTypes.categories.advanced.subcategories.prediction.title', 'التنبؤ والائتمان'),
          count: 10,
          description: t('analysisTypes.categories.advanced.subcategories.prediction.description', 'تحليلات التنبؤ والائتمان'),
          items: [
            'نماذج التنبؤ بالإفلاس',
            'تحليل الجدارة الائتمانية',
            'نماذج التنبؤ بالتعثر المالي',
            'تحليل المخاطر الائتمانية',
            'نماذج التصنيف الائتماني',
            'التنبؤ بالتدفقات النقدية',
            'نماذج التنبؤ بالأرباح',
            'تحليل احتمالية السداد',
            'نماذج الإنذار المبكر',
            'التنبؤ بالاتجاهات المالية'
          ]
        },
        {
          title: t('analysisTypes.categories.advanced.subcategories.risk.title', 'المخاطر الكمية'),
          count: 25,
          description: t('analysisTypes.categories.advanced.subcategories.risk.description', 'تحليل المخاطر الكمية'),
          items: [
            'قياس المخاطر المالية (VaR)',
            'تحليل الضغط المالي',
            'مخاطر السوق',
            'مخاطر السيولة',
            'مخاطر التشغيل',
            'مخاطر الائتمان',
            'المخاطر النظامية',
            'تحليل الحساسية للمخاطر',
            'مؤشرات الاستقرار المالي',
            'نماذج المخاطر المتكاملة',
            'تحليل مخاطر التركز',
            'مخاطر أسعار الفائدة',
            'مخاطر أسعار الصرف',
            'مخاطر السلع الأساسية',
            'التحوط من المخاطر',
            'تحليل مخاطر المحفظة',
            'مؤشرات المخاطر المبكرة',
            'تحليل الارتباط في المخاطر',
            'نماذج انتشار المخاطر',
            'قياس المخاطر الطارئة',
            'تحليل سيناريوهات المخاطر',
            'مخاطر السمعة والامتثال',
            'المخاطر البيئية والاجتماعية',
            'تحليل مخاطر التكنولوجيا',
            'إدارة المخاطر المتكاملة'
          ]
        }
      ]
    }
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
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 via-white to-primary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center space-x-2 rtl:space-x-reverse bg-primary-100 dark:bg-primary-900/20 text-primary-800 dark:text-primary-200 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <SparklesIcon className="w-4 h-4" />
            <span>الأشمل في المنطقة العربية</span>
          </div>

          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="gradient-text">180</span>
            <br />
            <span className="text-gray-900 dark:text-white">
              {t('analysisTypes.title', 'نوع تحليل مالي')}
            </span>
          </h2>

          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            {t('analysisTypes.subtitle', 'أشمل مجموعة تحليلات مالية في العالم العربي - من الأساسي إلى المتقدم')}
          </p>
        </motion.div>

        {/* Categories Overview */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid md:grid-cols-3 gap-8 mb-16"
        >
          {categories.map((category, index) => (
            <motion.div
              key={category.id}
              variants={itemVariants}
              className={`cursor-pointer transition-all duration-300 ${
                activeCategory === index ? 'scale-105' : 'hover:scale-102'
              }`}
              onClick={() => setActiveCategory(index)}
            >
              <div className={`relative bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-soft hover:shadow-medium transition-all duration-300 border-2 ${
                activeCategory === index
                  ? 'border-primary-500 shadow-lg'
                  : 'border-gray-100 dark:border-gray-700'
              }`}>
                {/* Background Gradient */}
                <div className={`absolute inset-0 bg-gradient-to-br ${category.gradient} opacity-0 ${
                  activeCategory === index ? 'opacity-5' : 'group-hover:opacity-5'
                } rounded-2xl transition-opacity duration-300`}></div>

                {/* Icon and Count */}
                <div className="relative flex items-center justify-between mb-6">
                  <div className={`w-16 h-16 bg-gradient-to-br ${category.gradient} rounded-xl flex items-center justify-center`}>
                    <category.icon className="w-8 h-8 text-white" />
                  </div>
                  <div className={`text-4xl font-bold text-transparent bg-gradient-to-br ${category.gradient} bg-clip-text`}>
                    {category.count}
                  </div>
                </div>

                {/* Content */}
                <div className="relative">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                    {category.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                    {category.description}
                  </p>
                </div>

                {/* Active Indicator */}
                {activeCategory === index && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary-500 to-transparent"></div>
                )}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Detailed Breakdown */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeCategory}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            {/* Header */}
            <div className={`bg-gradient-to-r ${categories[activeCategory].gradient} px-8 py-6`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 rtl:space-x-reverse">
                  <categories[activeCategory].icon className="w-8 h-8 text-white" />
                  <div>
                    <h3 className="text-2xl font-bold text-white">
                      {categories[activeCategory].title}
                    </h3>
                    <p className="text-white/80">
                      {categories[activeCategory].count} نوع تحليل متاح
                    </p>
                  </div>
                </div>
                <div className="text-4xl font-bold text-white/80">
                  {categories[activeCategory].count}
                </div>
              </div>
            </div>

            {/* Subcategories */}
            <div className="p-8">
              <div className="grid lg:grid-cols-2 gap-8">
                {categories[activeCategory].subcategories.map((subcategory, subIndex) => (
                  <motion.div
                    key={subIndex}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: subIndex * 0.1 }}
                    className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-bold text-gray-900 dark:text-white">
                        {subcategory.title}
                      </h4>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r ${categories[activeCategory].gradient} text-white`}>
                        {subcategory.count}
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">
                      {subcategory.description}
                    </p>

                    {/* Analysis Items */}
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {subcategory.items.map((item, itemIndex) => (
                        <div key={itemIndex} className="flex items-start space-x-2 rtl:space-x-reverse">
                          <CheckCircleIcon className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-gray-700 dark:text-gray-300">{item}</span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="text-center mt-16"
        >
          <div className="bg-gradient-to-r from-primary-500 to-blue-600 rounded-2xl p-8 text-white">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              اكتشف قوة التحليل الشامل
            </h3>
            <p className="text-lg mb-6 opacity-90 max-w-2xl mx-auto">
              جميع هذه التحليلات متاحة في نقرة واحدة مع نتائج فورية ودقيقة بالذكاء الاصطناعي
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn bg-white text-primary-600 hover:bg-gray-100 font-semibold px-8 py-3 rounded-xl"
              >
                ابدأ التحليل الآن
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold px-8 py-3 rounded-xl transition-all duration-200"
              >
                تصفح جميع التحليلات
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default AnalysisTypesSection;