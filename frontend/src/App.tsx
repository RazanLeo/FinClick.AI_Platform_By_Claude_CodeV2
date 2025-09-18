import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n/config';

// Components
import LoadingSpinner from './components/ui/LoadingSpinner';
import ErrorBoundary from './components/ui/ErrorBoundary';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';

// Pages
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import AnalysisPage from './pages/AnalysisPage';
import ReportsPage from './pages/ReportsPage';
import PricingPage from './pages/PricingPage';
import AuthPage from './pages/AuthPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import ContactPage from './pages/ContactPage';
import AboutPage from './pages/AboutPage';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';

// Contexts
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { AnalysisProvider } from './contexts/AnalysisContext';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <I18nextProvider i18n={i18n}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider>
            <AuthProvider>
              <AnalysisProvider>
                <Router>
                  <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
                    <Navbar />

                    <main className="flex-1">
                      <Suspense fallback={<LoadingSpinner />}>
                        <Routes>
                          {/* Public Routes */}
                          <Route path="/" element={<HomePage />} />
                          <Route path="/pricing" element={<PricingPage />} />
                          <Route path="/auth" element={<AuthPage />} />
                          <Route path="/contact" element={<ContactPage />} />
                          <Route path="/about" element={<AboutPage />} />
                          <Route path="/privacy" element={<PrivacyPage />} />
                          <Route path="/terms" element={<TermsPage />} />

                          {/* Protected Routes */}
                          <Route path="/dashboard" element={<DashboardPage />} />
                          <Route path="/analysis" element={<AnalysisPage />} />
                          <Route path="/reports" element={<ReportsPage />} />
                          <Route path="/profile" element={<ProfilePage />} />
                          <Route path="/settings" element={<SettingsPage />} />

                          {/* 404 Route */}
                          <Route path="*" element={<div className="text-center py-20">
                            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">404</h1>
                            <p className="text-gray-600 dark:text-gray-400 mt-4">الصفحة غير موجودة</p>
                          </div>} />
                        </Routes>
                      </Suspense>
                    </main>

                    <Footer />

                    {/* Toast Notifications */}
                    <Toaster
                      position="top-right"
                      toastOptions={{
                        duration: 4000,
                        style: {
                          background: '#363636',
                          color: '#fff',
                        },
                      }}
                    />
                  </div>
                </Router>
              </AnalysisProvider>
            </AuthProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </I18nextProvider>
    </ErrorBoundary>
  );
};

export default App;