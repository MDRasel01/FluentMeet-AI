-- =============================================================================
-- FluentMeet AI  |  Founder Workbench: User Management, Sessions, Audit Trail
-- Migration: 0003_founder_user_management_audit.sql
-- Target: Supabase (PostgreSQL 15+)
-- =============================================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;

-- ---------- ENUMS ------------------------------------------------------------
DO $$ BEGIN
  CREATE TYPE public.user_role AS ENUM ('owner', 'admin', 'member');
EXCEPTION WHEN duplicate_object THEN
  -- Safely add enum values if user_role already exists (e.g. from 0002)
  ALTER TYPE public.user_role ADD VALUE IF NOT EXISTS 'admin';
  ALTER TYPE public.user_role ADD VALUE IF NOT EXISTS 'member';
END $$;

DO $$ BEGIN
  CREATE TYPE public.user_status AS ENUM ('active', 'suspended');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE public.audit_event_type AS ENUM (
    'LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_REVOKED', 'PASSWORD_CHANGED',
    'ACCOUNT_LOCKED', 'ACCOUNT_UNLOCKED', 'ROLE_CHANGED', 'STATUS_CHANGED'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ---------- PROFILES (Enhance existing or create) -----------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
  id                  UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email               TEXT NOT NULL,
  display_name        TEXT,
  role                public.user_role   NOT NULL DEFAULT 'member',
  status              public.user_status NOT NULL DEFAULT 'active',
  failed_login_count  INT  NOT NULL DEFAULT 0 CHECK (failed_login_count >= 0),
  locked_until        TIMESTAMPTZ,
  last_seen_at        TIMESTAMPTZ,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT profiles_email_lowercase CHECK (email = lower(email))
);

-- Ensure columns exist if table was created by earlier migration
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS display_name TEXT;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS status public.user_status NOT NULL DEFAULT 'active';
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS failed_login_count INT NOT NULL DEFAULT 0;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS profiles_email_key    ON public.profiles (email);
CREATE UNIQUE INDEX IF NOT EXISTS profiles_single_owner ON public.profiles (role) WHERE role = 'owner';
CREATE INDEX IF NOT EXISTS profiles_created_at_idx      ON public.profiles (created_at);

-- Trigger for new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  INSERT INTO public.profiles (id, email)
  VALUES (new.id, lower(new.email))
  ON CONFLICT (id) DO UPDATE SET email = lower(new.email);
  RETURN new;
