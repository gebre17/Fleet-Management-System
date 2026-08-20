// Pulls in @testing-library/jest-dom's ambient type augmentations (e.g.
// `toBeInTheDocument`, `toBeDisabled`) so `tsc --noEmit` recognizes the
// matchers registered at runtime by jest.setup.js.
import '@testing-library/jest-dom';
