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
        wasabi:'#A8BF2A',
        wasabiIntenso:'#CFE401',
        wasabiClaro:'#D9D6A5',
        hoverHome:'#92A525'
      }
    },
  },
  plugins: [],
};
