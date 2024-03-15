module.exports = {
  root: false,
  parserOptions: {
    ecmaVersion: 2019,
    sourceType: 'module',
    parser: 'babel-eslint',
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/base',
  ],
  // required to lint *.vue files
  plugins: [
    'vue'
  ],
  // add your custom rules here
  'rules': {
    // allow paren-less arrow functions
    'arrow-parens': 0,
    // allow async-await
    'generator-star-spacing': 0,
    // allow debugger during development
    'no-debugger': process.env.NODE_ENV === 'production' ? 2 : 0,
    // Force semicolons (VirtuCrypt did not override this rule)
    'semi': ['error', 'always'],
    // Allow trailing commas to improve diffs
    'comma-dangle': ['error', 'only-multiline'],
    // A lot of these in the old code
    'no-unused-vars': ["warn", { "vars": "all", "args": "after-used", "ignoreRestSiblings": false }],
    // A lot of these in the old code
    'no-extra-semi': 'warn',
  },
  env: {
    'jquery': true
  },
  'ignorePatterns': [
    // Ignore build files
    '**/build/**',
    // Ignore built files
    '**/dist/**',
    // Ignore legacy angular components
    '**/protected_static/**',
    '**/fxCookieService.js',
    '**/fxLoginService.js',
    '**/fxLogin.js',
    // RIP KMES web
    '**/kmes/vue/**',
  ],
};
