/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a2a4e',
        accent: '#d4af37',
        background: '#ffffff',
        surface: '#f7f8fa',
        text: '#222b3a',
        border: '#cfd8e3',
        success: '#2ecc71',
        error: '#e74c3c',
      },
    },
  },
  plugins: [],
}