-- ==============================================================================
-- FluentMeet AI: Founder-Only Area & Workbench Migration (0002_founder_workbench.sql)
-- Multi-tenant Row-Level Security, Screen Registry & App Spaces
-- ==============================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Create Enums
DO $$ BEGIN
  CREATE TYPE user_role AS ENUM ('owner', 'user');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE screen_status AS ENUM ('planned', 'in_progress', 'ready');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 2. Profiles Table (Extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
  id                   UUID PRIMARY KEY,
  email                CITEXT NOT NULL,
  role                 user_role NOT NULL DEFAULT 'user',
  must_change_password BOOLEAN NOT NULL DEFAULT false,
  theme                TEXT NOT NULL DEFAULT 'system',
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Constraint: Only ONE owner can exist across the entire platform
CREATE UNIQUE INDEX IF NOT EXISTS one_owner ON public.profiles ((role)) WHERE role = 'owner';

-- 3. App Spaces Table (Dynamic tabs in Founder Workbench)
CREATE TABLE IF NOT EXISTS public.app_spaces (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug       CITEXT NOT NULL UNIQUE,
  name       TEXT NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Screen Registry Table (Dynamic Screen Completion Tracker)
CREATE TABLE IF NOT EXISTS public.screen_registry (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  app_space_id  UUID NOT NULL REFERENCES public.app_spaces(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  route         TEXT NOT NULL,
  status        screen_status NOT NULL DEFAULT 'ready',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_screen_registry_space ON public.screen_registry(app_space_id);
CREATE INDEX IF NOT EXISTS idx_screen_registry_status ON public.screen_registry(status);

-- 5. Row Level Security (RLS) Configuration
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.app_spaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.screen_registry ENABLE ROW LEVEL SECURITY;

-- Helper function: Check if authenticated user is the platform owner
CREATE OR REPLACE FUNCTION public.is_founder_owner()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = auth.uid() AND role = 'owner'
  );
$$;

-- RLS: Profiles Table
-- Users can read their own profile; Owners can view all profiles
DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
CREATE POLICY "profiles_select_own" ON public.profiles
  FOR SELECT USING (auth.uid() = id OR public.is_founder_owner());

-- Prevent non-owners from setting or escalating role
DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
CREATE POLICY "profiles_update_own" ON public.profiles
  FOR UPDATE USING (auth.uid() = id)
  WITH CHECK (
    auth.uid() = id AND (
      role = (SELECT role FROM public.profiles WHERE id = auth.uid()) OR public.is_founder_owner()
    )
  );

-- RLS: App Spaces Table
-- Public read for authorized users, but write access is strictly founder-only
DROP POLICY IF EXISTS "app_spaces_owner_all" ON public.app_spaces;
CREATE POLICY "app_spaces_owner_all" ON public.app_spaces
  FOR ALL USING (public.is_founder_owner());

DROP POLICY IF EXISTS "app_spaces_read" ON public.app_spaces;
CREATE POLICY "app_spaces_read" ON public.app_spaces
  FOR SELECT USING (auth.role() = 'authenticated');

-- RLS: Screen Registry Table
-- Write access is strictly founder-only
DROP POLICY IF EXISTS "screen_registry_owner_all" ON public.screen_registry;
CREATE POLICY "screen_registry_owner_all" ON public.screen_registry
  FOR ALL USING (public.is_founder_owner());

DROP POLICY IF EXISTS "screen_registry_read" ON public.screen_registry;
CREATE POLICY "screen_registry_read" ON public.screen_registry
  FOR SELECT USING (auth.role() = 'authenticated');

-- 6. Trigger: Secure User Sign-up (Always sets role='user')
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO public.profiles (id, email, role, must_change_password)
  VALUES (NEW.id, NEW.email, 'user', false)
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

-- 7. Seed Initial App Spaces (5 Spaces)
INSERT INTO public.app_spaces (slug, name, sort_order) VALUES
  ('landing', 'Landing Page', 1),
  ('dashboard', 'Web Dashboard', 2),
  ('extension', 'Chrome Extension Simulator', 3),
  ('admin', 'Super Admin Console', 4),
  ('design-system', 'Design System Showcase', 5)
ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, sort_order = EXCLUDED.sort_order;

-- 8. Seed Screen Registry (49 Screens total: 21 Dashboard + 15 Extension + 13 Admin)
DELETE FROM public.screen_registry;

-- Dashboard Screens (21)
WITH d AS (SELECT id FROM public.app_spaces WHERE slug = 'dashboard')
INSERT INTO public.screen_registry (app_space_id, name, route, status) VALUES
  ((SELECT id FROM d), 'Overview Dashboard', '/dashboard/overview', 'ready'),
  ((SELECT id FROM d), 'Meetings Directory', '/dashboard/meetings', 'ready'),
  ((SELECT id FROM d), 'Meeting Details Analysis', '/dashboard/meetings/details', 'ready'),
  ((SELECT id FROM d), 'Audio Transcript Viewer', '/dashboard/transcript', 'ready'),
  ((SELECT id FROM d), 'Executive Summary Report', '/dashboard/report', 'ready'),
  ((SELECT id FROM d), 'Personal Performance Scorecard', '/dashboard/performance', 'ready'),
  ((SELECT id FROM d), 'Grammar Correction Center', '/dashboard/grammar', 'ready'),
  ((SELECT id FROM d), 'Executive Vocabulary Suggestions', '/dashboard/vocabulary', 'ready'),
  ((SELECT id FROM d), 'Fluency & Speech Pace Tracker', '/dashboard/fluency', 'ready'),
  ((SELECT id FROM d), 'Pronunciation Drill Lab', '/dashboard/pronunciation', 'ready'),
  ((SELECT id FROM d), 'IELTS & CEFR Band Practice', '/dashboard/ielts-practice', 'ready'),
  ((SELECT id FROM d), 'Interactive Learning Center', '/dashboard/learning', 'ready'),
  ((SELECT id FROM d), 'Mistakes Spaced Flashcards', '/dashboard/mistakes', 'ready'),
  ((SELECT id FROM d), '30-Day Speech Improvement Plan', '/dashboard/improvement-plan', 'ready'),
  ((SELECT id FROM d), 'Team Fluency Benchmark Analytics', '/dashboard/team-analytics', 'ready'),
  ((SELECT id FROM d), 'Team Roles & Member Settings', '/dashboard/team-settings', 'ready'),
  ((SELECT id FROM d), 'Meeting Platform Integrations', '/dashboard/integrations', 'ready'),
  ((SELECT id FROM d), 'Chrome Extension Download Hub', '/dashboard/extension-download', 'ready'),
  ((SELECT id FROM d), 'Billing & Stripe Customer Portal', '/dashboard/billing', 'ready'),
  ((SELECT id FROM d), 'Profile & Career Goal Settings', '/dashboard/profile', 'ready'),
  ((SELECT id FROM d), 'Security & SOC2 Privacy Settings', '/dashboard/privacy', 'ready');

-- Extension Simulator Screens (15)
WITH e AS (SELECT id FROM public.app_spaces WHERE slug = 'extension')
INSERT INTO public.screen_registry (app_space_id, name, route, status) VALUES
  ((SELECT id FROM e), 'Extension Auth Pairing', '/extension/auth', 'ready'),
  ((SELECT id FROM e), 'Home Ready Standby', '/extension/home', 'ready'),
  ((SELECT id FROM e), 'Active Call Detected', '/extension/detected', 'ready'),
  ((SELECT id FROM e), 'Meeting Participants Roster', '/extension/participants', 'ready'),
  ((SELECT id FROM e), 'Dual-Stream Audio Consent', '/extension/consent', 'ready'),
  ((SELECT id FROM e), 'Live Coaching & Pace Monitor', '/extension/live', 'ready'),
  ((SELECT id FROM e), 'Session Paused State', '/extension/paused', 'ready'),
  ((SELECT id FROM e), 'Gemini Linguistic Processing', '/extension/processing', 'ready'),
  ((SELECT id FROM e), 'Post-Call Scorecard Summary', '/extension/completed', 'ready'),
  ((SELECT id FROM e), 'Error: Mic Permission Denied', '/extension/error-permission', 'ready'),
  ((SELECT id FROM e), 'Error: Tab Audio Capture Failed', '/extension/error-audio', 'ready'),
  ((SELECT id FROM e), 'Error: WebSocket Connection Dropped', '/extension/error-connection', 'ready'),
  ((SELECT id FROM e), 'Error: Unsupported URL/Domain', '/extension/error-unsupported', 'ready'),
  ((SELECT id FROM e), 'Error: Session Abruptly Interrupted', '/extension/error-interrupted', 'ready'),
  ((SELECT id FROM e), 'Extension Stealth Preferences', '/extension/settings', 'ready');

-- Super Admin Console Screens (13)
WITH a AS (SELECT id FROM public.app_spaces WHERE slug = 'admin')
INSERT INTO public.screen_registry (app_space_id, name, route, status) VALUES
  ((SELECT id FROM a), 'Super Admin Executive Overview', '/admin/overview', 'ready'),
  ((SELECT id FROM a), 'User Accounts Directory', '/admin/users', 'ready'),
  ((SELECT id FROM a), 'Deep User Audit & Inspection', '/admin/users/details', 'ready'),
  ((SELECT id FROM a), 'Multi-Tenant Organizations', '/admin/orgs', 'ready'),
  ((SELECT id FROM a), 'Organization Seat & Domain Controls', '/admin/orgs/details', 'ready'),
  ((SELECT id FROM a), 'Subscriptions & MRR Billing', '/admin/subscriptions', 'ready'),
  ((SELECT id FROM a), 'Tier Pricing & Quota Config', '/admin/plans', 'ready'),
  ((SELECT id FROM a), 'Gemini AI Token & Cost Metrics', '/admin/ai-usage', 'ready'),
  ((SELECT id FROM a), 'Audio Background Task Queues', '/admin/queues', 'ready'),
  ((SELECT id FROM a), 'System Infrastructure Health', '/admin/system', 'ready'),
  ((SELECT id FROM a), 'Global Error & Crash Traces', '/admin/errors', 'ready'),
  ((SELECT id FROM a), 'Immutable Security Audit Trail', '/admin/audit', 'ready'),
  ((SELECT id FROM a), 'Extension Releases & Rollout Engine', '/admin/releases', 'ready');

COMMIT;
