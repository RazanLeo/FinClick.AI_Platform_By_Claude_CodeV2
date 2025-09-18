import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChatBubbleLeftRightIcon,
  XMarkIcon,
  PaperAirplaneIcon,
  SparklesIcon,
  QuestionMarkCircleIcon,
  LightBulbIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  isTyping?: boolean;
}

const ChatbotWidget: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Welcome message on first open
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const welcomeMessage: Message = {
        id: '1',
        type: 'bot',
        content: i18n.language === 'ar'
          ? 'مرحباً! أنا مساعدك الذكي في التحليل المالي. كيف يمكنني مساعدتك اليوم؟'
          : 'Hello! I\'m your smart financial analysis assistant. How can I help you today?',
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, messages.length, i18n.language]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen]);

  const quickQuestions = [
    {
      id: 'analysis_types',
      icon: ChartBarIcon,
      question: i18n.language === 'ar'
        ? 'ما هي أنواع التحليل المتاحة؟'
        : 'What analysis types are available?',
      response: i18n.language === 'ar'
        ? 'نوفر 180 نوع تحليل مالي مقسمة إلى 3 فئات رئيسية:\n\n📊 تحليل الأداء المالي (106 تحليلات)\n⚠️ تحليل المخاطر المالية (21 تحليلاً)\n📈 تحليل السوق والمقارنات (53 تحليلاً)\n\nكل تحليل يوفر معلومات تفصيلية ورؤى عملية لاتخاذ القرارات المالية المدروسة.'
        : 'We offer 180 financial analysis types divided into 3 main categories:\n\n📊 Financial Performance Analysis (106 analyses)\n⚠️ Financial Risk Analysis (21 analyses)\n📈 Market & Benchmark Analysis (53 analyses)\n\nEach analysis provides detailed insights and actionable recommendations for informed financial decisions.'
    },
    {
      id: 'file_upload',
      icon: QuestionMarkCircleIcon,
      question: i18n.language === 'ar'
        ? 'ما هي الملفات المطلوبة للتحليل؟'
        : 'What files are required for analysis?',
      response: i18n.language === 'ar'
        ? 'يمكنك رفع الملفات التالية:\n\n📋 القوائم المالية الكاملة (قائمة مركز مالي، قائمة دخل، قائمة تدفقات نقدية)\n⚖️ موازين مراجعة كاملة\n📊 موازنات تقديرية للسنة الحالية والقادمة\n📁 الصيغ المدعومة: PDF, Excel, Word, صور ممسوحة ضوئياً\n📏 حتى 10 ملفات بأحجام غير محدودة'
        : 'You can upload the following files:\n\n📋 Complete financial statements (balance sheet, income statement, cash flow)\n⚖️ Complete trial balances\n📊 Budget estimates for current and next year\n📁 Supported formats: PDF, Excel, Word, scanned images\n📏 Up to 10 files with unlimited sizes'
    },
    {
      id: 'pricing',
      icon: LightBulbIcon,
      question: i18n.language === 'ar'
        ? 'ما هي خطط الأسعار المتاحة؟'
        : 'What pricing plans are available?',
      response: i18n.language === 'ar'
        ? 'لدينا 4 خطط تناسب جميع الاحتياجات:\n\n🆓 مجاني: 5 تحليلات شهرياً\n⭐ أساسي: 29$ - 50 تحليل شهرياً\n🚀 متقدم: 99$ - 200 تحليل شهرياً\n💎 للمؤسسات: 299$ - تحليلات غير محدودة\n\nجميع الخطط تشمل تقارير احترافية وأدوات مالية مجانية!'
        : 'We have 4 plans to suit all needs:\n\n🆓 Free: 5 analyses per month\n⭐ Basic: $29 - 50 analyses per month\n🚀 Advanced: $99 - 200 analyses per month\n💎 Enterprise: $299 - unlimited analyses\n\nAll plans include professional reports and free financial tools!'
    }
  ];

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate bot response (في التطبيق الحقيقي، ستكون مكالمة API)
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: i18n.language === 'ar'
          ? 'شكراً لسؤالك! أعمل على تحليل استفسارك وسأقدم لك إجابة شاملة قريباً. هل تحتاج مساعدة في موضوع آخر؟'
          : 'Thank you for your question! I\'m analyzing your inquiry and will provide you with a comprehensive answer soon. Do you need help with anything else?',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 2000);
  };

  const handleQuickQuestion = (question: any) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question.question,
      timestamp: new Date()
    };

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'bot',
      content: question.response,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage, botMessage]);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString(i18n.language === 'ar' ? 'ar-SA' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      {/* Chat Widget Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 1 }}
        onClick={() => setIsOpen(true)}
        className={`
          fixed bottom-6 ${isRTL ? 'left-6' : 'right-6'} z-50
          w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 text-white
          rounded-full shadow-lg hover:shadow-xl transition-all duration-300
          flex items-center justify-center group hover:scale-110
          ${isOpen ? 'hidden' : 'flex'}
        `}
      >
        <ChatBubbleLeftRightIcon className="w-8 h-8" />

        {/* Notification badge */}
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
          <SparklesIcon className="w-4 h-4 text-white" />
        </div>

        {/* Tooltip */}
        <div className={`
          absolute bottom-full mb-2 ${isRTL ? 'right-0' : 'left-0'}
          bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap
          opacity-0 group-hover:opacity-100 transition-opacity duration-200
        `}>
          {t('chatbot.askMe', 'اسألني عن أي شيء!')}
        </div>
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            className={`
              fixed bottom-6 ${isRTL ? 'left-6' : 'right-6'} z-50
              w-96 h-[600px] bg-white dark:bg-gray-800 rounded-2xl shadow-2xl
              border border-gray-200 dark:border-gray-700 overflow-hidden
              flex flex-col
            `}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 flex items-center justify-between">
              <div className="flex items-center space-x-3 rtl:space-x-reverse">
                <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <SparklesIcon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold">
                    {t('chatbot.title', 'مساعد FinClick.AI')}
                  </h3>
                  <p className="text-xs opacity-90">
                    {t('chatbot.status', 'متصل - جاهز للمساعدة')}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`
                    max-w-[80%] p-3 rounded-2xl text-sm
                    ${message.type === 'user'
                      ? 'bg-blue-600 text-white ml-2'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white mr-2'
                    }
                  `}>
                    <p className="whitespace-pre-line">{message.content}</p>
                    <p className={`text-xs mt-1 opacity-60`}>
                      {formatTime(message.timestamp)}
                    </p>
                  </div>
                </motion.div>
              ))}

              {/* Typing indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-2xl mr-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Questions (show only if no messages yet) */}
            {messages.length <= 1 && (
              <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  {t('chatbot.quickQuestions', 'أسئلة سريعة:')}
                </p>
                <div className="space-y-2">
                  {quickQuestions.map((question) => {
                    const IconComponent = question.icon;
                    return (
                      <button
                        key={question.id}
                        onClick={() => handleQuickQuestion(question)}
                        className="w-full text-left p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors flex items-center space-x-3 rtl:space-x-reverse"
                      >
                        <IconComponent className="w-5 h-5 text-blue-600 flex-shrink-0" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {question.question}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex space-x-2 rtl:space-x-reverse">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder={t('chatbot.placeholder', 'اكتب رسالتك هنا...')}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  disabled={isTyping}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                  className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PaperAirplaneIcon className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatbotWidget;