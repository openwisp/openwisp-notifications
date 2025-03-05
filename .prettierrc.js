/**
 * @see https://prettier.io/docs/configuration
 * @type {import("prettier").Config}
 */
const config = {
  trailingComma: "es5",
  tabWidth: 2,
  semi: true,
  singleQuote: false,
  arrowParens: "always",
  printWidth: 80, // Adjusting print width can help manage line breaks
  experimentalTernaries: true, // Use experimental ternary formatting
};

module.exports = config;
