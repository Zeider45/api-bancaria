import nextPlugin from '@next/eslint-plugin-next';
import tsParser from '@typescript-eslint/parser';

const nextCoreWebVitals = nextPlugin.configs['core-web-vitals'];

export default [
  {
    ignores: ['.next/**', 'node_modules/**'],
  },
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
      },
    },
    plugins: {
      ...nextCoreWebVitals.plugins,
    },
    rules: {
      ...nextCoreWebVitals.rules,
    },
  },
];
