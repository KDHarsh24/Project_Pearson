/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Semantic tokens
        primary: '#132642',
        accent: '#d4af37',
        background: '#ffffff',
        surface: '#f7f8fa',
        text: '#222b3a',
        border: '#cfd8e3',
        success: '#2ecc71',
        error: '#e74c3c',
        // Provided palette (light -> dark)
        brand: {
          100: '#a1a8b3',
          200: '#717d8e',
          300: '#425168',
          400: '#2b3c55',
          500: '#132642',
        },
      },
    },
  },
  plugins: [],
};