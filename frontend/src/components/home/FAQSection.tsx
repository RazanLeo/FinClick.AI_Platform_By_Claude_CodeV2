import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDownIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

const FAQSection: React.FC = () => {
  const { t } = useTranslation();
  const [openItems, setOpenItems] = useState<number[]>([0]);

  const toggleItem = (index: number) => {
    setOpenItems(prev =>
      prev.includes(index)
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  const faqs = [
    {
      question: 'ما هو FinClick.AI وكيف يعمل؟',
      answer: 'FinClick.AI هو أول منصة ذكاء اصطناعي متكاملة للتحليل المالي في المنطقة العربية. يستخدم 23 وكيل ذكاء اصطناعي مستقل يعملون بالتوازي لتحليل بياناتك المالية وتقديم 180 نوع تحليل مختلف في أقل من 30 ثانية. كل ما عليك فعله هو رفع القوائم المالية، اختيار القطاع والنشاط، والحصول على تحليل شامل مع تقارير احترافية.'
    },
    {
      question: 'ما هي أنواع الملفات المدعومة للرفع؟',
      answer: 'ندعم جميع صيغ الملفات المالية الشائعة بما في ذلك PDF، Excel (XLS, XLSX)، Word (DOC, DOCX)، PowerPoint (PPT, PPTX)، CSV، والصور (JPG, PNG, TIFF). كما نوفر تقنية OCR متقدمة لاستخراج البيانات من المستندات الممسوحة ضوئياً. يمكنك رفع حتى 10 ملفات في المرة الواحدة.'
    },
    {
      question: 'كم من الوقت يستغرق الحصول على نتائج التحليل؟',
      answer: 'معظم التحليلات تكتمل في أقل من 30 ثانية. الوقت يعتمد على حجم البيانات وتعقيد التحليل المطلوب. التحليلات الأساسية تستغرق 10-15 ثانية، بينما التحليلات المتقدمة مع النمذجة المالية قد تستغرق حتى دقيقتين. ستحصل على تحديثات فورية حول تقدم التحليل.'
    },
    {
      question: 'هل البيانات آمنة ومحمية؟',
      answer: 'أمان بياناتك أولويتنا القصوى. نستخدم تشفير SSL/TLS لجميع عمليات النقل، وتشفير AES-256 لتخزين البيانات. جميع الخوادم محمية بجدران حماية متقدمة ونظام مراقبة على مدار الساعة. نلتزم بمعايير GDPR وSOC 2 Type II. يتم حذف ملفاتك تلقائياً بعد 30 يوماً ما لم تطلب الاحتفاظ بها.'
    },
    {
      question: 'هل يمكنني مقارنة شركتي مع المنافسين؟',
      answer: 'نعم، نوفر مقارنات معيارية شاملة على 9 مستويات جغرافية: المحلي، الإقليمي، الخليجي، العربي، الشرق أوسطي، الآسيوي، الأفريقي، الأوروبي، والعالمي. كما نقدم مقارنات حسب حجم الشركة ونوع النشاط. قاعدة بياناتنا تحتوي على أكثر من 50,000 شركة من المنطقة العربية و500,000 شركة عالمياً.'
    },
    {
      question: 'ما هي صيغ التقارير المتاحة؟',
      answer: 'نوفر تقارير بصيغ متعددة حسب احتياجاتك: PDF للقراءة والعرض، Word للتحرير والتخصيص، Excel للتحليل التفصيلي، وPowerPoint للعروض التقديمية. جميع التقارير متاحة باللغتين العربية والإنجليزية مع دعم كامل للاتجاه من اليمين إلى اليسار. كما نوفر رسوماً بيانية تفاعلية يمكن تصديرها كصور عالية الدقة.'
    },
    {
      question: 'هل تدعمون التكامل مع الأنظمة الأخرى؟',
      answer: 'نعم، نوفر API شامل للتكامل مع أنظمة ERP مثل SAP، Oracle، وQuickBooks. كما ندعم التكامل مع منصات المحاسبة السحابية مثل Xero وZoho Books. للعملاء المؤسسيين، نقدم تكامل مخصص مع أنظمة إدارة البيانات والذكاء التجاري. فريقنا الفني يساعد في إعداد التكامل المطلوب.'
    },
    {
      question: 'ما هو الدعم الفني المتاح؟',
      answer: 'نقدم دعم فني متعدد المستويات: دعم عبر البريد الإلكتروني لجميع الخطط، دعم المحادثة المباشرة للخطة الاحترافية، ودعم هاتفي مخصص للعملاء المؤسسيين. كما نوفر قاعدة معرفية شاملة، فيديوهات تعليمية، وندوات تدريبية شهرية. أوقات الاستجابة: 24 ساعة للخطة المجانية، 4 ساعات للاحترافية، وساعة واحدة للمؤسسية.'
    },
    {
      question: 'هل يمكنني الحصول على تجربة مجانية؟',
      answer: 'بالطبع! نقدم خطة مجانية دائمة تتضمن 3 تحليلات شهرياً و50 نوع تحليل أساسي. كما نوفر تجربة مجانية لمدة 14 يوم للخطة الاحترافية مع الوصول الكامل لجميع الـ180 تحليل. لا نطلب بيانات بطاقة ائتمانية للتجربة المجانية. يمكنك الترقية أو الإلغاء في أي وقت دون التزامات.'
    },
    {
      question: 'كيف يختلف FinClick.AI عن الحلول الأخرى؟',
      answer: 'FinClick.AI يتميز بعدة جوانب فريدة: هو الوحيد المصمم خصيصاً للسوق العربي مع دعم كامل للعربية، يوفر أشمل مجموعة تحليلات (180 نوع)، يستخدم 23 وكيل ذكاء اصطناعي للتحليل المتوازي، ينتج نتائج في ثوانٍ بدلاً من ساعات، ويقدم مقارنات معيارية شاملة للمنطقة. كما أن أسعارنا تنافسية جداً مقارنة بالحلول العالمية.'
    }
  ];

  return (
    <section className="py-20 bg-gray-50 dark:bg-gray-800">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center space-x-2 rtl:space-x-reverse bg-primary-100 dark:bg-primary-900/20 text-primary-800 dark:text-primary-200 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <QuestionMarkCircleIcon className="w-4 h-4" />
            <span>الأسئلة الشائعة</span>
          </div>

          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            إجابات لأسئلتك
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            كل ما تريد معرفته عن FinClick.AI وكيفية الاستفادة القصوى من المنصة
          </p>
        </motion.div>

        {/* FAQ Items */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="space-y-4"
        >
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              className="bg-white dark:bg-gray-900 rounded-xl shadow-soft border border-gray-100 dark:border-gray-700 overflow-hidden"
            >
              <button
                onClick={() => toggleItem(index)}
                className="w-full px-6 py-5 text-right flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200"
              >
                <span className="text-lg font-semibold text-gray-900 dark:text-white pr-4">
                  {faq.question}
                </span>
                <motion.div
                  animate={{ rotate: openItems.includes(index) ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex-shrink-0"
                >
                  <ChevronDownIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                </motion.div>
              </button>

              <AnimatePresence>
                {openItems.includes(index) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="px-6 pb-5">
                      <div className="pt-2 border-t border-gray-100 dark:border-gray-700">
                        <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                          {faq.answer}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </motion.div>

        {/* Contact CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="text-center mt-16"
        >
          <div className="bg-white dark:bg-gray-900 rounded-xl p-8 shadow-soft border border-gray-100 dark:border-gray-700">
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              لم تجد إجابة لسؤالك؟
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-2xl mx-auto">
              فريق الدعم الفني لدينا جاهز لمساعدتك. تواصل معنا في أي وقت وسنرد عليك خلال ساعات قليلة
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn btn-primary"
              >
                تواصل مع الدعم الفني
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn btn-outline"
              >
                زيارة مركز المساعدة
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default FAQSection;