import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bars3Icon,
  XMarkIcon,
  ChevronDownIcon,
  UserCircleIcon,
  CogIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon,
  LanguageIcon,
  BellIcon,
} from '@heroicons/react/24/outline';

// Components
import StockTicker from './StockTicker';

// Hooks
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';

const Navbar: React.FC = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  const isRTL = i18n.language === 'ar';

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Navigation items
  const navigationItems = [
    { key: 'home', href: '/', label: t('navigation.home') },
    { key: 'dashboard', href: '/dashboard', label: t('navigation.dashboard'), requireAuth: true },
    { key: 'analysis', href: '/analysis', label: t('navigation.analysis'), requireAuth: true },
    { key: 'reports', href: '/reports', label: t('navigation.reports'), requireAuth: true },
    { key: 'pricing', href: '/pricing', label: t('navigation.pricing') },
    { key: 'help', href: '/help', label: t('navigation.help') },
    { key: 'contact', href: '/contact', label: t('navigation.contact') },
  ];

  const filteredNavItems = navigationItems.filter(item => !item.requireAuth || user);

  // Language toggle
  const toggleLanguage = () => {
    const newLang = i18n.language === 'ar' ? 'en' : 'ar';
    i18n.changeLanguage(newLang);
  };

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/');
    setIsUserMenuOpen(false);
  };

  return (
    <>
      {/* Stock Ticker */}
      <StockTicker />

      {/* Main Navbar */}
      <nav
        className={`
          sticky top-0 z-50 bg-white dark:bg-gray-900 transition-all duration-200
          ${isScrolled ? 'shadow-lg border-b border-gray-200 dark:border-gray-700' : 'border-b border-gray-100 dark:border-gray-800'}
        `}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link
              to="/"
              className="flex items-center space-x-3 rtl:space-x-reverse hover:opacity-80 transition-opacity"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">F</span>
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold gradient-text">FinClick.AI</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {t('branding.tagline')}
                </span>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8 rtl:space-x-reverse">
              {filteredNavItems.map((item) => (
                <Link
                  key={item.key}
                  to={item.href}
                  className={`
                    text-sm font-medium transition-colors duration-200 hover:text-primary-600 dark:hover:text-primary-400
                    ${location.pathname === item.href
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-gray-700 dark:text-gray-300'
                    }
                  `}
                >
                  {item.label}
                </Link>
              ))}
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-4 rtl:space-x-reverse">
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? (
                  <SunIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                ) : (
                  <MoonIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                )}
              </button>

              {/* Language Toggle */}
              <button
                onClick={toggleLanguage}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center space-x-1 rtl:space-x-reverse"
                aria-label="Toggle language"
              >
                <LanguageIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                  {i18n.language.toUpperCase()}
                </span>
              </button>

              {/* User Menu or Auth Buttons */}
              {user ? (
                <>
                  {/* Notifications */}
                  <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors relative">
                    <BellIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                  </button>

                  {/* User Dropdown */}
                  <div className="relative">
                    <button
                      onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                      className="flex items-center space-x-2 rtl:space-x-reverse p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      <UserCircleIcon className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300 hidden sm:block">
                        {user.firstName}
                      </span>
                      <ChevronDownIcon className="w-4 h-4 text-gray-500" />
                    </button>

                    {/* User Dropdown Menu */}
                    <AnimatePresence>
                      {isUserMenuOpen && (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.95, y: -10 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.95, y: -10 }}
                          className={`
                            absolute top-full mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1
                            ${isRTL ? 'left-0' : 'right-0'}
                          `}
                        >
                          <Link
                            to="/profile"
                            className="flex items-center space-x-3 rtl:space-x-reverse px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                            onClick={() => setIsUserMenuOpen(false)}
                          >
                            <UserCircleIcon className="w-4 h-4" />
                            <span>{t('navigation.profile')}</span>
                          </Link>
                          <Link
                            to="/settings"
                            className="flex items-center space-x-3 rtl:space-x-reverse px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                            onClick={() => setIsUserMenuOpen(false)}
                          >
                            <CogIcon className="w-4 h-4" />
                            <span>{t('navigation.settings')}</span>
                          </Link>
                          <hr className="my-1 border-gray-200 dark:border-gray-700" />
                          <button
                            onClick={handleLogout}
                            className="flex items-center space-x-3 rtl:space-x-reverse px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
                          >
                            <ArrowRightOnRectangleIcon className="w-4 h-4" />
                            <span>{t('navigation.logout')}</span>
                          </button>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </>
              ) : (
                <div className="flex items-center space-x-3 rtl:space-x-reverse">
                  <Link
                    to="/auth?mode=login"
                    className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  >
                    {t('navigation.login')}
                  </Link>
                  <Link
                    to="/auth?mode=register"
                    className="btn btn-primary btn-sm"
                  >
                    {t('navigation.register')}
                  </Link>
                </div>
              )}

              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Toggle menu"
              >
                {isMenuOpen ? (
                  <XMarkIcon className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                ) : (
                  <Bars3Icon className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                )}
              </button>
            </div>
          </div>

          {/* Mobile Navigation Menu */}
          <AnimatePresence>
            {isMenuOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="md:hidden border-t border-gray-200 dark:border-gray-700 py-4"
              >
                <div className="flex flex-col space-y-3">
                  {filteredNavItems.map((item) => (
                    <Link
                      key={item.key}
                      to={item.href}
                      className={`
                        text-sm font-medium px-4 py-2 rounded-lg transition-colors
                        ${location.pathname === item.href
                          ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                        }
                      `}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      {item.label}
                    </Link>
                  ))}

                  {/* Mobile Auth Buttons */}
                  {!user && (
                    <div className="flex flex-col space-y-2 px-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <Link
                        to="/auth?mode=login"
                        className="btn btn-outline w-full"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        {t('navigation.login')}
                      </Link>
                      <Link
                        to="/auth?mode=register"
                        className="btn btn-primary w-full"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        {t('navigation.register')}
                      </Link>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </nav>
    </>
  );
};

export default Navbar;