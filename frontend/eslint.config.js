import js from "@eslint/js";
import boundaries from "eslint-plugin-boundaries";
import importPlugin from "eslint-plugin-import";
import jsxA11y from "eslint-plugin-jsx-a11y";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

const LAYERS = ["app", "pages", "features", "shared"];
const NO_RELATIVE = { group: ["../*", "../../*"], message: "Use the @/ alias." };
const FEATURE_INDEX = { group: ["@/features/*/*"], message: "Import a feature through its index file." };

export default tseslint.config(
  { ignores: ["dist", "node_modules"] },
  js.configs.recommended,
  ...tseslint.configs.strict,
  jsxA11y.flatConfigs.recommended,
  reactHooks.configs.flat.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: { globals: globals.browser },
    plugins: { boundaries, import: importPlugin },
    settings: {
      "import/resolver": { typescript: true },
      "boundaries/elements": [
        { type: "app", pattern: "src/app/**" },
        { type: "pages", pattern: "src/pages/**" },
        { type: "features", pattern: "src/features/*", capture: ["feature"] },
        { type: "shared", pattern: "src/shared/**" },
      ],
      "boundaries/include": ["src/**/*"],
    },
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/consistent-type-imports": "error",
      "boundaries/dependencies": [
        "error",
        {
          default: "disallow",
          policies: [
            { from: { element: { type: "app" } }, allow: { to: { element: { types: LAYERS } } } },
            { from: { element: { type: "pages" } }, allow: { to: { element: { types: ["pages", "features", "shared"] } } } },
            {
              from: { element: { type: "features" } },
              allow: [
                { to: { element: { type: "shared" } } },
                { to: { element: { type: "features", captured: { feature: "{{ from.element.captured.feature }}" } } } },
              ],
            },
            { from: { element: { type: "shared" } }, allow: { to: { element: { type: "shared" } } } },
          ],
        },
      ],
      "no-restricted-imports": ["error", { patterns: [NO_RELATIVE, FEATURE_INDEX] }],
      "no-restricted-globals": ["error", { name: "fetch", message: "Use the API client in shared/api." }],
      "no-restricted-syntax": [
        "error",
        {
          selector: "JSXAttribute[name.name='key'] > JSXExpressionContainer Identifier[name=/^(index|idx|i)$/]",
          message: "Do not use an array index as key.",
        },
      ],
      "import/no-cycle": "error",
      complexity: ["error", 10],
      "max-depth": ["error", 4],
      "max-lines": ["error", { max: 300, skipBlankLines: true, skipComments: true }],
      "max-lines-per-function": ["error", { max: 80, skipBlankLines: true, skipComments: true }],
      "max-params": ["error", 4],
    },
  },
  {
    files: ["src/features/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": ["error", { patterns: [NO_RELATIVE] }],
    },
  },
  {
    files: ["src/shared/api/**/*.ts"],
    rules: { "no-restricted-globals": "off" },
  },
);
