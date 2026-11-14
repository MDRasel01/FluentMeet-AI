-- FluentMeet AI: multi-tenant schema with Row-Level Security.
-- Run as the OWNER role (fluentmeet_owner). The API connects as fluentmeet_app, which owns
-- nothing and has NOBYPASSRLS, so no policy below can be skipped by application code.
-- Out of band (secret manager):  ALTER ROLE fluentmeet_app LOGIN PASSWORD '...';
BEGIN;

CREATE EXTENSION IF NOT EXISTS citext;
CREATE SCHEMA IF NOT EXISTS app;

DO $$ BEGIN
  CREATE ROLE fluentmeet_app NOLOGIN NOSUPERUSER NOBYPASSRLS;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TYPE tenant_tier        AS ENUM ('free', 'pro', 'team', 'enterprise');
CREATE TYPE member_role        AS ENUM ('owner', 'admin', 'member');
CREATE TYPE meeting_platform   AS ENUM ('google_meet', 'zoom', 'teams', 'other');
CREATE TYPE meeting_status     AS ENUM ('recording', 'processing', 'completed', 'failed');
CREATE TYPE meeting_visibility AS ENUM ('private', 'team');
CREATE TYPE mistake_category   AS ENUM ('grammar', 'vocabulary', 'pronunciation', 'filler_words', 'fluency', 'tone');

-- ---------------------------------------------------------------- identity
CREATE TABLE tenants (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name                   text NOT NULL CHECK (length(name) BETWEEN 1 AND 120),
  slug                   citext NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9][a-z0-9-]{2,62}$'),
  tier                   tenant_tier NOT NULL DEFAULT 'free',
  max_seats              int NOT NULL DEFAULT 1 CHECK (max_seats >= 1),
  is_personal            boolean NOT NULL DEFAULT false,
  stripe_customer_id     text UNIQUE,
  stripe_subscription_id text UNIQUE,
  created_at             timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email             citext NOT NULL UNIQUE,
  hashed_password   text NOT NULL,
  full_name         text NOT NULL DEFAULT '',
  goal              text,
  avatar_url        text,
  default_tenant_id uuid REFERENCES tenants(id) ON DELETE SET NULL,
  email_verified_at timestamptz,
  is_active         boolean NOT NULL DEFAULT true,
  created_at        timestamptz NOT NULL DEFAULT now()
);

-- One row per (user, tenant): a person can belong to a personal workspace and several companies.
CREATE TABLE memberships (
  tenant_id  uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id    uuid NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
  role       member_role NOT NULL DEFAULT 'member',
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, user_id)
);
CREATE INDEX memberships_user_idx ON memberships (user_id);

