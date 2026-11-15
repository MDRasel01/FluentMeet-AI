export interface AuthUser {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  role?: 'owner' | 'admin' | 'member' | string;
  jobTitle?: string;
  goal?: string;
  tier?: 'starter' | 'pro' | 'enterprise';
  token?: string;
  mustChangePassword?: boolean;
  theme?: 'light' | 'dark' | 'system';
  createdAt?: string;
}

export type AuthMode = 'signin' | 'signup' | 'forgot';

export type GatedDestination = 'dashboard' | 'extension' | 'chrome-store';

export interface PricingPlan {
  id: string;
  name: string;
  badge?: string;
  description: string;
  monthlyPrice: number;
  yearlyPrice: number;
  isPopular?: boolean;
  ctaText: string;
  features: string[];
}

export interface Testimonial {
  id: string;
  quote: string;
  author: string;
  role: string;
  company: string;
  avatar: string;
  rating: number;
  verified?: boolean;
}

export interface FeatureTabItem {
  id: 'prepare' | 'live' | 'followup';
  title: string;
  badge: string;
  headline: string;
  description: string;
  bullets: string[];
  mockupTag: string;
}
