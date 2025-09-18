import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  CalculatorIcon,
  CurrencyDollarIcon,
  ChartLineIcon,
  TrendingUpIcon,
  BanknotesIcon,
  ScaleIcon,
  PresentationChartLineIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

// Free Financial Tools as specified in the prompt
const FINANCIAL_TOOLS = [
  {
    id: 'roi_calculator',
    nameAr: 'حاسبة العائد على الاستثمار',
    nameEn: 'ROI Calculator',
    descriptionAr: 'احسب العائد على الاستثمار بدقة',
    descriptionEn: 'Calculate return on investment accurately',
    icon: TrendingUpIcon,
    color: 'blue'
  },
  {
    id: 'fair_value_calculator',
    nameAr: 'حاسبة السعر العادل للسهم',
    nameEn: 'Fair Value Calculator',
    descriptionAr: 'احسب السعر العادل للأسهم',
    descriptionEn: 'Calculate fair value of stocks',
    icon: ChartLineIcon,
    color: 'emerald'
  },
  {
    id: 'compound_interest',
    nameAr: 'حاسبة الفائدة المركبة',
    nameEn: 'Compound Interest Calculator',
    descriptionAr: 'احسب نمو الاستثمارات المركبة',
    descriptionEn: 'Calculate compound investment growth',
    icon: BanknotesIcon,
    color: 'purple'
  },
  {
    id: 'break_even',
    nameAr: 'حاسبة نقطة التعادل',
    nameEn: 'Break-Even Calculator',
    descriptionAr: 'احسب نقطة التعادل للمشاريع',
    descriptionEn: 'Calculate project break-even point',
    icon: ScaleIcon,
    color: 'orange'
  },
  {
    id: 'dcf_calculator',
    nameAr: 'حاسبة التدفقات النقدية المخصومة',
    nameEn: 'DCF Calculator',
    descriptionAr: 'تقييم الشركات بطريقة DCF',
    descriptionEn: 'Value companies using DCF method',
    icon: PresentationChartLineIcon,
    color: 'indigo'
  },
  {
    id: 'loan_calculator',
    nameAr: 'حاسبة القروض',
    nameEn: 'Loan Calculator',
    descriptionAr: 'احسب أقساط القروض والفوائد',
    descriptionEn: 'Calculate loan payments and interest',
    icon: CurrencyDollarIcon,
    color: 'red'
  }
];

