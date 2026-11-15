import { z } from 'zod';

/**
 * Validation schema for User Registration.
 * Enforces strong password rules and valid email formats to protect database integrity.
 */
export const registerSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, { message: 'Full name must be at least 2 characters.' })
    .max(80, { message: 'Full name cannot exceed 80 characters.' }),
  email: z
    .string()
    .trim()
    .email({ message: 'Please enter a valid work or personal email address.' })
    .toLowerCase(),
  password: z
    .string()
    .min(8, { message: 'Password must be at least 8 characters long.' })
    .regex(/[A-Z]/, { message: 'Password must contain at least one uppercase letter.' })
    .regex(/[a-z]/, { message: 'Password must contain at least one lowercase letter.' })
    .regex(/[0-9]/, { message: 'Password must contain at least one number.' }),
  goal: z.string().optional(),
  role: z.enum(['owner', 'admin', 'member']).optional().default('member'),
});

export type RegisterInput = z.infer<typeof registerSchema>;

/**
 * Validation schema for User Login.
 */
export const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .email({ message: 'Please enter a valid email address.' })
    .toLowerCase(),
  password: z
    .string()
    .min(1, { message: 'Password cannot be empty.' }),
});

export type LoginInput = z.infer<typeof loginSchema>;

/**
 * Safe redirect URL sanitization.
 * Prevents open-redirect vulnerabilities by strictly requiring internal relative paths.
 * Blocks protocol-relative URLs (`//example.com`), backslashes (`/\example.com`), and scheme prefixes.
 */
export function sanitizeInternalRedirect(
  target: string | null | undefined,
  fallback: string = '/dashboard'
): string {
  if (!target || typeof target !== 'string') {
    return fallback;
  }

  const trimmed = target.trim();

  // Must begin with a single slash, not double slash or backslash
  if (
    trimmed.startsWith('/') &&
    !trimmed.startsWith('//') &&
    !trimmed.startsWith('/\\') &&
    !trimmed.includes('\\') &&
    !trimmed.includes('://')
  ) {
    return trimmed;
  }

  return fallback;
}

/**
 * Role check helper: Verifies if a user has founder/owner privileges.
 * UI convenience wrapper; backend DB RLS enforces absolute authorization.
 */
export function isOwnerRole(role?: string | null): boolean {
  if (!role) return false;
  return role.trim().toLowerCase() === 'owner';
}

/**
 * Maps DB and network errors to safe, friendly messages so database internals
 * are never leaked to end users.
 */
export function getFriendlyErrorMessage(err: unknown, defaultMessage = 'An unexpected error occurred. Please try again.'): string {
  if (!err) return defaultMessage;

  const msg = typeof err === 'object' && 'message' in err && typeof (err as any).message === 'string'
    ? (err as any).message
    : String(err);

  const lower = msg.toLowerCase();

  if (lower.includes('duplicate') || lower.includes('unique') || lower.includes('already exists') || lower.includes('409')) {
    return 'An account with this email already exists. Please sign in instead.';
  }
  if (lower.includes('invalid credentials') || lower.includes('incorrect password') || lower.includes('401')) {
    return 'Invalid email or password. Please verify your credentials.';
  }
  if (lower.includes('rate limit') || lower.includes('too many requests') || lower.includes('429')) {
    return 'Too many login attempts. Please wait a few moments before trying again.';
  }
  if (lower.includes('network') || lower.includes('failed to fetch')) {
    return 'Network connection issue. Please check your internet connection.';
  }

  return msg || defaultMessage;
}
