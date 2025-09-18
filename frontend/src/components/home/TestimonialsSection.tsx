import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { StarIcon, QuoteIcon } from '@heroicons/react/24/solid';

const TestimonialsSection: React.FC = () => {
  const { t } = useTranslation();

  const testimonials = [
    {
      id: 1,
      name: 'أحمد الشمري',
      position: 'المدير المالي',
      company: 'شركة الخليج للاستثمار',
      content: 'FinClick.AI غيرت طريقة عملنا في التحليل المالي. ما كان يستغرق أسابيع أصبح يتم في دقائق مع دقة عالية ونتائج شاملة. التقارير المولدة احترافية جداً ومناسبة للعرض على مجلس الإدارة مباشرة.',
      rating: 5,
      avatar: 'https://ui-avatars.com/api/?name=Ahmed+Al-Shamri&background=B48500&color=fff&size=64',
      industry: 'استثمار'
    },
    {
      id: 2,
      name: 'فاطمة العلي',
      position: 'محللة مالية أول',
      company: 'بنك الإمارات الوطني',
      content: 'المنصة توفر تحليلات متقدمة لم نكن نتمكن من إجرائها سابقاً. خاصة تحليلات المخاطر الكمية والنمذجة المالية. الدعم الفني ممتاز والواجهة سهلة الاستخدام.',
      rating: 5,
      avatar: 'https://ui-avatars.com/api/?name=Fatima+Al-Ali&background=B48500&color=fff&size=64',
      industry: 'مصرفي'
    },
    {
      id: 3,
      name: 'خالد المنصوري',
      position: 'رئيس قسم التحليل المالي',
      company: 'صندوق الاستثمارات العامة',
      content: 'دقة التحليلات المقدمة من FinClick.AI رائعة. استخدمنا المنصة لتحليل أكثر من 200 شركة في محفظتنا الاستثمارية. النتائج كانت متسقة ومفيدة جداً في اتخاذ قرارات الاستثمار.',
      rating: 5,
      avatar: 'https://ui-avatars.com/api/?name=Khalid+Al-Mansouri&background=B48500&color=fff&size=64',
      industry: 'صناديق استثمار'
    },
    {
      id: 4,
      name: 'مريم الزهراني',
      position: 'مديرة التخطيط المالي',
      company: 'شركة أرامكو السعودية',
      content: 'سهولة الاستخدام والنتائج السريعة هما أبرز ما يميز FinClick.AI. نحن نستخدم المنصة للتحليل الشهري لأداء الشركة وللمقارنات المعيارية مع الشركات المماثلة في الصناعة.',
      rating: 5,
      avatar: 'https://ui-avatars.com/api/?name=Mariam+Al-Zahrani&background=B48500&color=fff&size=64',
      industry: 'بترول وغاز'
    },
    {
      id: 5,
      name: 'عبدالله الدوسري',
      position: 'مدير الاستثمار',
      company: 'مجموعة الراجحي المالية',
      content: 'التحليلات المتوافقة مع الشريعة الإسلامية والدعم للمعايير المحاسبية المحلية جعل FinClick.AI الخيار الأمثل لنا. التقارير مفصلة ودقيقة وتساعدنا في اتخاذ قرارات استثمارية مدروسة.',
      rating: 5,
      avatar: 'https://ui-avatars.com/api/?name=Abdullah+Al-Dosari&background=B48500&color=fff&size=64',
      industry: 'خدمات مالية'
    },
    {
      id: 6,
      name: 'نورا القحطاني',
      position: 'محللة أسواق مالية',
      company: 'شركة الأهلي كابيتال',
      content: 'إمكانية المقارنة مع الشركات المماثلة ومتوسطات الصناعة على مستوى المنطقة ميزة لا تقدر بثمن. هذا يساعدنا كثيراً في إعداد التقارير البحثية وتوصيات الاستثمار.',
      rating: 5,
      avatar: 'https://ui-avatars.com/api/?name=Nora+Al-Qahtani&background=B48500&color=fff&size=64',
      industry: 'أسواق مالية'
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
    <section className="py-20 bg-gray-50 dark:bg-gray-800">
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
            {t('testimonials.title', 'آراء العملاء')}
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            {t('testimonials.subtitle', 'ماذا يقول عملاؤنا عن FinClick.AI')}
          </p>
        </motion.div>

        {/* Testimonials Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
        >
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.id}
              variants={itemVariants}
              className="group"
            >
              <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 shadow-soft hover:shadow-medium transition-all duration-300 border border-gray-100 dark:border-gray-700 hover:border-primary-200 dark:hover:border-primary-800 h-full flex flex-col">
                {/* Quote Icon */}
                <div className="flex justify-between items-start mb-4">
                  <QuoteIcon className="w-8 h-8 text-primary-500 opacity-60" />

                  {/* Rating */}
                  <div className="flex space-x-1 rtl:space-x-reverse">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <StarIcon key={i} className="w-4 h-4 text-yellow-400" />
                    ))}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1">
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-6 italic">
                    "{testimonial.content}"
                  </p>
                </div>

                {/* Author */}
                <div className="flex items-center space-x-4 rtl:space-x-reverse pt-4 border-t border-gray-100 dark:border-gray-700">
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full"
                  />
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 dark:text-white">
                      {testimonial.name}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {testimonial.position}
                    </p>
                    <p className="text-sm text-primary-600 dark:text-primary-400 font-medium">
                      {testimonial.company}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="inline-block px-2 py-1 bg-primary-100 dark:bg-primary-900/20 text-primary-800 dark:text-primary-200 text-xs rounded-full">
                      {testimonial.industry}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mt-16 bg-white dark:bg-gray-900 rounded-2xl p-8 shadow-soft border border-gray-100 dark:border-gray-700"
        >
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">98%</div>
              <p className="text-sm text-gray-600 dark:text-gray-400">معدل رضا العملاء</p>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">500+</div>
              <p className="text-sm text-gray-600 dark:text-gray-400">شركة تثق بنا</p>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">50K+</div>
              <p className="text-sm text-gray-600 dark:text-gray-400">تحليل مكتمل</p>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">15</div>
              <p className="text-sm text-gray-600 dark:text-gray-400">دولة في المنطقة</p>
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-center mt-12"
        >
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            انضم إلى العملاء الراضين
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-2xl mx-auto">
            اكتشف لماذا يثق المحللون الماليون والمستثمرون في المنطقة العربية في FinClick.AI
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn btn-primary btn-lg"
          >
            ابدأ تجربتك المجانية اليوم
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
};

export default TestimonialsSection;