const ToolsSection: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';
  const [selectedTool, setSelectedTool] = useState<string | null>(null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
    >
      <div className="flex items-center mb-6">
        <CalculatorIcon className="w-6 h-6 text-emerald-600 mr-3" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {t('tools.title', 'أدوات مالية مجانية')}
        </h3>
      </div>

      <div className="space-y-4">
        {FINANCIAL_TOOLS.map((tool, index) => (
          <motion.div
            key={tool.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`p-4 rounded-lg border-2 transition-all cursor-pointer ${
              selectedTool === tool.id
                ? `border-${tool.color}-500 bg-${tool.color}-50 dark:bg-${tool.color}-900/20`
                : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
            }`}
            onClick={() => setSelectedTool(selectedTool === tool.id ? null : tool.id)}
          >
            <div className="flex items-center">
              <div className={`w-10 h-10 bg-${tool.color}-100 dark:bg-${tool.color}-900/30 rounded-lg flex items-center justify-center mr-3`}>
                <tool.icon className={`w-5 h-5 text-${tool.color}-600 dark:text-${tool.color}-400`} />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                  {isRTL ? tool.nameAr : tool.nameEn}
                </h4>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {isRTL ? tool.descriptionAr : tool.descriptionEn}
                </p>
              </div>
            </div>

            {/* Tool Interface - Expanded when selected */}
            {selectedTool === tool.id && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600"
              >
                {tool.id === 'roi_calculator' && <ROICalculator />}
                {tool.id === 'fair_value_calculator' && <FairValueCalculator />}
                {tool.id === 'compound_interest' && <CompoundInterestCalculator />}
                {tool.id === 'break_even' && <BreakEvenCalculator />}
                {tool.id === 'dcf_calculator' && <DCFCalculator />}
                {tool.id === 'loan_calculator' && <LoanCalculator />}
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      <div className="mt-6 text-center">
        <button className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium">
          {t('tools.viewAll', 'عرض جميع الأدوات')} →
        </button>
      </div>
    </motion.div>
  );
};

// ROI Calculator Component
const ROICalculator: React.FC = () => {
  const { t } = useTranslation();
  const [initialInvestment, setInitialInvestment] = useState<number>(0);
  const [finalValue, setFinalValue] = useState<number>(0);
  const [roi, setROI] = useState<number>(0);

  const calculateROI = () => {
    if (initialInvestment > 0) {
      const roiValue = ((finalValue - initialInvestment) / initialInvestment) * 100;
      setROI(roiValue);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('roi.initialInvestment', 'الاستثمار الأولي')}
        </label>
        <input
          type="number"
          value={initialInvestment}
          onChange={(e) => setInitialInvestment(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('roi.finalValue', 'القيمة النهائية')}
        </label>
        <input
          type="number"
          value={finalValue}
          onChange={(e) => setFinalValue(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0"
        />
      </div>
      <button
        onClick={calculateROI}
        className="w-full bg-blue-600 text-white py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
      >
        {t('roi.calculate', 'احسب العائد')}
      </button>
      {roi !== 0 && (
        <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-md">
          <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
            {t('roi.result', 'العائد على الاستثمار')}: <span className="font-bold">{roi.toFixed(2)}%</span>
          </p>
        </div>
      )}
    </div>
  );
};

// Fair Value Calculator Component
const FairValueCalculator: React.FC = () => {
  const { t } = useTranslation();
  const [eps, setEps] = useState<number>(0);
  const [peRatio, setPeRatio] = useState<number>(0);
  const [fairValue, setFairValue] = useState<number>(0);

  const calculateFairValue = () => {
    const value = eps * peRatio;
    setFairValue(value);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('fairValue.eps', 'ربحية السهم (EPS)')}
        </label>
        <input
          type="number"
          step="0.01"
          value={eps}
          onChange={(e) => setEps(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0.00"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('fairValue.peRatio', 'نسبة السعر للأرباح (P/E)')}
        </label>
        <input
          type="number"
          step="0.1"
          value={peRatio}
          onChange={(e) => setPeRatio(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0.0"
        />
      </div>
      <button
        onClick={calculateFairValue}
        className="w-full bg-emerald-600 text-white py-2 rounded-md text-sm font-medium hover:bg-emerald-700 transition-colors"
      >
        {t('fairValue.calculate', 'احسب السعر العادل')}
      </button>
      {fairValue > 0 && (
        <div className="bg-emerald-50 dark:bg-emerald-900/20 p-3 rounded-md">
          <p className="text-sm font-medium text-emerald-900 dark:text-emerald-100">
            {t('fairValue.result', 'السعر العادل')}: <span className="font-bold">${fairValue.toFixed(2)}</span>
          </p>
        </div>
      )}
    </div>
  );
};

// Compound Interest Calculator Component
const CompoundInterestCalculator: React.FC = () => {
  const { t } = useTranslation();
  const [principal, setPrincipal] = useState<number>(0);
  const [rate, setRate] = useState<number>(0);
  const [time, setTime] = useState<number>(0);
  const [compoundFrequency, setCompoundFrequency] = useState<number>(12);
  const [futureValue, setFutureValue] = useState<number>(0);

  const calculateCompoundInterest = () => {
    const fv = principal * Math.pow(1 + (rate / 100) / compoundFrequency, compoundFrequency * time);
    setFutureValue(fv);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('compound.principal', 'المبلغ الأساسي')}
        </label>
        <input
          type="number"
          value={principal}
          onChange={(e) => setPrincipal(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('compound.rate', 'معدل الفائدة السنوي (%)')}
        </label>
        <input
          type="number"
          step="0.1"
          value={rate}
          onChange={(e) => setRate(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0.0"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('compound.time', 'المدة بالسنوات')}
        </label>
        <input
          type="number"
          value={time}
          onChange={(e) => setTime(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0"
        />
      </div>
      <button
        onClick={calculateCompoundInterest}
        className="w-full bg-purple-600 text-white py-2 rounded-md text-sm font-medium hover:bg-purple-700 transition-colors"
      >
        {t('compound.calculate', 'احسب القيمة المستقبلية')}
      </button>
      {futureValue > 0 && (
        <div className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-md">
          <p className="text-sm font-medium text-purple-900 dark:text-purple-100">
            {t('compound.result', 'القيمة المستقبلية')}: <span className="font-bold">${futureValue.toFixed(2)}</span>
          </p>
          <p className="text-xs text-purple-700 dark:text-purple-300 mt-1">
            {t('compound.interest', 'الفائدة المكتسبة')}: ${(futureValue - principal).toFixed(2)}
          </p>
        </div>
      )}
    </div>
  );
};

// Break Even Calculator Component
const BreakEvenCalculator: React.FC = () => {
  const { t } = useTranslation();
  const [fixedCosts, setFixedCosts] = useState<number>(0);
  const [variableCostPerUnit, setVariableCostPerUnit] = useState<number>(0);
  const [pricePerUnit, setPricePerUnit] = useState<number>(0);
  const [breakEvenPoint, setBreakEvenPoint] = useState<number>(0);

  const calculateBreakEven = () => {
    if (pricePerUnit > variableCostPerUnit) {
      const bep = fixedCosts / (pricePerUnit - variableCostPerUnit);
      setBreakEvenPoint(bep);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('breakEven.fixedCosts', 'التكاليف الثابتة')}
        </label>
        <input
          type="number"
          value={fixedCosts}
          onChange={(e) => setFixedCosts(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('breakEven.variableCost', 'التكلفة المتغيرة للوحدة')}
        </label>
        <input
          type="number"
          step="0.01"
          value={variableCostPerUnit}
          onChange={(e) => setVariableCostPerUnit(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0.00"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('breakEven.price', 'سعر البيع للوحدة')}
        </label>
        <input
          type="number"
          step="0.01"
          value={pricePerUnit}
          onChange={(e) => setPricePerUnit(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0.00"
        />
      </div>
      <button
        onClick={calculateBreakEven}
        className="w-full bg-orange-600 text-white py-2 rounded-md text-sm font-medium hover:bg-orange-700 transition-colors"
      >
        {t('breakEven.calculate', 'احسب نقطة التعادل')}
      </button>
      {breakEvenPoint > 0 && (
        <div className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-md">
          <p className="text-sm font-medium text-orange-900 dark:text-orange-100">
            {t('breakEven.result', 'نقطة التعادل')}: <span className="font-bold">{Math.ceil(breakEvenPoint)} {t('breakEven.units', 'وحدة')}</span>
          </p>
          <p className="text-xs text-orange-700 dark:text-orange-300 mt-1">
            {t('breakEven.revenue', 'إيرادات التعادل')}: ${(Math.ceil(breakEvenPoint) * pricePerUnit).toFixed(2)}
          </p>
        </div>
      )}
    </div>
  );
};

// DCF Calculator Component (simplified)
const DCFCalculator: React.FC = () => {
  const { t } = useTranslation();
  const [cashFlow, setCashFlow] = useState<number>(0);
  const [growthRate, setGrowthRate] = useState<number>(0);
  const [discountRate, setDiscountRate] = useState<number>(0);
  const [years, setYears] = useState<number>(5);
  const [dcfValue, setDCFValue] = useState<number>(0);

  const calculateDCF = () => {
    let totalValue = 0;
    for (let year = 1; year <= years; year++) {
      const futureCashFlow = cashFlow * Math.pow(1 + growthRate / 100, year);
      const presentValue = futureCashFlow / Math.pow(1 + discountRate / 100, year);
      totalValue += presentValue;
    }
    setDCFValue(totalValue);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('dcf.cashFlow', 'التدفق النقدي الحالي')}
        </label>
        <input
          type="number"
          value={cashFlow}
          onChange={(e) => setCashFlow(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0"
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('dcf.growthRate', 'معدل النمو (%)')}
          </label>
          <input
            type="number"
            step="0.1"
            value={growthRate}
            onChange={(e) => setGrowthRate(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
            placeholder="0.0"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('dcf.discountRate', 'معدل الخصم (%)')}
          </label>
          <input
            type="number"
            step="0.1"
            value={discountRate}
            onChange={(e) => setDiscountRate(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
            placeholder="0.0"
          />
        </div>
      </div>
      <button
        onClick={calculateDCF}
        className="w-full bg-indigo-600 text-white py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
      >
        {t('dcf.calculate', 'احسب القيمة الحالية')}
      </button>
      {dcfValue > 0 && (
        <div className="bg-indigo-50 dark:bg-indigo-900/20 p-3 rounded-md">
          <p className="text-sm font-medium text-indigo-900 dark:text-indigo-100">
            {t('dcf.result', 'القيمة الحالية')}: <span className="font-bold">${dcfValue.toFixed(2)}</span>
          </p>
        </div>
      )}
    </div>
  );
};

// Loan Calculator Component
const LoanCalculator: React.FC = () => {
  const { t } = useTranslation();
  const [loanAmount, setLoanAmount] = useState<number>(0);
  const [interestRate, setInterestRate] = useState<number>(0);
  const [loanTerm, setLoanTerm] = useState<number>(0);
  const [monthlyPayment, setMonthlyPayment] = useState<number>(0);

  const calculateLoan = () => {
    const monthlyRate = interestRate / 100 / 12;
    const numberOfPayments = loanTerm * 12;

    if (monthlyRate > 0) {
      const payment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) /
                     (Math.pow(1 + monthlyRate, numberOfPayments) - 1);
      setMonthlyPayment(payment);
    } else {
      setMonthlyPayment(loanAmount / numberOfPayments);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('loan.amount', 'مبلغ القرض')}
        </label>
        <input
          type="number"
          value={loanAmount}
          onChange={(e) => setLoanAmount(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
          placeholder="0"
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('loan.rate', 'معدل الفائدة (%)')}
          </label>
          <input
            type="number"
            step="0.1"
            value={interestRate}
            onChange={(e) => setInterestRate(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
            placeholder="0.0"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('loan.term', 'مدة القرض (سنوات)')}
          </label>
          <input
            type="number"
            value={loanTerm}
            onChange={(e) => setLoanTerm(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white"
            placeholder="0"
          />
        </div>
      </div>
      <button
        onClick={calculateLoan}
        className="w-full bg-red-600 text-white py-2 rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
      >
        {t('loan.calculate', 'احسب القسط الشهري')}
      </button>
      {monthlyPayment > 0 && (
        <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-md">
          <p className="text-sm font-medium text-red-900 dark:text-red-100">
            {t('loan.result', 'القسط الشهري')}: <span className="font-bold">${monthlyPayment.toFixed(2)}</span>
          </p>
          <p className="text-xs text-red-700 dark:text-red-300 mt-1">
            {t('loan.total', 'إجمالي المدفوعات')}: ${(monthlyPayment * loanTerm * 12).toFixed(2)}
          </p>
        </div>
      )}
    </div>
  );
};

export default ToolsSection;