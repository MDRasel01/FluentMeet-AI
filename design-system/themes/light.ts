import { colors } from '../tokens/colors';
import { shadows } from '../tokens/shadows';

export const lightTheme = {
  name: 'light',
  colors: {
    bgApp: colors.neutral[50],
    bgSurface: colors.neutral[0],
    bgSurfaceElevated: colors.neutral[0],
    bgSubtle: colors.neutral[100],
    borderSubtle: colors.neutral[200],
    borderStrong: colors.neutral[300],
    textHeading: colors.neutral[900],
    textBody: colors.neutral[700],
    textSecondary: colors.neutral[500],
    textMuted: colors.neutral[400],
    primary: colors.primary[500],
    primaryHover: colors.primary[600],
    primaryActive: colors.primary[700],
    primarySoft: colors.primary[50],
    statusSuccess: colors.status.success.DEFAULT,
    statusWarning: colors.status.warning.DEFAULT,
    statusDanger: colors.status.danger.DEFAULT,
    statusInfo: colors.status.info.DEFAULT,
  },
  shadows: {
    sm: shadows.sm,
    md: shadows.md,
    lg: shadows.lg,
  },
} as const;

export type Theme = typeof lightTheme;