END $$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ---------- USER SESSIONS ----------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_sessions (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  session_token_hash  TEXT NOT NULL,             -- sha256(auth session_id claim); never token itself
  ip_address          INET,                      -- MASKED (/24 v4, /48 v6) by the Edge Function
  ip_hash             TEXT,                      -- HMAC(ip, pepper) for correlation without storing IP
  country_code        CHAR(2),
  user_agent          TEXT,
  device_info         JSONB NOT NULL DEFAULT '{}'::jsonb,
  started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_active_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at            TIMESTAMPTZ,
  end_reason          TEXT CHECK (end_reason IN ('logout', 'timeout', 'revoked', 'suspended')),
  is_revoked          BOOLEAN NOT NULL DEFAULT false,
  CONSTRAINT sessions_time_order CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE UNIQUE INDEX IF NOT EXISTS user_sessions_token_hash_key ON public.user_sessions (session_token_hash);
CREATE INDEX IF NOT EXISTS user_sessions_user_started_idx      ON public.user_sessions (user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS user_sessions_live_idx ON public.user_sessions (last_active_at)
  WHERE is_revoked = false AND ended_at IS NULL;

-- ---------- AUDIT LOG (partitioned, append-only) ------------------------------
CREATE TABLE IF NOT EXISTS public.auth_audit_logs (
  id               UUID NOT NULL DEFAULT gen_random_uuid(),
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  user_id          UUID,
  actor_id         UUID,                         -- who performed an admin action
  event_type       public.audit_event_type NOT NULL,
  identifier_hash  TEXT,                         -- HMAC(email) for failed logins on unknown accounts
  ip_address       INET,
  ip_hash          TEXT,
  country_code     CHAR(2),
  user_agent       TEXT,
  metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS public.auth_audit_logs_default PARTITION OF public.auth_audit_logs DEFAULT;

CREATE OR REPLACE FUNCTION public.ensure_audit_partitions(p_months_ahead INT DEFAULT 2)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE m date;
BEGIN
  FOR i IN 0 .. p_months_ahead LOOP
    m := (date_trunc('month', now() AT TIME ZONE 'utc') + make_interval(months => i))::date;
    EXECUTE format(
      'CREATE TABLE IF NOT EXISTS public.auth_audit_logs_%s PARTITION OF public.auth_audit_logs
         FOR VALUES FROM (%L) TO (%L)',
      to_char(m, 'YYYY_MM'),
      (m::timestamp AT TIME ZONE 'utc'),
      ((m + interval '1 month')::timestamp AT TIME ZONE 'utc'));
  END LOOP;
END $$;
SELECT public.ensure_audit_partitions(2);

-- Indexes on audit logs
CREATE INDEX IF NOT EXISTS audit_user_created_idx   ON public.auth_audit_logs (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_keyset_idx         ON public.auth_audit_logs (created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS audit_event_created_idx  ON public.auth_audit_logs (event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS audit_created_brin       ON public.auth_audit_logs USING brin (created_at);
CREATE INDEX IF NOT EXISTS audit_failed_ip_idx      ON public.auth_audit_logs (ip_hash, created_at DESC)
  WHERE event_type = 'LOGIN_FAILED';

-- Immutability: block UPDATE/DELETE for everyone; only GDPR erasure may UPDATE.
CREATE OR REPLACE FUNCTION public.audit_block_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  IF tg_op = 'UPDATE' AND current_setting('app.gdpr_erasure', true) = 'on' THEN
    RETURN new;
  END IF;
  RAISE EXCEPTION 'auth_audit_logs is append-only' USING errcode = '42501';
END $$;

DROP TRIGGER IF EXISTS audit_no_update_delete ON public.auth_audit_logs;
CREATE TRIGGER audit_no_update_delete BEFORE UPDATE OR DELETE ON public.auth_audit_logs
  FOR EACH ROW EXECUTE FUNCTION public.audit_block_mutation();

REVOKE UPDATE, DELETE, TRUNCATE ON public.auth_audit_logs
  FROM public, anon, authenticated, service_role;

-- GDPR erasure
CREATE OR REPLACE FUNCTION public.erase_user_audit_pii(p_user_id UUID) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE n bigint;
BEGIN
  PERFORM set_config('app.gdpr_erasure', 'on', true);
  UPDATE public.auth_audit_logs
     SET ip_address = null, ip_hash = null, user_agent = null, identifier_hash = null,
         metadata = '{}'::jsonb, user_id = null
   WHERE user_id = p_user_id;
  GET DIAGNOSTICS n = row_count;
  RETURN n;
END $$;
REVOKE EXECUTE ON FUNCTION public.erase_user_audit_pii(UUID) FROM public, anon, authenticated;
GRANT  EXECUTE ON FUNCTION public.erase_user_audit_pii(UUID) TO service_role;

-- ---------- DAILY ROLLUP -----------------------------------------------------
CREATE TABLE IF NOT EXISTS public.daily_metrics_rollup (
  day                DATE PRIMARY KEY,
  total_users        INT NOT NULL DEFAULT 0,
  new_signups        INT NOT NULL DEFAULT 0,
  dau                INT NOT NULL DEFAULT 0,
  returning_users    INT NOT NULL DEFAULT 0,
  successful_logins  INT NOT NULL DEFAULT 0,
  failed_logins      INT NOT NULL DEFAULT 0,
  peak_concurrent    INT NOT NULL DEFAULT 0,
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION public.refresh_daily_metrics(
  p_day DATE DEFAULT (now() AT TIME ZONE 'utc')::date
) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE
  d0 timestamptz := (p_day::timestamp AT TIME ZONE 'utc');
  d1 timestamptz := d0 + interval '1 day';
  live int;
BEGIN
  SELECT count(*) INTO live FROM public.user_sessions
   WHERE ended_at IS NULL AND NOT is_revoked AND last_active_at > now() - interval '5 minutes';

  INSERT INTO public.daily_metrics_rollup AS r
    (day, total_users, new_signups, dau, returning_users, successful_logins, failed_logins,
     peak_concurrent, updated_at)
  SELECT p_day,
    (SELECT count(*) FROM public.profiles WHERE created_at < d1),
    (SELECT count(*) FROM public.profiles WHERE created_at >= d0 AND created_at < d1),
    (SELECT count(distinct user_id) FROM public.user_sessions
       WHERE started_at < d1 AND last_active_at >= d0),
    (SELECT count(distinct s.user_id) FROM public.user_sessions s
       JOIN public.profiles p ON p.id = s.user_id
       WHERE s.started_at < d1 AND s.last_active_at >= d0 AND p.created_at < d0),
    (SELECT count(*) FROM public.auth_audit_logs
       WHERE event_type = 'LOGIN_SUCCESS' AND created_at >= d0 AND created_at < d1),
    (SELECT count(*) FROM public.auth_audit_logs
       WHERE event_type = 'LOGIN_FAILED'  AND created_at >= d0 AND created_at < d1),
    live, now()
  ON CONFLICT (day) DO UPDATE SET
    total_users = excluded.total_users, new_signups = excluded.new_signups,
    dau = excluded.dau, returning_users = excluded.returning_users,
    successful_logins = excluded.successful_logins, failed_logins = excluded.failed_logins,
    peak_concurrent = greatest(r.peak_concurrent, excluded.peak_concurrent),
    updated_at = now();
END $$;
REVOKE EXECUTE ON FUNCTION public.refresh_daily_metrics(DATE) FROM public, anon, authenticated;

-- ---------- AUTHZ HELPERS ----------------------------------------------------
CREATE OR REPLACE FUNCTION public.is_session_live() RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT NOT EXISTS (
    SELECT 1 FROM public.user_sessions s
    WHERE s.session_token_hash = encode(extensions.digest(coalesce(auth.jwt() ->> 'session_id', ''), 'sha256'), 'hex')
      AND s.is_revoked
  );
$$;

CREATE OR REPLACE FUNCTION public.is_owner() RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles p
    WHERE p.id = auth.uid() AND p.role = 'owner' AND p.status = 'active'
  ) AND public.is_session_live();
$$;

-- ---------- RLS --------------------------------------------------------------
ALTER TABLE public.profiles             ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.auth_audit_logs      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_metrics_rollup ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.profiles, public.user_sessions, public.auth_audit_logs,
              public.daily_metrics_rollup FROM anon, authenticated;
GRANT SELECT ON public.profiles, public.user_sessions, public.auth_audit_logs,
                public.daily_metrics_rollup TO authenticated;
GRANT UPDATE (display_name) ON public.profiles TO authenticated;

DROP POLICY IF EXISTS profiles_select ON public.profiles;
CREATE POLICY profiles_select ON public.profiles FOR SELECT TO authenticated
  USING (id = auth.uid() OR public.is_owner());

DROP POLICY IF EXISTS profiles_update_self ON public.profiles;
CREATE POLICY profiles_update_self ON public.profiles FOR UPDATE TO authenticated
  USING (id = auth.uid()) WITH CHECK (id = auth.uid());

DROP POLICY IF EXISTS sessions_owner_select ON public.user_sessions;
CREATE POLICY sessions_owner_select ON public.user_sessions FOR SELECT TO authenticated
  USING (public.is_owner());

DROP POLICY IF EXISTS audit_owner_select ON public.auth_audit_logs;
CREATE POLICY audit_owner_select ON public.auth_audit_logs FOR SELECT TO authenticated
  USING (public.is_owner());

DROP POLICY IF EXISTS rollup_owner_select ON public.daily_metrics_rollup;
CREATE POLICY rollup_owner_select ON public.daily_metrics_rollup FOR SELECT TO authenticated
  USING (public.is_owner());

-- ---------- SERVER-SIDE RECORDING (service_role only) ------------------------
CREATE OR REPLACE FUNCTION public.is_login_blocked(p_email TEXT, p_ip_hash TEXT) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = '' AS $$
  SELECT EXISTS (SELECT 1 FROM public.profiles
                  WHERE email = lower(p_email) AND (locked_until > now() OR status = 'suspended'))
      OR (SELECT count(*) FROM public.auth_audit_logs
           WHERE event_type = 'LOGIN_FAILED' AND ip_hash = p_ip_hash
             AND created_at > now() - interval '15 minutes') >= 20;
$$;

CREATE OR REPLACE FUNCTION public.record_login_failure(
  p_email TEXT, p_ip INET, p_ip_hash TEXT, p_identifier_hash TEXT,
  p_country TEXT, p_ua TEXT
) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE v_uid uuid; v_count int;
BEGIN
  SELECT id INTO v_uid FROM public.profiles WHERE email = lower(p_email);
  INSERT INTO public.auth_audit_logs
    (user_id, event_type, identifier_hash, ip_address, ip_hash, country_code, user_agent)
  VALUES (v_uid, 'LOGIN_FAILED', p_identifier_hash, p_ip, p_ip_hash, p_country, left(p_ua, 512));

  IF v_uid IS NOT NULL THEN
    UPDATE public.profiles
       SET failed_login_count = failed_login_count + 1,
           locked_until = CASE WHEN failed_login_count + 1 >= 5
                               THEN now() + interval '15 minutes' ELSE locked_until END
     WHERE id = v_uid
     RETURNING failed_login_count INTO v_count;
    IF v_count = 5 THEN
      INSERT INTO public.auth_audit_logs (user_id, event_type, ip_hash, metadata)
      VALUES (v_uid, 'ACCOUNT_LOCKED', p_ip_hash, jsonb_build_object('minutes', 15));
    END IF;
  END IF;
END $$;

CREATE OR REPLACE FUNCTION public.record_login_success(
  p_user_id UUID, p_auth_session_id TEXT, p_ip INET, p_ip_hash TEXT,
  p_country TEXT, p_ua TEXT, p_device JSONB
) RETURNS uuid LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE v_sid uuid; v_hash text := encode(extensions.digest(p_auth_session_id, 'sha256'), 'hex');
BEGIN
  INSERT INTO public.user_sessions
    (user_id, session_token_hash, ip_address, ip_hash, country_code, user_agent, device_info)
  VALUES (p_user_id, v_hash, p_ip, p_ip_hash, p_country, left(p_ua, 512), coalesce(p_device, '{}'))
  ON CONFLICT (session_token_hash) DO UPDATE SET last_active_at = now()
  RETURNING id INTO v_sid;

  UPDATE public.profiles
     SET failed_login_count = 0, locked_until = null, last_seen_at = now()
   WHERE id = p_user_id;

  INSERT INTO public.auth_audit_logs
    (user_id, event_type, ip_address, ip_hash, country_code, user_agent, metadata)
  VALUES (p_user_id, 'LOGIN_SUCCESS', p_ip, p_ip_hash, p_country, left(p_ua, 512),
          jsonb_build_object('session_id', v_sid, 'device', p_device));
  RETURN v_sid;
END $$;

CREATE OR REPLACE FUNCTION public.record_logout(p_auth_session_id TEXT, p_reason TEXT DEFAULT 'logout')
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE v_hash text := encode(extensions.digest(p_auth_session_id, 'sha256'), 'hex'); s public.user_sessions;
BEGIN
  UPDATE public.user_sessions
     SET ended_at = now(), end_reason = p_reason
   WHERE session_token_hash = v_hash AND ended_at IS NULL
   RETURNING * INTO s;
  IF s.id IS NOT NULL THEN
    INSERT INTO public.auth_audit_logs (user_id, event_type, ip_hash, metadata)
    VALUES (s.user_id, 'LOGOUT', s.ip_hash, jsonb_build_object('session_id', s.id, 'reason', p_reason));
  END IF;
END $$;

REVOKE EXECUTE ON FUNCTION
  public.is_login_blocked(TEXT, TEXT),
  public.record_login_failure(TEXT, INET, TEXT, TEXT, TEXT, TEXT),
  public.record_login_success(UUID, TEXT, INET, TEXT, TEXT, TEXT, JSONB),
  public.record_logout(TEXT, TEXT)
FROM public, anon, authenticated;
GRANT EXECUTE ON FUNCTION
  public.is_login_blocked(TEXT, TEXT),
  public.record_login_failure(TEXT, INET, TEXT, TEXT, TEXT, TEXT),
  public.record_login_success(UUID, TEXT, INET, TEXT, TEXT, TEXT, JSONB),
  public.record_logout(TEXT, TEXT)
TO service_role;

-- ---------- HEARTBEAT + ZOMBIE SWEEP -----------------------------------------
CREATE OR REPLACE FUNCTION public.session_heartbeat() RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE v_hash text := encode(extensions.digest(coalesce(auth.jwt() ->> 'session_id', ''), 'sha256'), 'hex');
        v_ok boolean;
BEGIN
  IF auth.uid() IS NULL THEN RETURN false; END IF;
  UPDATE public.user_sessions
     SET last_active_at = now(), ended_at = null, end_reason = null
   WHERE session_token_hash = v_hash AND user_id = auth.uid() AND NOT is_revoked
     AND (ended_at IS NULL OR end_reason = 'timeout')
     AND last_active_at < now() - interval '45 seconds';
  UPDATE public.profiles SET last_seen_at = now()
   WHERE id = auth.uid() AND (last_seen_at IS NULL OR last_seen_at < now() - interval '5 minutes');
  SELECT EXISTS (SELECT 1 FROM public.user_sessions
                  WHERE session_token_hash = v_hash AND user_id = auth.uid()
                    AND NOT is_revoked AND ended_at IS NULL) INTO v_ok;
  RETURN v_ok;
END $$;
REVOKE EXECUTE ON FUNCTION public.session_heartbeat() FROM public, anon;
GRANT  EXECUTE ON FUNCTION public.session_heartbeat() TO authenticated;

CREATE OR REPLACE FUNCTION public.close_zombie_sessions(p_ttl interval DEFAULT interval '5 minutes')
RETURNS int LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE n int;
BEGIN
  WITH dead AS (
    UPDATE public.user_sessions
       SET ended_at = last_active_at, end_reason = 'timeout'
     WHERE ended_at IS NULL AND NOT is_revoked AND last_active_at < now() - p_ttl
     RETURNING id, user_id, ip_hash, last_active_at
  ), logged AS (
    INSERT INTO public.auth_audit_logs (user_id, event_type, ip_hash, metadata)
    SELECT user_id, 'LOGOUT', ip_hash,
           jsonb_build_object('session_id', id, 'reason', 'timeout', 'last_active_at', last_active_at)
    FROM dead RETURNING 1
  )
  SELECT count(*) INTO n FROM dead;
  RETURN n;
END $$;
REVOKE EXECUTE ON FUNCTION public.close_zombie_sessions(interval) FROM public, anon, authenticated;

-- ---------- OWNER-ONLY CONTROLS ----------------------------------------------
CREATE OR REPLACE FUNCTION public.owner_kpis() RETURNS jsonb
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = '' AS $$
DECLARE t public.daily_metrics_rollup;
BEGIN
  IF NOT public.is_owner() THEN RAISE EXCEPTION 'forbidden' USING errcode = '42501'; END IF;
  SELECT * INTO t FROM public.daily_metrics_rollup ORDER BY day DESC LIMIT 1;
  RETURN jsonb_build_object(
    'total_users',       coalesce(t.total_users, 0),
    'new_signups_today', coalesce(t.new_signups, 0),
    'dau',               coalesce(t.dau, 0),
    'returning_users',   coalesce(t.returning_users, 0),
    'peak_concurrent',   coalesce(t.peak_concurrent, 0),
    'active_now', (SELECT count(*) FROM public.user_sessions
                    WHERE ended_at IS NULL AND NOT is_revoked
                      AND last_active_at > now() - interval '5 minutes'),
    'failed_24h', (SELECT count(*) FROM public.auth_audit_logs
                    WHERE event_type = 'LOGIN_FAILED' AND created_at >= now() - interval '24 hours'),
    'rollup_updated_at', t.updated_at);
END $$;

CREATE OR REPLACE FUNCTION public.owner_list_audit_logs(
  p_limit INT DEFAULT 51,
  p_cursor_ts TIMESTAMPTZ DEFAULT null,
  p_cursor_id UUID DEFAULT null,
  p_event_types public.audit_event_type[] DEFAULT null,
  p_user_id UUID DEFAULT null,
  p_from TIMESTAMPTZ DEFAULT null,
  p_to TIMESTAMPTZ DEFAULT null,
  p_search TEXT DEFAULT null
) RETURNS TABLE (
  id uuid, created_at timestamptz, user_id uuid, email text,
  event_type public.audit_event_type, ip_address inet, country_code char(2),
  user_agent text, metadata jsonb
) LANGUAGE sql STABLE SET search_path = '' AS $$
  SELECT l.id, l.created_at, l.user_id, p.email, l.event_type, l.ip_address,
         l.country_code, l.user_agent, l.metadata
  FROM public.auth_audit_logs l
  LEFT JOIN public.profiles p ON p.id = l.user_id
  WHERE (p_cursor_ts IS NULL OR (l.created_at, l.id) < (p_cursor_ts, p_cursor_id))
    AND (p_event_types IS NULL OR l.event_type = ANY (p_event_types))
    AND (p_user_id IS NULL OR l.user_id = p_user_id)
    AND (p_from IS NULL OR l.created_at >= p_from)
    AND (p_to   IS NULL OR l.created_at <  p_to)
    AND (p_search IS NULL OR p.email LIKE
         replace(replace(replace(lower(p_search), '\', '\\'), '%', '\%'), '_', '\_') || '%')
  ORDER BY l.created_at DESC, l.id DESC
  LIMIT least(greatest(p_limit, 1), 201);
$$;

CREATE OR REPLACE FUNCTION public.owner_revoke_user_sessions(p_user_id UUID, p_reason TEXT DEFAULT null)
RETURNS int LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
DECLARE n int;
BEGIN
  IF NOT public.is_owner() THEN RAISE EXCEPTION 'forbidden' USING errcode = '42501'; END IF;
  IF p_user_id = auth.uid() THEN RAISE EXCEPTION 'cannot revoke own sessions here' USING errcode = '22023'; END IF;

  UPDATE public.user_sessions
     SET is_revoked = true, ended_at = coalesce(ended_at, now()), end_reason = 'revoked'
   WHERE user_id = p_user_id AND (ended_at IS NULL OR NOT is_revoked);
  GET DIAGNOSTICS n = row_count;

  -- Kill refresh tokens
  BEGIN
    DELETE FROM auth.sessions WHERE user_id = p_user_id;
  EXCEPTION WHEN others THEN NULL; END;

  INSERT INTO public.auth_audit_logs (user_id, actor_id, event_type, metadata)
  VALUES (p_user_id, auth.uid(), 'SESSION_REVOKED',
          jsonb_build_object('count', n, 'reason', left(coalesce(p_reason, ''), 200)));
  RETURN n;
END $$;

CREATE OR REPLACE FUNCTION public.owner_set_status(p_user_id UUID, p_status public.user_status)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  IF NOT public.is_owner() THEN RAISE EXCEPTION 'forbidden' USING errcode = '42501'; END IF;
  IF p_user_id = auth.uid() THEN RAISE EXCEPTION 'cannot change own status' USING errcode = '22023'; END IF;
  UPDATE public.profiles SET status = p_status,
         locked_until = CASE WHEN p_status = 'active' THEN null ELSE locked_until END,
         failed_login_count = CASE WHEN p_status = 'active' THEN 0 ELSE failed_login_count END
   WHERE id = p_user_id;
  INSERT INTO public.auth_audit_logs (user_id, actor_id, event_type, metadata)
  VALUES (p_user_id, auth.uid(), 'STATUS_CHANGED', jsonb_build_object('status', p_status));
  IF p_status = 'suspended' THEN
    PERFORM public.owner_revoke_user_sessions(p_user_id, 'account suspended');
  END IF;
END $$;

CREATE OR REPLACE FUNCTION public.owner_set_role(p_user_id UUID, p_role public.user_role)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  IF NOT public.is_owner() THEN RAISE EXCEPTION 'forbidden' USING errcode = '42501'; END IF;
  IF p_user_id = auth.uid() THEN RAISE EXCEPTION 'cannot change own role' USING errcode = '22023'; END IF;
  IF p_role = 'owner' THEN RAISE EXCEPTION 'ownership transfer is an out-of-band operation' USING errcode = '22023'; END IF;
  UPDATE public.profiles SET role = p_role WHERE id = p_user_id;
  INSERT INTO public.auth_audit_logs (user_id, actor_id, event_type, metadata)
  VALUES (p_user_id, auth.uid(), 'ROLE_CHANGED', jsonb_build_object('role', p_role));
END $$;

CREATE OR REPLACE FUNCTION public.owner_unlock_user(p_user_id UUID) RETURNS void
LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
  IF NOT public.is_owner() THEN RAISE EXCEPTION 'forbidden' USING errcode = '42501'; END IF;
  UPDATE public.profiles SET locked_until = null, failed_login_count = 0 WHERE id = p_user_id;
  INSERT INTO public.auth_audit_logs (user_id, actor_id, event_type)
  VALUES (p_user_id, auth.uid(), 'ACCOUNT_UNLOCKED');
END $$;

REVOKE EXECUTE ON FUNCTION
  public.owner_kpis(),
  public.owner_list_audit_logs(INT, TIMESTAMPTZ, UUID, public.audit_event_type[], UUID, TIMESTAMPTZ, TIMESTAMPTZ, TEXT),
  public.owner_revoke_user_sessions(UUID, TEXT),
  public.owner_set_status(UUID, public.user_status),
  public.owner_set_role(UUID, public.user_role),
  public.owner_unlock_user(UUID)
FROM public, anon;

GRANT EXECUTE ON FUNCTION
  public.owner_kpis(),
  public.owner_list_audit_logs(INT, TIMESTAMPTZ, UUID, public.audit_event_type[], UUID, TIMESTAMPTZ, TIMESTAMPTZ, TEXT),
  public.owner_revoke_user_sessions(UUID, TEXT),
  public.owner_set_status(UUID, public.user_status),
  public.owner_set_role(UUID, public.user_role),
  public.owner_unlock_user(UUID)
TO authenticated;

-- ---------- REALTIME ---------------------------------------------------------
DO $$ BEGIN
  ALTER PUBLICATION supabase_realtime ADD TABLE public.auth_audit_logs;
  ALTER PUBLICATION supabase_realtime SET (publish_via_partition_root = true);
EXCEPTION WHEN others THEN NULL; END $$;

COMMIT;
