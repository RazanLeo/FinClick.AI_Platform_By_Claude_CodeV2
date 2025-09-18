import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

interface StockData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  currency: string;
}

const StockTicker: React.FC = () => {
  const { t } = useTranslation();
  const [stockData, setStockData] = useState<StockData[]>([]);

  // Mock stock data - in production, this would come from an API
  useEffect(() => {
    const mockData: StockData[] = [
      { symbol: 'TASI', name: 'مؤشر تداول', price: 12485.67, change: 124.23, changePercent: 1.01, currency: 'SAR' },
      { symbol: 'DFM', name: 'سوق دبي', price: 4156.78, change: -23.45, changePercent: -0.56, currency: 'AED' },
      { symbol: 'EGX30', name: 'المؤشر المصري', price: 18965.43, change: 234.56, changePercent: 1.25, currency: 'EGP' },
      { symbol: 'QE', name: 'بورصة قطر', price: 10876.34, change: 67.89, changePercent: 0.63, currency: 'QAR' },
      { symbol: 'BHB', name: 'بورصة البحرين', price: 1987.65, change: -12.34, changePercent: -0.62, currency: 'BHD' },
      { symbol: 'MSX', name: 'سوق مسقط', price: 4523.78, change: 45.67, changePercent: 1.02, currency: 'OMR' },
      { symbol: 'KWSE', name: 'بورصة الكويت', price: 7890.12, change: 89.34, changePercent: 1.14, currency: 'KWD' },
      { symbol: 'USDSAR', name: 'الدولار/ريال', price: 3.75, change: 0.01, changePercent: 0.27, currency: 'SAR' },
      { symbol: 'GOLD', name: 'الذهب', price: 2156.78, change: 12.45, changePercent: 0.58, currency: 'USD' },
      { symbol: 'OIL', name: 'النفط', price: 78.45, change: -1.23, changePercent: -1.54, currency: 'USD' },
    ];

    setStockData(mockData);

    // Simulate real-time updates
    const interval = setInterval(() => {
      setStockData(prevData =>
        prevData.map(stock => ({
          ...stock,
          price: stock.price + (Math.random() - 0.5) * 10,
          change: (Math.random() - 0.5) * 20,
          changePercent: (Math.random() - 0.5) * 2,
        }))
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('ar-SA', {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}`;
  };

  const formatChangePercent = (changePercent: number) => {
    const sign = changePercent >= 0 ? '+' : '';
    return `${sign}${changePercent.toFixed(2)}%`;
  };

  if (stockData.length === 0) {
    return null;
  }

  return (
    <div className="bg-secondary-950 text-white py-2 overflow-hidden relative">
      <div className="flex items-center">
        {/* Ticker Label */}
        <div className="flex-shrink-0 px-4 py-1 bg-primary-500 text-secondary-950 font-semibold text-sm">
          {t('stockTicker.title')}
        </div>

        {/* Scrolling Stock Data */}
        <div className="flex-1 overflow-hidden">
          <motion.div
            className="flex space-x-8 rtl:space-x-reverse"
            animate={{ x: ['100%', '-100%'] }}
            transition={{
              duration: 120,
              repeat: Infinity,
              ease: 'linear',
            }}
          >
            {stockData.concat(stockData).map((stock, index) => (
              <div
                key={`${stock.symbol}-${index}`}
                className="flex-shrink-0 flex items-center space-x-6 rtl:space-x-reverse px-6"
              >
                {/* Stock Symbol and Name */}
                <div className="text-sm">
                  <span className="font-semibold text-primary-400">{stock.symbol}</span>
                  <span className="text-gray-300 mx-2">|</span>
                  <span className="text-gray-300">{stock.name}</span>
                </div>

                {/* Price */}
                <div className="text-sm font-medium">
                  {formatPrice(stock.price, stock.currency)} {stock.currency}
                </div>

                {/* Change */}
                <div
                  className={`text-sm font-medium flex items-center space-x-1 rtl:space-x-reverse ${
                    stock.change >= 0
                      ? 'text-green-400'
                      : 'text-red-400'
                  }`}
                >
                  <span>{formatChange(stock.change)}</span>
                  <span>({formatChangePercent(stock.changePercent)})</span>
                  <span className="text-xs">
                    {stock.change >= 0 ? '▲' : '▼'}
                  </span>
                </div>
              </div>
            ))}
          </motion.div>
        </div>

        {/* Live Indicator */}
        <div className="flex-shrink-0 flex items-center px-4">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-2"></div>
          <span className="text-xs text-gray-300">مباشر</span>
        </div>
      </div>
    </div>
  );
};

export default StockTicker;