CREATE TABLE invitations (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email       citext NOT NULL,
  role        member_role NOT NULL DEFAULT 'member' CHECK (role <> 'owner'),
  token_hash  text NOT NULL UNIQUE,
  invited_by  uuid REFERENCES users(id) ON DELETE SET NULL,
  expires_at  timestamptz NOT NULL,
  accepted_at timestamptz,
  revoked_at  timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX invitations_pending_uq ON invitations (tenant_id, email)
  WHERE accepted_at IS NULL AND revoked_at IS NULL;

-- Auth bookkeeping tables are reached only through auth code paths (no RLS, tokens stored hashed).
CREATE TABLE refresh_tokens (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  family_id   uuid NOT NULL,
  token_hash  text NOT NULL UNIQUE,
  user_agent  text,
  expires_at  timestamptz NOT NULL,
  revoked_at  timestamptz,
  replaced_by uuid,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX refresh_tokens_user_idx ON refresh_tokens (user_id) WHERE revoked_at IS NULL;
CREATE INDEX refresh_tokens_family_idx ON refresh_tokens (family_id);

CREATE TABLE password_reset_tokens (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash text NOT NULL UNIQUE,
  expires_at timestamptz NOT NULL,
  used_at    timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------- product data
CREATE TABLE meetings (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id        uuid NOT NULL,
  user_id          uuid NOT NULL,
  title            text NOT NULL DEFAULT 'Untitled meeting',
  platform         meeting_platform NOT NULL DEFAULT 'other',
  status           meeting_status NOT NULL DEFAULT 'recording',
  visibility       meeting_visibility NOT NULL DEFAULT 'private',
  started_at       timestamptz NOT NULL DEFAULT now(),
  ended_at         timestamptz,
  duration_seconds int NOT NULL DEFAULT 0 CHECK (duration_seconds >= 0),
  audio_url        text,  -- private object-storage KEY, never a public URL; sign on read
  cefr_band        text CHECK (cefr_band IN ('A1','A2','B1','B2','C1','C2')),
  fluency_score    numeric(5,2) CHECK (fluency_score BETWEEN 0 AND 100),
  created_at       timestamptz NOT NULL DEFAULT now(),
  FOREIGN KEY (tenant_id, user_id) REFERENCES memberships (tenant_id, user_id) ON DELETE CASCADE
);
CREATE INDEX meetings_owner_idx ON meetings (tenant_id, user_id, started_at DESC);

CREATE TABLE transcript_segments (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  meeting_id   uuid NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
  timestamp_ms int  NOT NULL CHECK (timestamp_ms >= 0),
  speaker_id   text NOT NULL,
  text         text NOT NULL
);
CREATE INDEX transcript_meeting_idx ON transcript_segments (meeting_id, timestamp_ms);

CREATE TABLE mistakes (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  meeting_id     uuid NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
  timestamp_ms   int  NOT NULL CHECK (timestamp_ms >= 0),
  speaker_id     text NOT NULL,
  original_text  text NOT NULL,
  corrected_text text NOT NULL,
  category       mistake_category NOT NULL,
  explanation    text
);
CREATE INDEX mistakes_meeting_idx ON mistakes (meeting_id, timestamp_ms);

CREATE TABLE tier_limits (
  tier                 tenant_tier PRIMARY KEY,
  monthly_audio_seconds int  -- NULL = unlimited
);
INSERT INTO tier_limits VALUES ('free', 18000), ('pro', 180000), ('team', 360000), ('enterprise', NULL);

CREATE TABLE user_quotas (
  tenant_id          uuid NOT NULL,
  user_id            uuid NOT NULL,
  audio_seconds_used int  NOT NULL DEFAULT 0 CHECK (audio_seconds_used >= 0),
  quota_reset_date   date NOT NULL,
  PRIMARY KEY (tenant_id, user_id),
  FOREIGN KEY (tenant_id, user_id) REFERENCES memberships (tenant_id, user_id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------- RLS context helpers
-- Set per transaction by the API: set_config('app.current_user_id', ..., true)
CREATE FUNCTION app.current_user_id() RETURNS uuid LANGUAGE sql STABLE
  AS $$ SELECT NULLIF(current_setting('app.current_user_id', true), '')::uuid $$;
CREATE FUNCTION app.current_tenant_id() RETURNS uuid LANGUAGE sql STABLE
  AS $$ SELECT NULLIF(current_setting('app.current_tenant_id', true), '')::uuid $$;
CREATE FUNCTION app.current_member_role() RETURNS text LANGUAGE sql STABLE
  AS $$ SELECT NULLIF(current_setting('app.current_member_role', true), '') $$;
CREATE FUNCTION app.next_reset() RETURNS date LANGUAGE sql STABLE
  AS $$ SELECT (date_trunc('month', now() AT TIME ZONE 'UTC') + interval '1 month')::date $$;

-- ---------------------------------------------------------------- RLS policies
ALTER TABLE tenants             ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships         ENABLE ROW LEVEL SECURITY;
ALTER TABLE invitations         ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings            ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcript_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE mistakes            ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_quotas         ENABLE ROW LEVEL SECURITY;

-- tenants: visible if you are a member; only owner/admin of the current tenant may edit its name.
CREATE POLICY tenants_read ON tenants FOR SELECT USING (
  id = app.current_tenant_id()
  OR id IN (SELECT tenant_id FROM memberships WHERE user_id = app.current_user_id()));
CREATE POLICY tenants_update ON tenants FOR UPDATE
  USING (id = app.current_tenant_id() AND app.current_member_role() IN ('owner','admin'))
  WITH CHECK (id = app.current_tenant_id());

-- memberships: see your own rows and your current tenant's roster; managing rules mirror RBAC.
CREATE POLICY mem_read ON memberships FOR SELECT USING (
  user_id = app.current_user_id() OR tenant_id = app.current_tenant_id());
CREATE POLICY mem_update ON memberships FOR UPDATE
  USING (tenant_id = app.current_tenant_id() AND role <> 'owner'
         AND (app.current_member_role() = 'owner'
              OR (app.current_member_role() = 'admin' AND role = 'member')))
  WITH CHECK (tenant_id = app.current_tenant_id() AND role <> 'owner'
              AND (app.current_member_role() = 'owner' OR role = 'member'));
CREATE POLICY mem_delete ON memberships FOR DELETE USING (
  tenant_id = app.current_tenant_id() AND role <> 'owner'
  AND (user_id = app.current_user_id()
       OR app.current_member_role() = 'owner'
       OR (app.current_member_role() = 'admin' AND role = 'member')));

CREATE POLICY inv_admin ON invitations FOR ALL
  USING (tenant_id = app.current_tenant_id() AND app.current_member_role() IN ('owner','admin'))
  WITH CHECK (tenant_id = app.current_tenant_id() AND app.current_member_role() IN ('owner','admin'));

-- meetings: owner has full access; teammates read only meetings explicitly shared with the team.
-- Admins do NOT get a bypass: private means private.
CREATE POLICY meetings_own ON meetings FOR ALL
  USING (tenant_id = app.current_tenant_id() AND user_id = app.current_user_id())
  WITH CHECK (tenant_id = app.current_tenant_id() AND user_id = app.current_user_id());
CREATE POLICY meetings_team_read ON meetings FOR SELECT
  USING (tenant_id = app.current_tenant_id() AND visibility = 'team');

-- transcripts and mistakes inherit access from meetings (the inner SELECT is itself filtered by RLS).
CREATE POLICY seg_own ON transcript_segments FOR ALL
  USING (EXISTS (SELECT 1 FROM meetings m WHERE m.id = transcript_segments.meeting_id
                 AND m.user_id = app.current_user_id() AND m.tenant_id = app.current_tenant_id()))
  WITH CHECK (EXISTS (SELECT 1 FROM meetings m WHERE m.id = transcript_segments.meeting_id
                 AND m.user_id = app.current_user_id() AND m.tenant_id = app.current_tenant_id()));
CREATE POLICY seg_team_read ON transcript_segments FOR SELECT
  USING (EXISTS (SELECT 1 FROM meetings m WHERE m.id = transcript_segments.meeting_id));

CREATE POLICY mis_own ON mistakes FOR ALL
  USING (EXISTS (SELECT 1 FROM meetings m WHERE m.id = mistakes.meeting_id
                 AND m.user_id = app.current_user_id() AND m.tenant_id = app.current_tenant_id()))
  WITH CHECK (EXISTS (SELECT 1 FROM meetings m WHERE m.id = mistakes.meeting_id
                 AND m.user_id = app.current_user_id() AND m.tenant_id = app.current_tenant_id()));
CREATE POLICY mis_team_read ON mistakes FOR SELECT
  USING (EXISTS (SELECT 1 FROM meetings m WHERE m.id = mistakes.meeting_id));

CREATE POLICY quota_own ON user_quotas FOR ALL
  USING (tenant_id = app.current_tenant_id() AND user_id = app.current_user_id())
  WITH CHECK (tenant_id = app.current_tenant_id() AND user_id = app.current_user_id());
CREATE POLICY quota_admin_read ON user_quotas FOR SELECT
  USING (tenant_id = app.current_tenant_id() AND app.current_member_role() IN ('owner','admin'));

-- ---------------------------------------------------------------- bootstrap functions (SECURITY DEFINER)
-- These run as the table owner (bypassing RLS) for the few operations where the caller
-- is not yet a member. Each is narrow, validates its inputs and fixes search_path.
CREATE FUNCTION app.signup(p_email citext, p_hash text, p_name text, p_goal text, p_workspace text, p_slug citext)
RETURNS TABLE (o_user_id uuid, o_tenant_id uuid)
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
DECLARE v_user uuid; v_tenant uuid;
BEGIN
  INSERT INTO tenants (name, slug, is_personal) VALUES (p_workspace, p_slug, true) RETURNING id INTO v_tenant;
  INSERT INTO users (email, hashed_password, full_name, goal, default_tenant_id)
    VALUES (p_email, p_hash, p_name, p_goal, v_tenant) RETURNING id INTO v_user;
  INSERT INTO memberships (tenant_id, user_id, role) VALUES (v_tenant, v_user, 'owner');
  INSERT INTO user_quotas (tenant_id, user_id, quota_reset_date) VALUES (v_tenant, v_user, app.next_reset());
  RETURN QUERY SELECT v_user, v_tenant;
END $$;

CREATE FUNCTION app.create_organization(p_user uuid, p_name text, p_slug citext)
RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
DECLARE v_tenant uuid;
BEGIN
  INSERT INTO tenants (name, slug) VALUES (p_name, p_slug) RETURNING id INTO v_tenant;
  INSERT INTO memberships (tenant_id, user_id, role) VALUES (v_tenant, p_user, 'owner');
  INSERT INTO user_quotas (tenant_id, user_id, quota_reset_date) VALUES (v_tenant, p_user, app.next_reset());
  RETURN v_tenant;
END $$;

CREATE FUNCTION app.accept_invitation(p_token_hash text, p_user uuid)
RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
DECLARE inv invitations%ROWTYPE; v_email citext; v_cap int; v_seats int; v_already boolean;
BEGIN
  SELECT email INTO v_email FROM users WHERE id = p_user AND is_active;
  SELECT * INTO inv FROM invitations WHERE token_hash = p_token_hash FOR UPDATE;
  IF v_email IS NULL OR NOT FOUND OR inv.accepted_at IS NOT NULL OR inv.revoked_at IS NOT NULL
     OR inv.expires_at < now() OR inv.email <> v_email THEN
    RAISE EXCEPTION 'invitation_invalid' USING ERRCODE = 'P0001';
  END IF;
  SELECT max_seats INTO v_cap FROM tenants WHERE id = inv.tenant_id FOR UPDATE;
  SELECT count(*) INTO v_seats FROM memberships WHERE tenant_id = inv.tenant_id;
  SELECT EXISTS (SELECT 1 FROM memberships WHERE tenant_id = inv.tenant_id AND user_id = p_user) INTO v_already;
  IF NOT v_already AND v_seats >= v_cap THEN
    RAISE EXCEPTION 'no_seats_available' USING ERRCODE = 'P0001';
  END IF;
  INSERT INTO memberships (tenant_id, user_id, role) VALUES (inv.tenant_id, p_user, inv.role)
    ON CONFLICT DO NOTHING;
  INSERT INTO user_quotas (tenant_id, user_id, quota_reset_date)
    VALUES (inv.tenant_id, p_user, app.next_reset()) ON CONFLICT DO NOTHING;
  UPDATE invitations SET accepted_at = now() WHERE id = inv.id;
  RETURN inv.tenant_id;
END $$;

-- Billing (called by your Stripe webhook handler, which has no user context).
CREATE FUNCTION app.link_stripe_customer(p_tenant uuid, p_customer text) RETURNS void
LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
  UPDATE tenants SET stripe_customer_id = p_customer WHERE id = p_tenant AND stripe_customer_id IS NULL $$;
CREATE FUNCTION app.apply_subscription(p_customer text, p_subscription text, p_tier tenant_tier, p_seats int)
RETURNS void LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
  UPDATE tenants SET tier = p_tier, max_seats = GREATEST(p_seats, 1), stripe_subscription_id = p_subscription
  WHERE stripe_customer_id = p_customer $$;

-- ---------------------------------------------------------------- grants for the API role
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA app TO fluentmeet_app;
GRANT EXECUTE ON FUNCTION app.current_user_id(), app.current_tenant_id(), app.current_member_role(), app.next_reset() TO fluentmeet_app;

REVOKE ALL ON FUNCTION app.signup(citext,text,text,text,text,citext),
  app.create_organization(uuid,text,citext), app.accept_invitation(text,uuid),
  app.link_stripe_customer(uuid,text), app.apply_subscription(text,text,tenant_tier,int) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app.signup(citext,text,text,text,text,citext),
  app.create_organization(uuid,text,citext), app.accept_invitation(text,uuid),
  app.link_stripe_customer(uuid,text), app.apply_subscription(text,text,tenant_tier,int) TO fluentmeet_app;

GRANT SELECT ON tier_limits TO fluentmeet_app;
GRANT SELECT, UPDATE (name) ON tenants TO fluentmeet_app;
GRANT SELECT, UPDATE (hashed_password, full_name, goal, avatar_url, default_tenant_id, email_verified_at) ON users TO fluentmeet_app;
GRANT SELECT, UPDATE (role), DELETE ON memberships TO fluentmeet_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON invitations, meetings, transcript_segments, mistakes, user_quotas TO fluentmeet_app;
GRANT SELECT, INSERT, UPDATE ON refresh_tokens, password_reset_tokens TO fluentmeet_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO fluentmeet_app;

COMMIT;
