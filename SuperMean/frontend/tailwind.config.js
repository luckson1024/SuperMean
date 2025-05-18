module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#6366f1', // indigo-500
          DEFAULT: '#4f46e5', // indigo-600
          dark: '#4338ca', // indigo-700
        },
        accent: '#f59e42', // orange-400
        background: '#f3f4f6', // gray-100
        surface: '#fff',
      },
      borderRadius: {
        xl: '1.25rem',
      },
      boxShadow: {
        'soft': '0 2px 8px 0 rgba(99,102,241,0.08)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/line-clamp'),
  ],
};
