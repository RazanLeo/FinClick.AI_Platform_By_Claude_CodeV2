import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  CheckIcon,
  XMarkIcon,
  SparklesIcon,
  RocketLaunchIcon,
  BuildingOfficeIcon,
  CrownIcon,
  CreditCardIcon,
  DevicePhoneMobileIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

// Subscription plans as specified in the prompt
const PRICING_PLANS = [
  {
    id: 'free',
    nameAr: 'المجاني',
    nameEn: 'Free',
    priceMonthly: 0,
    priceYearly: 0,
    analyses: 5,
    descriptionAr: 'للمستخدمين الجدد والتجربة',
    descriptionEn: 'For new users and trial',
    icon: SparklesIcon,
    color: 'gray',
    popular: false,
    features: [
      { keyAr: '5 تحليلات شهرياً', keyEn: '5 monthly analyses', included: true },
      { keyAr: 'تقارير PDF أساسية', keyEn: 'Basic PDF reports', included: true },
      { keyAr: 'الدعم الفني عبر البريد', keyEn: 'Email support', included: true },
      { keyAr: 'التحليل الأساسي الكلاسيكي', keyEn: 'Classical basic analysis', included: true },
      { keyAr: 'رسوم بيانية أساسية', keyEn: 'Basic charts', included: true },
      { keyAr: 'حفظ البيانات 30 يوم', keyEn: '30-day data retention', included: true },
      { keyAr: 'تقارير Excel و Word', keyEn: 'Excel & Word reports', included: false },
      { keyAr: 'التحليل المتقدم', keyEn: 'Advanced analysis', included: false },
      { keyAr: 'المقارنات المعيارية', keyEn: 'Benchmark comparisons', included: false },
      { keyAr: 'عروض PowerPoint', keyEn: 'PowerPoint presentations', included: false },
      { keyAr: 'API access', keyEn: 'API access', included: false },
      { keyAr: 'دعم الواتساب والهاتف', keyEn: 'WhatsApp & phone support', included: false }
    ]
  },
  {
    id: 'basic',
    nameAr: 'الأساسي',
    nameEn: 'Basic',
    priceMonthly: 29,
    priceYearly: 290, // 2 months free
    analyses: 50,
    descriptionAr: 'للشركات الصغيرة والمتوسطة',
    descriptionEn: 'For small and medium businesses',
    icon: RocketLaunchIcon,
    color: 'blue',
    popular: true,
    features: [
      { keyAr: '50 تحليل شهرياً', keyEn: '50 monthly analyses', included: true },
      { keyAr: 'جميع أنواع التقارير', keyEn: 'All report types', included: true },
      { keyAr: 'التحليل الأساسي والتطبيقي', keyEn: 'Basic & applied analysis', included: true },
      { keyAr: 'المقارنات المعيارية', keyEn: 'Benchmark comparisons', included: true },
      { keyAr: 'رسوم بيانية متقدمة', keyEn: 'Advanced charts', included: true },
      { keyAr: 'عروض PowerPoint', keyEn: 'PowerPoint presentations', included: true },
      { keyAr: 'حفظ البيانات 6 أشهر', keyEn: '6-month data retention', included: true },
      { keyAr: 'دعم فني أولوية', keyEn: 'Priority support', included: true },
      { keyAr: 'تدريب أساسي', keyEn: 'Basic training', included: true },
      { keyAr: 'التحليل المتقدم', keyEn: 'Advanced analysis', included: false },
      { keyAr: 'التحليلات اللامحدودة', keyEn: 'Unlimited analyses', included: false },
      { keyAr: 'API access', keyEn: 'API access', included: false }
    ]
  },
  {
    id: 'advanced',
    nameAr: 'المتقدم',
    nameEn: 'Advanced',
    priceMonthly: 99,
    priceYearly: 990, // 2 months free
    analyses: 200,
    descriptionAr: 'للشركات المتوسطة والكبيرة',
    descriptionEn: 'For medium and large businesses',
    icon: BuildingOfficeIcon,
    color: 'emerald',
    popular: false,
    features: [
      { keyAr: '200 تحليل شهرياً', keyEn: '200 monthly analyses', included: true },
      { keyAr: 'جميع أنواع التحليلات (180)', keyEn: 'All analysis types (180)', included: true },
      { keyAr: 'التحليل المتقدم والمتطور', keyEn: 'Advanced & sophisticated analysis', included: true },
      { keyAr: 'تحليلات مخصصة', keyEn: 'Custom analyses', included: true },
      { keyAr: 'API محدود', keyEn: 'Limited API access', included: true },
      { keyAr: 'تقارير مخصصة', keyEn: 'Custom reports', included: true },
      { keyAr: 'حفظ البيانات سنة كاملة', keyEn: '1-year data retention', included: true },
      { keyAr: 'دعم فني VIP', keyEn: 'VIP support', included: true },
      { keyAr: 'تدريب متقدم', keyEn: 'Advanced training', included: true },
      { keyAr: 'استشارة شهرية', keyEn: 'Monthly consultation', included: true },
      { keyAr: 'تكامل مع الأنظمة', keyEn: 'System integration', included: true },
      { keyAr: 'تحليلات لامحدودة', keyEn: 'Unlimited analyses', included: false }
    ]
  },
  {
    id: 'enterprise',
    nameAr: 'المؤسسي',
    nameEn: 'Enterprise',
    priceMonthly: 299,
    priceYearly: 2990, // 2 months free
    analyses: -1, // Unlimited
    descriptionAr: 'للمؤسسات والشركات الكبرى',
    descriptionEn: 'For enterprises and large corporations',
    icon: CrownIcon,
    color: 'purple',
    popular: false,
    features: [
      { keyAr: 'تحليلات لامحدودة', keyEn: 'Unlimited analyses', included: true },
      { keyAr: 'جميع الميزات المتقدمة', keyEn: 'All advanced features', included: true },
      { keyAr: 'API كامل غير محدود', keyEn: 'Full unlimited API', included: true },
      { keyAr: 'تحليلات مخصصة حسب الطلب', keyEn: 'Custom on-demand analyses', included: true },
      { keyAr: 'تقارير مخصصة بالعلامة التجارية', keyEn: 'White-label reports', included: true },
      { keyAr: 'حفظ البيانات بلا حدود', keyEn: 'Unlimited data retention', included: true },
      { keyAr: 'مدير حساب مخصص', keyEn: 'Dedicated account manager', included: true },
      { keyAr: 'دعم فني 24/7', keyEn: '24/7 support', included: true },
      { keyAr: 'تدريب شامل للفريق', keyEn: 'Comprehensive team training', included: true },
      { keyAr: 'استشارات أسبوعية', keyEn: 'Weekly consultations', included: true },
      { keyAr: 'تكامل كامل مع الأنظمة', keyEn: 'Full system integration', included: true },
      { keyAr: 'أولوية في الميزات الجديدة', keyEn: 'Priority for new features', included: true }
    ]
  }
];

