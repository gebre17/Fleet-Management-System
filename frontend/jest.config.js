const nextJest = require('next/jest');

const createJestConfig = nextJest({
  dir: './',
});

/** @type {import('jest').Config} */
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  // Measure coverage across the whole src tree, not just files a test
  // happens to import — otherwise the % (and any threshold on it) is
  // meaningless.
  collectCoverageFrom: ['src/**/*.{ts,tsx}', '!src/**/*.d.ts', '!src/**/*.test.{ts,tsx}'],
  // A regression floor, not an aspirational target: most pages/hooks/stores
  // have no tests yet (project-wide coverage is ~17-18% as of the tests
  // that do exist). This is set just below that so CI catches coverage
  // *dropping* while more tests get added incrementally over time, rather
  // than gating on a number nothing in the repo currently meets.
  coverageThreshold: {
    global: {
      statements: 15,
      branches: 15,
      functions: 10,
      lines: 15,
    },
  },
  // next/jest auto-maps "@/*" from tsconfig for normal imports, but that
  // mapping doesn't reach jest.mock('@/...') module-specifier strings, so
  // it's declared explicitly here too.
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};

module.exports = createJestConfig(customJestConfig);
