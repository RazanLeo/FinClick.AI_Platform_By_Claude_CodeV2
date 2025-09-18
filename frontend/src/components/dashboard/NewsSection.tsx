import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  NewspaperIcon,
  GlobeAltIcon,
  CalendarIcon,
  ArrowTopRightOnSquareIcon,
  TrendingUpIcon,
  TrendingDownIcon
} from '@heroicons/react/24/outline';

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  category: 'market' | 'banking' | 'energy' | 'technology' | 'economy';
  impact: 'positive' | 'negative' | 'neutral';
  readTime: number;
  url: string;
  isArabic: boolean;
}

const NewsSection: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Mock news data - في التطبيق الحقيقي، ستأتي من News API
  const newsItems: NewsItem[] = [
    {
      id: '1',
      title: i18n.language === 'ar'
        ? 'أرامكو تسجل أرباحاً قياسية في الربع الثالث'
        : 'Saudi Aramco Reports Record Q3 Profits',
      summary: i18n.language === 'ar'
        ? 'حققت أرامكو السعودية أرباحاً صافية قدرها 32.6 مليار ريال في الربع الثالث، محققة نمواً بنسبة 15% مقارنة بالربع السابق'
        : 'Saudi Aramco achieved net profits of SAR 32.6 billion in Q3, representing 15% growth compared to previous quarter',
      source: 'تداول السعودية',
      publishedAt: '2024-01-15T08:30:00Z',
      category: 'energy',
      impact: 'positive',
      readTime: 3,
      url: '#',
      isArabic: i18n.language === 'ar'
    },
    {
      id: '2',
      title: i18n.language === 'ar'
        ? 'البنك المركزي يرفع أسعار الفائدة بـ 25 نقطة أساس'
        : 'Central Bank Raises Interest Rates by 25 Basis Points',
      summary: i18n.language === 'ar'
        ? 'قرر البنك المركزي السعودي رفع أسعار الفائدة الأساسية لتصل إلى 5.75% للحد من التضخم ودعم الاستقرار الاقتصادي'
        : 'Saudi Central Bank decided to raise the base interest rate to 5.75% to curb inflation and support economic stability',
      source: 'البنك المركزي السعودي',
      publishedAt: '2024-01-14T14:00:00Z',
      category: 'banking',
      impact: 'neutral',
      readTime: 4,
      url: '#',
      isArabic: i18n.language === 'ar'
    },
    {
      id: '3',
      title: i18n.language === 'ar'
        ? 'تراجع أسعار النفط عالمياً بنسبة 3%'
        : 'Global Oil Prices Drop 3%',
      summary: i18n.language === 'ar'
        ? 'شهدت أسعار النفط الخام تراجعاً ملحوظاً في التداولات الآسيوية بسبب مخاوف من تباطؤ النمو الاقتصادي العالمي'
        : 'Crude oil prices saw notable decline in Asian trading due to concerns over global economic growth slowdown',
      source: 'بلومبرغ',
      publishedAt: '2024-01-14T06:15:00Z',
      category: 'energy',
      impact: 'negative',
      readTime: 2,
      url: '#',
      isArabic: i18n.language === 'ar'
    },
    {
      id: '4',
      title: i18n.language === 'ar'
        ? 'نيوم تطلق مشروع تقنيات الذكاء الاصطناعي'
        : 'NEOM Launches AI Technology Project',
      summary: i18n.language === 'ar'
        ? 'أعلنت نيوم عن إطلاق مشروع رائد في تقنيات الذكاء الاصطناعي باستثمارات تقدر بـ 5 مليارات ريال لتطوير المدينة الذكية'
        : 'NEOM announced launch of pioneering AI technology project with SAR 5 billion investment to develop the smart city',
      source: 'نيوم',
      publishedAt: '2024-01-13T16:45:00Z',
      category: 'technology',
      impact: 'positive',
      readTime: 5,
      url: '#',
      isArabic: i18n.language === 'ar'
    },
    {
      id: '5',
      title: i18n.language === 'ar'
        ? 'مؤشر تداول يغلق على ارتفاع 2.1%'
        : 'Tadawul Index Closes Up 2.1%',
      summary: i18n.language === 'ar'
        ? 'أغلق المؤشر العام للسوق السعودي على ارتفاع قدره 2.1% مدعوماً بصعود أسهم البنوك والطاقة'
        : 'Saudi market general index closed up 2.1% supported by banking and energy sector gains',
      source: 'تداول',
      publishedAt: '2024-01-13T15:00:00Z',
      category: 'market',
      impact: 'positive',
      readTime: 2,
      url: '#',
      isArabic: i18n.language === 'ar'
    }
  ];

  const categories = [
    { id: 'all', label: t('news.categories.all', 'الكل'), icon: '📰' },
    { id: 'market', label: t('news.categories.market', 'السوق'), icon: '📈' },
    { id: 'banking', label: t('news.categories.banking', 'البنوك'), icon: '🏦' },
    { id: 'energy', label: t('news.categories.energy', 'الطاقة'), icon: '⛽' },
    { id: 'technology', label: t('news.categories.technology', 'التقنية'), icon: '💻' },
    { id: 'economy', label: t('news.categories.economy', 'الاقتصاد'), icon: '📊' }
  ];

  const filteredNews = selectedCategory === 'all'
    ? newsItems
    : newsItems.filter(item => item.category === selectedCategory);

  const getImpactIcon = (impact: string) => {
    switch (impact) {
      case 'positive':
        return <TrendingUpIcon className="w-4 h-4 text-green-500" />;
      case 'negative':
        return <TrendingDownIcon className="w-4 h-4 text-red-500" />;
      default:
        return <div className="w-4 h-4 rounded-full bg-gray-400" />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'positive':
        return 'border-l-green-500 bg-green-50 dark:bg-green-900/20';
      case 'negative':
        return 'border-l-red-500 bg-red-50 dark:bg-red-900/20';
      default:
        return 'border-l-gray-500 bg-gray-50 dark:bg-gray-700';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) {
      return t('time.justNow', 'الآن');
    } else if (diffInHours < 24) {
      return t('time.hoursAgo', `منذ ${diffInHours} ساعة`);
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return t('time.daysAgo', `منذ ${diffInDays} يوم`);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3 rtl:space-x-reverse">
          <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
            <NewspaperIcon className="w-6 h-6 text-orange-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {t('dashboard.marketNews', 'أخبار السوق')}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('dashboard.latestFinancialNews', 'آخر الأخبار المالية والاقتصادية')}
            </p>
          </div>
        </div>

        <button className="text-sm text-orange-600 hover:text-orange-700 font-medium flex items-center space-x-1 rtl:space-x-reverse">
          <span>{t('common.viewAll', 'عرض الكل')}</span>
          <ArrowTopRightOnSquareIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Category Filter */}
      <div className="flex space-x-2 rtl:space-x-reverse mb-6 overflow-x-auto pb-2">
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`
              flex items-center space-x-2 rtl:space-x-reverse px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 whitespace-nowrap
              ${selectedCategory === category.id
                ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700'
              }
            `}
          >
            <span className="text-base">{category.icon}</span>
            <span>{category.label}</span>
          </button>
        ))}
      </div>

      {/* News List */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {filteredNews.map((news, index) => (
          <motion.div
            key={news.id}
            initial={{ opacity: 0, x: isRTL ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`
              group p-4 border-l-4 ${getImpactColor(news.impact)} rounded-lg hover:shadow-md transition-all duration-200 cursor-pointer
            `}
          >
            <div className="flex items-start justify-between space-x-3 rtl:space-x-reverse">
              <div className="flex-1 min-w-0">
                {/* Title and Impact */}
                <div className="flex items-start space-x-2 rtl:space-x-reverse mb-2">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2 group-hover:text-orange-600 transition-colors">
                    {news.title}
                  </h4>
                  <div className="flex-shrink-0 mt-1">
                    {getImpactIcon(news.impact)}
                  </div>
                </div>

                {/* Summary */}
                <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
                  {news.summary}
                </p>

                {/* Meta information */}
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  <div className="flex items-center space-x-4 rtl:space-x-reverse">
                    <div className="flex items-center space-x-1 rtl:space-x-reverse">
                      <GlobeAltIcon className="w-3 h-3" />
                      <span>{news.source}</span>
                    </div>
                    <div className="flex items-center space-x-1 rtl:space-x-reverse">
                      <CalendarIcon className="w-3 h-3" />
                      <span>{formatDate(news.publishedAt)}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 rtl:space-x-reverse">
                    <span>{news.readTime} {t('time.minRead', 'د قراءة')}</span>
                    <ArrowTopRightOnSquareIcon className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty state */}
      {filteredNews.length === 0 && (
        <div className="text-center py-8">
          <NewspaperIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            {t('news.noNews', 'لا توجد أخبار في هذه الفئة')}
          </h4>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            {t('news.tryDifferentCategory', 'جرب فئة أخرى أو عد لاحقاً')}
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center space-x-2 rtl:space-x-reverse">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>{t('news.liveUpdates', 'تحديثات مباشرة')}</span>
          </div>
          <span>{t('news.lastUpdate', 'آخر تحديث:')} {formatDate(newsItems[0]?.publishedAt || new Date().toISOString())}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default NewsSection;