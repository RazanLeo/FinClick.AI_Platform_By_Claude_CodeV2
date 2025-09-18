import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  CheckIcon,
  XMarkIcon,
  StarIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

const PricingPreview: React.FC = () => {
  const { t } = useTranslation();

  const plans = [
    {
      id: 'free',
      name: t('pricing.plans.free.name', 'مجاني'),
      price: '0',
      currency: 'ريال',
      period: 'شهر',
      description: t('pricing.plans.free.description', 'للأفراد والطلاب'),
      popular: false,
      features: [
        '3 تحليلات شهرياً',
        'تحليلات أساسية (50 نوع)',
        'تقرير PDF أساسي',
        'دعم فني محدود',
        'واجهة باللغتين العربية والإنجليزية',
      ],
      limitations: [
        'بدون مقارنات معيارية',
        'بدون تصدير Excel/Word',
        'بدون رسوم بيانية متقدمة',
        'بدون API للتكامل',
        'بدون تحليلات المخاطر المتقدمة',
      ],
      cta: 'ابدأ مجاناً',
      ctaLink: '/auth?mode=register&plan=free',
    },
    {
      id: 'professional',
      name: t('pricing.plans.professional.name', 'احترافي'),
      price: '299',
      currency: 'ريال',
      period: 'شهر',
      description: t('pricing.plans.professional.description', 'للمحللين والشركات الصغيرة'),
      popular: true,
      features: [
        '50 تحليل شهرياً',
        'جميع التحليلات (180 نوع)',
        'تقارير متعددة الصيغ (PDF, Word, Excel, PPT)',
        'مقارنات معيارية شاملة',
        'رسوم بيانية تفاعلية',
        'دعم فني 24/7',
        'تحليلات المخاطر المتقدمة',
        'النمذجة المالية',
        'التحليل الإحصائي',
        'API أساسي للتكامل',
      ],
      limitations: [],
      cta: 'ابدأ التجربة المجانية',
      ctaLink: '/auth?mode=register&plan=professional',
    },
    {
      id: 'enterprise',
      name: t('pricing.plans.enterprise.name', 'مؤسسي'),
      price: 'تواصل معنا',
      currency: '',
      period: '',
      description: t('pricing.plans.enterprise.description', 'للشركات الكبيرة والمؤسسات'),
      popular: false,
      features: [
        'تحليلات غير محدودة',
        'تخصيص كامل للتقارير',
        'API متكامل للتطوير',
        'تدريب فريق العمل',
        'مدير حساب مخصص',
        'SLA مضمون 99.9%',
        'تكامل مع أنظمة ERP',
        'تحليلات مخصصة حسب القطاع',
        'نماذج تنبؤية متقدمة',
        'دعم فني مخصص',
        'تقارير عرض تقديمي مخصصة',
        'تحليل محافظ متعددة',
      ],
      limitations: [],
      cta: 'تواصل مع المبيعات',
      ctaLink: '/contact?plan=enterprise',
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
            {t('pricing.title', 'خطط الاشتراك')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed mb-8">
            {t('pricing.subtitle', 'اختر الخطة المناسبة لاحتياجاتك')}
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button className="px-4 py-2 text-sm font-medium text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-md shadow-sm">
              شهري
            </button>
            <button className="px-4 py-2 text-sm font-medium text-gray-500 dark:text-gray-400">
              سنوي
              <span className="ml-2 text-xs text-green-600 dark:text-green-400">وفر 20%</span>
            </button>
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid md:grid-cols-3 gap-8"
        >
          {plans.map((plan, index) => (
            <motion.div
              key={plan.id}
              variants={itemVariants}
              className={`relative group ${plan.popular ? 'md:-mt-4' : ''}`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                  <div className="bg-gradient-to-r from-primary-500 to-primary-600 text-white px-4 py-1 rounded-full text-sm font-medium flex items-center space-x-1 rtl:space-x-reverse">
                    <StarIcon className="w-4 h-4" />
                    <span>الأكثر شعبية</span>
                  </div>
                </div>
              )}

              <div className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-soft hover:shadow-medium transition-all duration-300 border-2 ${
                plan.popular
                  ? 'border-primary-500 shadow-lg'
                  : 'border-gray-100 dark:border-gray-700 hover:border-primary-200 dark:hover:border-primary-800'
              } h-full flex flex-col overflow-hidden`}>

                {/* Plan Header */}
                <div className={`p-8 ${plan.popular ? 'bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/10 dark:to-blue-900/10' : ''}`}>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-6">
                    {plan.description}
                  </p>

                  {/* Price */}
                  <div className="mb-6">
                    {plan.price === 'تواصل معنا' ? (
                      <div className="text-3xl font-bold text-gray-900 dark:text-white">
                        تواصل معنا
                      </div>
                    ) : (
                      <div className="flex items-baseline">
                        <span className="text-4xl font-bold gradient-text">{plan.price}</span>
                        <span className="text-lg text-gray-500 dark:text-gray-400 mr-2">
                          {plan.currency}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">/ {plan.period}</span>
                      </div>
                    )}
                  </div>

                  {/* CTA Button */}
                  <Link
                    to={plan.ctaLink}
                    className={`block w-full text-center py-3 px-6 rounded-xl font-semibold transition-all duration-200 ${
                      plan.popular
                        ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-xl hover:scale-105'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                  >
                    {plan.cta}
                  </Link>
                </div>

                {/* Features */}
                <div className="flex-1 p-8 pt-0">
                  <div className="space-y-4">
                    {/* Included Features */}
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                        <SparklesIcon className="w-4 h-4 text-green-500 mr-2" />
                        المميزات المشمولة
                      </h4>
                      <ul className="space-y-2">
                        {plan.features.map((feature, featureIndex) => (
                          <li key={featureIndex} className="flex items-start">
                            <CheckIcon className="w-4 h-4 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                            <span className="text-sm text-gray-700 dark:text-gray-300">{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Limitations */}
                    {plan.limitations.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                          <XMarkIcon className="w-4 h-4 text-gray-400 mr-2" />
                          غير مشمول
                        </h4>
                        <ul className="space-y-2">
                          {plan.limitations.map((limitation, limitationIndex) => (
                            <li key={limitationIndex} className="flex items-start">
                              <XMarkIcon className="w-4 h-4 text-gray-400 mt-0.5 mr-3 flex-shrink-0" />
                              <span className="text-sm text-gray-500 dark:text-gray-400">{limitation}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* FAQ Preview */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mt-16 text-center"
        >
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            أسئلة شائعة حول الأسعار
          </h3>
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <div className="text-left bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                هل يمكنني تجربة الخطة الاحترافية مجاناً؟
              </h4>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                نعم، نقدم تجربة مجانية لمدة 14 يوم للخطة الاحترافية مع إمكانية الوصول لجميع الميزات.
              </p>
            </div>
            <div className="text-left bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                هل يمكنني ترقية أو تخفيض خطتي في أي وقت؟
              </h4>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                بالطبع، يمكنك تغيير خطتك في أي وقت. التغييرات تطبق فوراً مع احتساب تناسبي للفترة المتبقية.
              </p>
            </div>
            <div className="text-left bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                هل تدعمون طرق دفع متعددة؟
              </h4>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                نعم، ندعم بطاقات الائتمان، التحويل البنكي، مدى، وطرق الدفع الإلكترونية المحلية.
              </p>
            </div>
            <div className="text-left bg-gray-50 dark:bg-gray-800 rounded-lg p-6">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                ماذا يحدث إذا تجاوزت حد التحليلات الشهرية؟
              </h4>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                يمكنك شراء تحليلات إضافية أو الترقية لخطة أعلى. نرسل تنبيهات عند اقتراب الحد.
              </p>
            </div>
          </div>

          <div className="mt-8">
            <Link
              to="/pricing"
              className="inline-flex items-center text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
            >
              عرض جميع التفاصيل والأسعار
              <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default PricingPreview;