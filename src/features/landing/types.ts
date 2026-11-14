export interface AuthUser {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  role?: string;
  goal?: string;
  tier?: 'starter' | 'pro' | 'enterprise';
  token?: string;
  createdAt?: string;
}

export type AuthMode = 'signin' | 'signup' | 'forgot';

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
