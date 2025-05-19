import React from 'react';

const Loading = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-primary-light via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-primary-dark transition-colors duration-500">
      <div className="flex flex-col items-center">
        <svg className="animate-spin h-16 w-16 text-primary dark:text-primary-light mb-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
        </svg>
        <h2 className="text-2xl font-bold text-primary dark:text-primary-light mb-2">Loading...</h2>
        <p className="text-lg text-gray-500 dark:text-gray-400">Please wait while we load your data.</p>
      </div>
    </div>
  );
};

export default Loading;
