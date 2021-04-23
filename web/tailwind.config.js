module.exports = {
  purge: {
    enabled: true,
    content: [
      './public/**/*.html',
      './src/**/*.html',
      './src/**/*.css',
      './src/**/*.js',
    ],
  },
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {
       opacity: ['disabled'],
       cursor: ['disabled'],
    },
  },
  plugins: [],
}
