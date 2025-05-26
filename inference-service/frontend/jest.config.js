const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    // Handle module aliases (this will be automatically configured for you based on your tsconfig.json paths)
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^@/pages/(.*)$': '<rootDir>/pages/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
  // Add globals for Jest functions
  globals: {
    'ts-jest': {
      useESM: true,
    },
  },
  // Configure module path ignore patterns to avoid Haste conflicts
  modulePathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/.pnpm/',
  ],
  // Configure Haste map ignore patterns
  haste: {
    forceNodeFilesystemAPI: true,
  },
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
