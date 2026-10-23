import { vi } from 'vitest'
import '@vitest/expect'
import '@testing-library/jest-dom'

// Mock fetch globally
globalThis.fetch = vi.fn()