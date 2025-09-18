import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import {
  HeartIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline';

const Footer: React.FC = () => {
  const { t, i18n } = useTranslation();
  const isRTL = i18n.language === 'ar';

  const currentYear = new Date().getFullYear();

  const companyLinks = [
    { key: 'about', href: '/about', label: t('footer.company.about') },
    { key: 'careers', href: '/careers', label: t('footer.company.careers') },
    { key: 'press', href: '/press', label: t('footer.company.press') },
    { key: 'news', href: '/news', label: t('footer.company.news') },
    { key: 'contact', href: '/contact', label: t('footer.company.contact') },
  ];

  const productLinks = [
    { key: 'features', href: '/features', label: t('footer.product.features') },
    { key: 'pricing', href: '/pricing', label: t('footer.product.pricing') },
    { key: 'security', href: '/security', label: t('footer.product.security') },
    { key: 'enterprise', href: '/enterprise', label: t('footer.product.enterprise') },
    { key: 'api', href: '/api', label: t('footer.product.api') },
  ];

  const resourceLinks = [
    { key: 'documentation', href: '/docs', label: t('footer.resources.documentation') },
    { key: 'help', href: '/help', label: t('footer.resources.help') },
    { key: 'support', href: '/support', label: t('footer.resources.support') },
    { key: 'status', href: '/status', label: t('footer.resources.status') },
    { key: 'blog', href: '/blog', label: t('footer.resources.blog') },
  ];

  const legalLinks = [
    { key: 'privacy', href: '/privacy', label: t('footer.legal.privacy') },
    { key: 'terms', href: '/terms', label: t('footer.legal.terms') },
    { key: 'cookies', href: '/cookies', label: t('footer.legal.cookies') },
    { key: 'compliance', href: '/compliance', label: t('footer.legal.compliance') },
  ];

  const socialLinks = [
    {
      key: 'twitter',
      href: 'https://twitter.com/finclick_ai',
      label: t('footer.social.twitter'),
      icon: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
        </svg>
      )
    },
    {
      key: 'linkedin',
      href: 'https://linkedin.com/company/finclick-ai',
      label: t('footer.social.linkedin'),
      icon: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clipRule="evenodd" />
        </svg>
      )
    },
    {
      key: 'facebook',
      href: 'https://facebook.com/finclick.ai',
      label: t('footer.social.facebook'),
      icon: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M20 10c0-5.523-4.477-10-10-10S0 4.477 0 10c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V10h2.54V7.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V10h2.773l-.443 2.89h-2.33v6.988C16.343 19.128 20 14.991 20 10z" clipRule="evenodd" />
        </svg>
      )
    },
    {
      key: 'instagram',
      href: 'https://instagram.com/finclick.ai',
      label: t('footer.social.instagram'),
      icon: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
        </svg>
      )
    },
    {
      key: 'youtube',
      href: 'https://youtube.com/@finclick-ai',
      label: t('footer.social.youtube'),
      icon: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
        </svg>
      )
    },
  ];

  return (
    <footer className="bg-gray-900 text-white">
      {/* Newsletter Section */}
      <div className="bg-gray-800 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">
              {t('footer.newsletter.title')}
            </h3>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              {t('footer.newsletter.description')}
            </p>
            <div className="max-w-md mx-auto flex">
              <input
                type="email"
                placeholder={t('footer.newsletter.placeholder')}
                className="flex-1 px-4 py-3 bg-gray-700 border border-gray-600 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-white placeholder-gray-400"
              />
              <button className="px-6 py-3 bg-primary-500 hover:bg-primary-600 rounded-r-lg font-medium transition-colors">
                {t('footer.newsletter.subscribe')}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-8">
            {/* Company Info */}
            <div className="lg:col-span-2">
              <div className="flex items-center space-x-3 rtl:space-x-reverse mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">F</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold gradient-text">FinClick.AI</h3>
                  <p className="text-sm text-gray-400">{t('branding.tagline')}</p>
                </div>
              </div>
              <p className="text-gray-400 mb-6 leading-relaxed">
                {t('branding.description')}
              </p>

              {/* Contact Info */}
              <div className="space-y-3">
                <div className="flex items-center space-x-3 rtl:space-x-reverse text-sm text-gray-400">
                  <EnvelopeIcon className="w-4 h-4 text-primary-500" />
                  <span>{t('footer.contact.email')}</span>
                </div>
                <div className="flex items-center space-x-3 rtl:space-x-reverse text-sm text-gray-400">
                  <PhoneIcon className="w-4 h-4 text-primary-500" />
                  <span>{t('footer.contact.phone')}</span>
                </div>
                <div className="flex items-center space-x-3 rtl:space-x-reverse text-sm text-gray-400">
                  <MapPinIcon className="w-4 h-4 text-primary-500" />
                  <span>{t('footer.contact.address')}</span>
                </div>
              </div>
            </div>

            {/* Company Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">{t('footer.company.title')}</h4>
              <ul className="space-y-3">
                {companyLinks.map((link) => (
                  <li key={link.key}>
                    <Link
                      to={link.href}
                      className="text-gray-400 hover:text-white transition-colors text-sm"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Product Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">{t('footer.product.title')}</h4>
              <ul className="space-y-3">
                {productLinks.map((link) => (
                  <li key={link.key}>
                    <Link
                      to={link.href}
                      className="text-gray-400 hover:text-white transition-colors text-sm"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">{t('footer.resources.title')}</h4>
              <ul className="space-y-3">
                {resourceLinks.map((link) => (
                  <li key={link.key}>
                    <Link
                      to={link.href}
                      className="text-gray-400 hover:text-white transition-colors text-sm"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Legal Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">{t('footer.legal.title')}</h4>
              <ul className="space-y-3">
                {legalLinks.map((link) => (
                  <li key={link.key}>
                    <Link
                      to={link.href}
                      className="text-gray-400 hover:text-white transition-colors text-sm"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="border-t border-gray-800 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            {/* Copyright */}
            <div className="text-sm text-gray-400">
              <p>
                © {currentYear} FinClick.AI. {t('footer.copyright')}
              </p>
              <p className="flex items-center mt-1">
                {t('footer.madeWith')}
                <HeartIcon className="w-4 h-4 text-red-500 mx-1" />
                {t('footer.in')} الرياض، المملكة العربية السعودية
              </p>
            </div>

            {/* Social Links */}
            <div className="flex items-center space-x-4 rtl:space-x-reverse">
              {socialLinks.map((social) => (
                <motion.a
                  key={social.key}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  aria-label={social.label}
                >
                  {social.icon}
                </motion.a>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;