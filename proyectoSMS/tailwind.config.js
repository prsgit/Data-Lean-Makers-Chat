/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./appSMS/templates/appSMS/**/*.html",
    "./appSMS/static/js/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
      colors: {
        wasabi:'#B5BE04',
        wasabiIntenso:'#CFE401',
        wasabiClaro:'#D9D6A5',
      }
    },
  },
  plugins: [],
};
