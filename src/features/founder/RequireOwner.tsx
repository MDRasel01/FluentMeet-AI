import React from 'react';
import { AuthUser } from '../landing/types';
import { NotFoundPage } from './NotFoundPage';

interface RequireOwnerProps {
  user: AuthUser | null;
  onGoHome: () => void;
  children: React.ReactNode;
}

/**
 * Route guard wrapper for all /founder/* routes.
 * 
 * Strict Hard Rules:
 * 1. Checks if session is valid AND user.role === 'owner'.
 * 2. If unauthorized, returns clean 404 Not Found (never 403, no founder DOM leakage).
 */
export const RequireOwner: React.FC<RequireOwnerProps> = ({
  user,
  onGoHome,
  children,
}) => {
  const isOwner = Boolean(user && user.role?.toLowerCase() === 'owner');

  if (!isOwner) {
    return <NotFoundPage onGoHome={onGoHome} />;
  }

  return <>{children}</>;
};
