import React from 'react';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useAuthStore } from '../store';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();
  
  const { login, isAuthenticated, isLoading, error, clearError } = useAuthStore();

  useEffect(() => {
    // If user is already authenticated, redirect to dashboard
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-light via-background to-accent dark:from-gray-900 dark:via-gray-800 dark:to-primary-dark transition-colors duration-500">
      <div className="max-w-md w-full space-y-8 card shadow-soft">
        <div className="flex flex-col items-center">
          <h2 className="mt-6 text-center text-4xl font-extrabold text-primary dark:text-primary-light tracking-tight drop-shadow-lg">SuperMean</h2>
          <p className="mt-2 text-center text-lg text-gray-600 dark:text-gray-300">Sign in to your account</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-xl shadow-soft bg-white/80 dark:bg-gray-900/80 p-6 space-y-4">
            <div>
              <label htmlFor="email-address" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Email address</label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="input input-bordered w-full"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="input input-bordered w-full"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="text-red-500 text-sm text-center mt-2">
              {error}
              <button 
                onClick={clearError} 
                className="ml-2 text-primary hover:text-accent underline"
                type="button"
              >
                Dismiss
              </button>
            </div>
          )}

          <div className="flex items-center justify-between mt-4">
            <div className="text-sm">
              <Link href="/register" className="font-medium text-primary hover:text-accent underline">
                Don't have an account? Register
              </Link>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-3 text-lg font-semibold shadow-soft hover:scale-105 transition-transform duration-200"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;