// Payment methods as specified
const PAYMENT_METHODS = [
  { id: 'credit_card', nameAr: 'بطاقة ائتمان', nameEn: 'Credit Card', icon: CreditCardIcon },
  { id: 'paypal', nameAr: 'PayPal', nameEn: 'PayPal', icon: CreditCardIcon },
  { id: 'apple_pay', nameAr: 'Apple Pay', nameEn: 'Apple Pay', icon: DevicePhoneMobileIcon },
  { id: 'google_pay', nameAr: 'Google Pay', nameEn: 'Google Pay', icon: DevicePhoneMobileIcon },
  { id: 'bank_transfer', nameAr: 'تحويل بنكي', nameEn: 'Bank Transfer', icon: CreditCardIcon },
  { id: 'stc_pay', nameAr: 'STC Pay', nameEn: 'STC Pay', icon: DevicePhoneMobileIcon }
];

const PricingPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const formatPrice = (monthly: number, yearly: number) => {
    const price = billingCycle === 'monthly' ? monthly : Math.round(yearly / 12);
    return price === 0 ? t('pricing.free', 'مجاناً') : `$${price}`;
  };

  const getSavings = (monthly: number, yearly: number) => {
    if (monthly === 0) return 0;
    const monthlyCost = monthly * 12;
    const savings = monthlyCost - yearly;
    return Math.round((savings / monthlyCost) * 100);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-3xl mx-auto"
          >
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              {t('pricing.title', 'خطط الاشتراك والأسعار')}
            </h1>
            <p className="text-xl opacity-90 mb-8">
              {t('pricing.subtitle', 'اختر الخطة المناسبة لاحتياجاتك وابدأ رحلة التحليل المالي الذكي')}
            </p>

            {/* Billing Toggle */}
            <div className="inline-flex items-center bg-white/10 backdrop-blur-sm rounded-full p-1">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
                  billingCycle === 'monthly'
                    ? 'bg-white text-blue-900 shadow-lg'
                    : 'text-white hover:bg-white/10'
                }`}
              >
                {t('pricing.monthly', 'شهري')}
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
                  billingCycle === 'yearly'
                    ? 'bg-white text-blue-900 shadow-lg'
                    : 'text-white hover:bg-white/10'
                }`}
              >
                {t('pricing.yearly', 'سنوي')}
                <span className="ml-2 px-2 py-1 bg-emerald-500 text-white text-xs rounded-full">
                  {t('pricing.save', 'وفر')} 17%
                </span>
              </button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {PRICING_PLANS.map((plan, index) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 ${
                plan.popular ? 'ring-2 ring-blue-500 scale-105' : ''
              } ${selectedPlan === plan.id ? 'ring-2 ring-purple-500' : ''}`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-blue-500 text-white text-sm font-medium px-4 py-1 rounded-full">
                    {t('pricing.popular', 'الأكثر شيوعاً')}
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="text-center mb-8">
                <div className={`inline-flex items-center justify-center w-16 h-16 bg-${plan.color}-100 dark:bg-${plan.color}-900/20 rounded-full mb-4`}>
                  <plan.icon className={`w-8 h-8 text-${plan.color}-600 dark:text-${plan.color}-400`} />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {isRTL ? plan.nameAr : plan.nameEn}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                  {isRTL ? plan.descriptionAr : plan.descriptionEn}
                </p>
              </div>

              {/* Price */}
              <div className="text-center mb-8">
                <div className="text-4xl font-bold text-gray-900 dark:text-white">
                  {formatPrice(plan.priceMonthly, plan.priceYearly)}
                  {plan.priceMonthly > 0 && (
                    <span className="text-lg text-gray-500 dark:text-gray-400">
                      /{billingCycle === 'monthly' ? t('pricing.month', 'شهر') : t('pricing.monthInYear', 'شهر')}
                    </span>
                  )}
                </div>

                {billingCycle === 'yearly' && plan.priceMonthly > 0 && (
                  <div className="text-sm text-emerald-600 dark:text-emerald-400 mt-2">
                    {t('pricing.billed', 'يُفوتر سنوياً')} ${plan.priceYearly}
                    <span className="ml-1">
                      ({t('pricing.save', 'وفر')} {getSavings(plan.priceMonthly, plan.priceYearly)}%)
                    </span>
                  </div>
                )}

                <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                  {plan.analyses === -1
                    ? t('pricing.unlimited', 'تحليلات لامحدودة')
                    : `${plan.analyses} ${t('pricing.analysesPerMonth', 'تحليل شهرياً')}`
                  }
                </div>
              </div>

              {/* Features */}
              <div className="space-y-3 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <div key={featureIndex} className="flex items-center">
                    {feature.included ? (
                      <CheckIcon className="w-5 h-5 text-emerald-500 mr-3 flex-shrink-0" />
                    ) : (
                      <XMarkIcon className="w-5 h-5 text-gray-400 mr-3 flex-shrink-0" />
                    )}
                    <span className={`text-sm ${
                      feature.included
                        ? 'text-gray-900 dark:text-white'
                        : 'text-gray-500 dark:text-gray-400 line-through'
                    }`}>
                      {isRTL ? feature.keyAr : feature.keyEn}
                    </span>
                  </div>
                ))}
              </div>

              {/* CTA Button */}
              <button
                onClick={() => setSelectedPlan(plan.id)}
                className={`w-full py-3 px-6 rounded-lg font-medium transition-all ${
                  plan.popular
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : selectedPlan === plan.id
                    ? 'bg-purple-600 hover:bg-purple-700 text-white'
                    : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white'
                }`}
              >
                {plan.priceMonthly === 0
                  ? t('pricing.startFree', 'ابدأ مجاناً')
                  : selectedPlan === plan.id
                  ? t('pricing.selected', 'تم اختيارها')
                  : t('pricing.choosePlan', 'اختر هذه الخطة')
                }
              </button>
            </motion.div>
          ))}
        </div>

        {/* Payment Methods */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-20 text-center"
        >
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
            {t('pricing.paymentMethods', 'طرق الدفع المتاحة')}
          </h3>
          <div className="flex flex-wrap justify-center gap-6">
            {PAYMENT_METHODS.map((method) => (
              <div
                key={method.id}
                className="flex items-center space-x-3 bg-white dark:bg-gray-800 rounded-lg px-6 py-3 shadow-lg"
              >
                <method.icon className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {isRTL ? method.nameAr : method.nameEn}
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Features Comparison */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-20"
        >
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white text-center mb-12">
            {t('pricing.featuresComparison', 'مقارنة الميزات بالتفصيل')}
          </h3>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-900 dark:text-white">
                      {t('pricing.feature', 'الميزة')}
                    </th>
                    {PRICING_PLANS.map((plan) => (
                      <th key={plan.id} className="px-6 py-4 text-center text-sm font-medium text-gray-900 dark:text-white">
                        {isRTL ? plan.nameAr : plan.nameEn}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                  {PRICING_PLANS[0].features.map((_, featureIndex) => (
                    <tr key={featureIndex}>
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                        {isRTL
                          ? PRICING_PLANS[0].features[featureIndex].keyAr
                          : PRICING_PLANS[0].features[featureIndex].keyEn
                        }
                      </td>
                      {PRICING_PLANS.map((plan) => (
                        <td key={plan.id} className="px-6 py-4 text-center">
                          {plan.features[featureIndex].included ? (
                            <CheckIcon className="w-5 h-5 text-emerald-500 mx-auto" />
                          ) : (
                            <XMarkIcon className="w-5 h-5 text-gray-400 mx-auto" />
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mt-20"
        >
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white text-center mb-12">
            {t('pricing.faq', 'الأسئلة الشائعة حول الأسعار')}
          </h3>

          <div className="grid md:grid-cols-2 gap-8">
            {[
              {
                questionAr: 'هل يمكنني تغيير خطة الاشتراك؟',
                questionEn: 'Can I change my subscription plan?',
                answerAr: 'نعم، يمكنك ترقية أو تخفيض خطتك في أي وقت من لوحة التحكم.',
                answerEn: 'Yes, you can upgrade or downgrade your plan anytime from the dashboard.'
              },
              {
                questionAr: 'هل هناك رسوم إضافية؟',
                questionEn: 'Are there any additional fees?',
                answerAr: 'لا توجد رسوم خفية. جميع الميزات المذكورة مشمولة في السعر.',
                answerEn: 'No hidden fees. All listed features are included in the price.'
              },
              {
                questionAr: 'ماذا يحدث إذا تجاوزت عدد التحليلات؟',
                questionEn: 'What happens if I exceed my analysis limit?',
                answerAr: 'يمكنك شراء تحليلات إضافية أو ترقية خطتك.',
                answerEn: 'You can purchase additional analyses or upgrade your plan.'
              },
              {
                questionAr: 'هل يمكنني إلغاء الاشتراك؟',
                questionEn: 'Can I cancel my subscription?',
                answerAr: 'نعم، يمكنك إلغاء الاشتراك في أي وقت بدون رسوم إلغاء.',
                answerEn: 'Yes, you can cancel anytime without cancellation fees.'
              }
            ].map((faq, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
                  {isRTL ? faq.questionAr : faq.questionEn}
                </h4>
                <p className="text-gray-600 dark:text-gray-400">
                  {isRTL ? faq.answerAr : faq.answerEn}
                </p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Final CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-center mt-20"
        >
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-12 text-white">
            <h3 className="text-3xl font-bold mb-4">
              {t('pricing.readyToStart', 'جاهز للبدء؟')}
            </h3>
            <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
              {t('pricing.startToday', 'ابدأ اليوم وأحصل على تحليل مالي احترافي في ثوانٍ')}
            </p>
            <Link
              to="/auth"
              className="inline-flex items-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-xl hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              {t('pricing.signUpNow', 'اشترك الآن')}
              <ArrowRightIcon className={`w-5 h-5 ${isRTL ? 'mr-2' : 'ml-2'}`} />
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PricingPage;