module.exports = {
  root: true,
  env: { browser: true, es2021: true, node: true },
  ignorePatterns: ["dist", "node_modules"],
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
  ],
  parserOptions: { ecmaVersion: "latest", sourceType: "module", ecmaFeatures: { jsx: true } },
  settings: { react: { version: "18.3" } },
  plugins: ["react-refresh"],
  rules: {
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off",
    "react/no-unescaped-entities": "off",
    "react-refresh/only-export-components": "warn",
    "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
  },
};