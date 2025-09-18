import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  MagnifyingGlassIcon,
  ChevronDownIcon,
  CheckIcon,
  XMarkIcon,
  InformationCircleIcon,
  GlobeAltIcon,
  BuildingOfficeIcon,
  DocumentChartBarIcon,
  ChartBarIcon,
  CogIcon,
  PlayIcon,
} from '@heroicons/react/24/outline';

import { useAnalysis } from '../../contexts/AnalysisContext';
import {
  sectors,
  entityTypes,
  comparisonTypes,
  analysisTypes,
  reportFormats,
  getSectorById,
  getActivitiesBySector,
} from '../../data/sectors';

const AnalysisOptionsForm: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { options, updateOptions, files, startAnalysis, isAnalyzing } = useAnalysis();
  const isRTL = i18n.language === 'ar';

  const [searchTerm, setSearchTerm] = useState('');
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  // Filter sectors based on search
  const filteredSectors = useMemo(() => {
    if (!searchTerm) return sectors;
    return sectors.filter(sector =>
      sector.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      sector.nameEn.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm]);

  // Get activities for selected sector
  const availableActivities = useMemo(() => {
    return options.sector ? getActivitiesBySector(options.sector) : [];
  }, [options.sector]);

  const handleDropdownToggle = (dropdownName: string) => {
    setOpenDropdown(openDropdown === dropdownName ? null : dropdownName);
  };

  const handleSectorSelect = (sectorId: string) => {
    updateOptions({
      sector: sectorId,
      activity: '' // Reset activity when sector changes
    });
    setOpenDropdown(null);
  };

  const handleOptionSelect = (key: string, value: string) => {
    updateOptions({ [key]: value });
    setOpenDropdown(null);
  };

  const handleAnalysisTypeToggle = (typeId: string) => {
    const currentTypes = options.analysisTypes;
    const updatedTypes = currentTypes.includes(typeId)
      ? currentTypes.filter(id => id !== typeId)
      : [...currentTypes, typeId];
    updateOptions({ analysisTypes: updatedTypes });
  };

  const handleReportFormatToggle = (formatId: string) => {
    const currentFormats = options.reportFormats;
    const updatedFormats = currentFormats.includes(formatId)
      ? currentFormats.filter(id => id !== formatId)
      : [...currentFormats, formatId];
    updateOptions({ reportFormats: updatedFormats });
  };

  const isFormValid = () => {
    return (
      files.length > 0 &&
      options.sector &&
      options.activity &&
      options.entityType &&
      options.analysisTypes.length > 0 &&
      options.reportFormats.length > 0
    );
  };

  const selectedSector = getSectorById(options.sector);
  const selectedActivity = availableActivities.find(a => a.id === options.activity);
  const selectedEntityType = entityTypes.find(e => e.id === options.entityType);
  const selectedComparison = comparisonTypes.find(c => c.id === options.comparisonType);

  return (
    <div className="space-y-6">
      {/* Language Selection */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3 rtl:space-x-reverse mb-4">
          <GlobeAltIcon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {t('dashboard.sections.options.language', 'لغة التقرير')}
          </h3>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => updateOptions({ language: 'ar' })}
            className={`p-4 rounded-lg border-2 transition-all duration-200 ${
              options.language === 'ar'
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-gray-600 hover:border-primary-300 dark:hover:border-primary-600'
            }`}
          >
            <div className="text-center">
              <span className="text-2xl block mb-2">🇸🇦</span>
              <span className="font-medium">العربية</span>
            </div>
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => updateOptions({ language: 'en' })}
            className={`p-4 rounded-lg border-2 transition-all duration-200 ${
              options.language === 'en'
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                : 'border-gray-200 dark:border-gray-600 hover:border-primary-300 dark:hover:border-primary-600'
            }`}
          >
            <div className="text-center">
              <span className="text-2xl block mb-2">🇺🇸</span>
              <span className="font-medium">English</span>
            </div>
          </motion.button>
        </div>
      </div>

      {/* Sector and Activity Selection */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3 rtl:space-x-reverse mb-4">
          <BuildingOfficeIcon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            القطاع والنشاط
          </h3>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          {/* Sector Dropdown */}
          <div className="relative">
            <label className="label required">
              {t('dashboard.sections.options.sector', 'القطاع')}
            </label>
            <div className="relative">
              <button
                onClick={() => handleDropdownToggle('sector')}
                className="select w-full text-right flex items-center justify-between"
              >
                <span className={selectedSector ? 'text-gray-900 dark:text-white' : 'text-gray-500'}>
                  {selectedSector ? selectedSector.name : 'اختر القطاع'}
                </span>
                <ChevronDownIcon className={`w-4 h-4 text-gray-400 transition-transform ${
                  openDropdown === 'sector' ? 'rotate-180' : ''
                }`} />
              </button>

              {openDropdown === 'sector' && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto"
                >
                  {/* Search */}
                  <div className="p-3 border-b border-gray-200 dark:border-gray-600">
                    <div className="relative">
                      <MagnifyingGlassIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        placeholder="ابحث في القطاعات..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pr-10 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                  </div>

                  {/* Sectors List */}
                  <div className="py-1">
                    {filteredSectors.map((sector) => (
                      <button
                        key={sector.id}
                        onClick={() => handleSectorSelect(sector.id)}
                        className={`w-full text-right px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                          options.sector === sector.id
                            ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'text-gray-900 dark:text-white'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm">{sector.name}</span>
                          {options.sector === sector.id && (
                            <CheckIcon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                          )}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {sector.nameEn}
                        </div>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
          </div>

          {/* Activity Dropdown */}
          <div className="relative">
            <label className="label required">
              {t('dashboard.sections.options.activity', 'النشاط')}
            </label>
            <div className="relative">
              <button
                onClick={() => handleDropdownToggle('activity')}
                disabled={!options.sector}
                className={`select w-full text-right flex items-center justify-between ${
                  !options.sector ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <span className={selectedActivity ? 'text-gray-900 dark:text-white' : 'text-gray-500'}>
                  {selectedActivity ? selectedActivity.name : 'اختر النشاط'}
                </span>
                <ChevronDownIcon className={`w-4 h-4 text-gray-400 transition-transform ${
                  openDropdown === 'activity' ? 'rotate-180' : ''
                }`} />
              </button>

              {openDropdown === 'activity' && options.sector && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto"
                >
                  <div className="py-1">
                    {availableActivities.map((activity) => (
                      <button
                        key={activity.id}
                        onClick={() => handleOptionSelect('activity', activity.id)}
                        className={`w-full text-right px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                          options.activity === activity.id
                            ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                            : 'text-gray-900 dark:text-white'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm">{activity.name}</span>
                          {options.activity === activity.id && (
                            <CheckIcon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                          )}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {activity.nameEn}
                        </div>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Entity Type and Comparison */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Entity Type */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3 rtl:space-x-reverse mb-4">
            <CogIcon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {t('dashboard.sections.options.entity', 'نوع الكيان القانوني')}
            </h3>
          </div>
          <div className="relative">
            <button
              onClick={() => handleDropdownToggle('entityType')}
              className="select w-full text-right flex items-center justify-between"
            >
              <span className={selectedEntityType ? 'text-gray-900 dark:text-white' : 'text-gray-500'}>
                {selectedEntityType ? selectedEntityType.name : 'اختر نوع الكيان'}
              </span>
              <ChevronDownIcon className={`w-4 h-4 text-gray-400 transition-transform ${
                openDropdown === 'entityType' ? 'rotate-180' : ''
              }`} />
            </button>

            {openDropdown === 'entityType' && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto"
              >
                <div className="py-1">
                  {entityTypes.map((entity) => (
                    <button
                      key={entity.id}
                      onClick={() => handleOptionSelect('entityType', entity.id)}
                      className={`w-full text-right px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                        options.entityType === entity.id
                          ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                          : 'text-gray-900 dark:text-white'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm">{entity.name}</span>
                        {options.entityType === entity.id && (
                          <CheckIcon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                        )}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {entity.nameEn}
                      </div>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Comparison Type */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3 rtl:space-x-reverse mb-4">
            <ChartBarIcon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {t('dashboard.sections.options.comparison', 'نوع المقارنة')}
            </h3>
          </div>
          <div className="relative">
            <button
              onClick={() => handleDropdownToggle('comparisonType')}
              className="select w-full text-right flex items-center justify-between"
            >
              <span className={selectedComparison ? 'text-gray-900 dark:text-white' : 'text-gray-500'}>
                {selectedComparison ? selectedComparison.name : 'اختر نوع المقارنة'}
              </span>
              <ChevronDownIcon className={`w-4 h-4 text-gray-400 transition-transform ${
                openDropdown === 'comparisonType' ? 'rotate-180' : ''
              }`} />
            </button>

            {openDropdown === 'comparisonType' && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto"
              >
                <div className="py-1">
                  {comparisonTypes.map((comparison) => (
                    <button
                      key={comparison.id}
                      onClick={() => handleOptionSelect('comparisonType', comparison.id)}
                      className={`w-full text-right px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                        options.comparisonType === comparison.id
                          ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300'
                          : 'text-gray-900 dark:text-white'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm">{comparison.name}</span>
                        {options.comparisonType === comparison.id && (
                          <CheckIcon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                        )}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {comparison.nameEn}
                      </div>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* Analysis Types */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3 rtl:space-x-reverse mb-4">
          <DocumentChartBarIcon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {t('dashboard.sections.options.analysisType', 'نوع التحليل')}
          </h3>
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
            <InformationCircleIcon className="w-4 h-4 mr-1" />
            <span>يمكن اختيار أكثر من نوع</span>
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-3">
          {analysisTypes.map((type) => (
            <motion.label
              key={type.id}
              whileHover={{ scale: 1.02 }}
              className="flex items-center p-4 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-200"
            >
              <input
                type="checkbox"
                checked={options.analysisTypes.includes(type.id)}
                onChange={() => handleAnalysisTypeToggle(type.id)}
                className="checkbox mr-3"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">
                  {type.name}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {type.nameEn}
                </div>
              </div>
            </motion.label>
          ))}
        </div>
      </div>

      {/* Report Formats */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3 rtl:space-x-reverse mb-4">
          <DocumentChartBarIcon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {t('dashboard.sections.options.reportFormat', 'صيغة التقرير')}
          </h3>
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
            <InformationCircleIcon className="w-4 h-4 mr-1" />
            <span>يمكن اختيار أكثر من صيغة</span>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {reportFormats.map((format) => (
            <motion.label
              key={format.id}
              whileHover={{ scale: 1.02 }}
              className="flex items-center p-4 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer hover:border-primary-300 dark:hover:border-primary-600 transition-all duration-200"
            >
              <input
                type="checkbox"
                checked={options.reportFormats.includes(format.id)}
                onChange={() => handleReportFormatToggle(format.id)}
                className="checkbox mr-3"
              />
              <div className="flex-1 text-center">
                <div className="text-2xl mb-2">{format.icon}</div>
                <div className="font-medium text-gray-900 dark:text-white text-sm">
                  {format.name}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {format.nameEn}
                </div>
              </div>
            </motion.label>
          ))}
        </div>
      </div>

      {/* Action Button */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-soft border border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={startAnalysis}
            disabled={!isFormValid() || isAnalyzing}
            className={`w-full md:w-auto inline-flex items-center justify-center px-8 py-4 rounded-xl font-semibold transition-all duration-200 ${
              isFormValid() && !isAnalyzing
                ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-xl'
                : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-3" />
                <span>جارٍ التحليل...</span>
              </>
            ) : (
              <>
                <PlayIcon className={`w-5 h-5 ${isRTL ? 'ml-3' : 'mr-3'}`} />
                <span>{t('dashboard.sections.analysis.button', 'بدء التحليل')}</span>
              </>
            )}
          </motion.button>

          {!isFormValid() && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-3">
              يرجى إكمال جميع الحقول المطلوبة ورفع ملف واحد على الأقل
            </p>
          )}

          {isFormValid() && !isAnalyzing && (
            <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
              <p className="mb-2">✅ جاهز للتحليل!</p>
              <p>{t('dashboard.sections.analysis.estimated', 'الوقت المتوقع: 30 ثانية')}</p>
            </div>
          )}
        </div>
      </div>

      {/* Click outside handler */}
      {openDropdown && (
        <div
          className="fixed inset-0 z-10"
          onClick={() => setOpenDropdown(null)}
        />
      )}
    </div>
  );
};

export default AnalysisOptionsForm;