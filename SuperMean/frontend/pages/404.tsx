import React from 'react';

const NotFound = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-100 via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-500">
      <div className="text-center">
        <h1 className="text-7xl font-extrabold text-primary dark:text-primary-light mb-4 animate-bounce">404</h1>
        <h2 className="text-3xl font-bold text-gray-700 dark:text-gray-200 mb-2">Page Not Found</h2>
        <p className="text-lg text-gray-500 dark:text-gray-400 mb-6">Sorry, the page you are looking for does not exist.</p>
        <a href="/dashboard" className="btn-primary px-6 py-3 text-lg">Go to Dashboard</a>
      </div>
    </div>
  );
};

export default NotFound;
