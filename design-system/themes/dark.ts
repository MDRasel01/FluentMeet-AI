import { colors } from '../tokens/colors';
import { shadows } from '../tokens/shadows';

export const darkTheme = {
  name: 'dark',
  colors: {
    bgApp: colors.dark.background,
    bgSurface: colors.dark.surface,
    bgSurfaceElevated: colors.dark.elevatedSurface,
    bgSubtle: colors.dark.subtle,
    borderSubtle: colors.dark.borderSubtle,
    borderStrong: colors.dark.border,
    textHeading: colors.dark.heading,
    textBody: colors.dark.body,
    textSecondary: colors.dark.muted,
    textMuted: colors.dark.disabled,
    primary: colors.primary[500],
    primaryHover: colors.primary[400],
    primaryActive: colors.primary[600],
    primarySoft: colors.primary[950],
    statusSuccess: colors.status.success.DEFAULT,
    statusWarning: colors.status.warning.DEFAULT,
    statusDanger: colors.status.danger.DEFAULT,
    statusInfo: colors.status.info.DEFAULT,
  },
  shadows: {
    sm: shadows.dark.sm,
    md: shadows.dark.md,
    lg: shadows.dark.lg,
  },
} as const;

