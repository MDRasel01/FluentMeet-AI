-- =============================================================================
-- FluentMeet AI  |  Founder Workbench: User Management, Sessions, Audit Trail
-- Target: Supabase (PostgreSQL 15+). Test on staging and take a backup first.
-- =============================================================================
begin;

create extension if not exists pgcrypto with schema extensions;

-- ---------- ENUMS ------------------------------------------------------------
create type public.user_role   as enum ('owner', 'admin', 'member');
create type public.user_status as enum ('active', 'suspended');
create type public.audit_event_type as enum (
  'LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGOUT', 'SESSION_REVOKED', 'PASSWORD_CHANGED',
  -- admin-action events (extra to the 5 core types)
  'ACCOUNT_LOCKED', 'ACCOUNT_UNLOCKED', 'ROLE_CHANGED', 'STATUS_CHANGED'
);

-- ---------- PROFILES ---------------------------------------------------------
create table public.profiles (
  id                  uuid primary key references auth.users(id) on delete cascade,
  email               text not null,
  display_name        text,
  role                public.user_role   not null default 'member',
  status              public.user_status not null default 'active',
  failed_login_count  int  not null default 0 check (failed_login_count >= 0),
  locked_until        timestamptz,
  last_seen_at        timestamptz,
  created_at          timestamptz not null default now(),
  constraint profiles_email_lowercase check (email = lower(email))
);
create unique index profiles_email_key    on public.profiles (email);
-- Exactly ONE owner can ever exist.
create unique index profiles_single_owner on public.profiles (role) where role = 'owner';
create index profiles_created_at_idx      on public.profiles (created_at);

-- Every new auth user gets a 'member' profile. Role is never read from client input.
create function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  insert into public.profiles (id, email) values (new.id, lower(new.email));
  return new;
end $$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- USER SESSIONS ----------------------------------------------------
create table public.user_sessions (
  id                  uuid primary key default gen_random_uuid(),
  user_id             uuid not null references public.profiles(id) on delete cascade,
  session_token_hash  text not null,             -- sha256(auth session_id claim); never the token itself
  ip_address          inet,                      -- MASKED (/24 v4, /48 v6) by the Edge Function
  ip_hash             text,                      -- HMAC(ip, pepper) for correlation without storing the IP
  country_code        char(2),
  user_agent          text,
  device_info         jsonb not null default '{}'::jsonb,
  started_at          timestamptz not null default now(),
  last_active_at      timestamptz not null default now(),
  ended_at            timestamptz,
  end_reason          text check (end_reason in ('logout', 'timeout', 'revoked', 'suspended')),
  is_revoked          boolean not null default false,
  constraint sessions_time_order check (ended_at is null or ended_at >= started_at)
);
create unique index user_sessions_token_hash_key on public.user_sessions (session_token_hash);
create index user_sessions_user_started_idx      on public.user_sessions (user_id, started_at desc);
-- Partial index: only live sessions (tiny, hot).
create index user_sessions_live_idx on public.user_sessions (last_active_at)
  where is_revoked = false and ended_at is null;

-- ---------- AUDIT LOG (partitioned, append-only) ------------------------------
create table public.auth_audit_logs (
  id               uuid not null default gen_random_uuid(),
  created_at       timestamptz not null default now(),
  user_id          uuid,
  actor_id         uuid,                         -- who performed an admin action
  event_type       public.audit_event_type not null,
  identifier_hash  text,                         -- HMAC(email) for failed logins on unknown accounts
  ip_address       inet,
  ip_hash          text,
  country_code     char(2),
  user_agent       text,
  metadata         jsonb not null default '{}'::jsonb,
  primary key (id, created_at)
) partition by range (created_at);

create table public.auth_audit_logs_default partition of public.auth_audit_logs default;

create or replace function public.ensure_audit_partitions(p_months_ahead int default 2)
returns void language plpgsql security definer set search_path = '' as $$
declare m date;
begin
  for i in 0 .. p_months_ahead loop
    m := (date_trunc('month', now() at time zone 'utc') + make_interval(months => i))::date;
    execute format(
      'create table if not exists public.auth_audit_logs_%s partition of public.auth_audit_logs
         for values from (%L) to (%L)',
      to_char(m, 'YYYY_MM'),
      (m::timestamp at time zone 'utc'),
      ((m + interval '1 month')::timestamp at time zone 'utc'));
  end loop;
end $$;
select public.ensure_audit_partitions(2);

-- Indexes (created on the parent, propagate to every partition)
create index audit_user_created_idx   on public.auth_audit_logs (user_id, created_at desc);
create index audit_keyset_idx         on public.auth_audit_logs (created_at desc, id desc);
create index audit_event_created_idx  on public.auth_audit_logs (event_type, created_at desc);
create index audit_created_brin       on public.auth_audit_logs using brin (created_at);
create index audit_failed_ip_idx      on public.auth_audit_logs (ip_hash, created_at desc)
  where event_type = 'LOGIN_FAILED';

-- Immutability: block UPDATE/DELETE for everyone; only the GDPR erasure function may UPDATE.
create function public.audit_block_mutation() returns trigger
language plpgsql as $$
begin
  if tg_op = 'UPDATE' and current_setting('app.gdpr_erasure', true) = 'on' then
    return new;
  end if;
  raise exception 'auth_audit_logs is append-only' using errcode = '42501';
end $$;
create trigger audit_no_update_delete before update or delete on public.auth_audit_logs
  for each row execute function public.audit_block_mutation();
revoke update, delete, truncate on public.auth_audit_logs
  from public, anon, authenticated, service_role;

-- GDPR erasure: strips PII, keeps the event skeleton for integrity/statistics.
create function public.erase_user_audit_pii(p_user_id uuid) returns bigint
language plpgsql security definer set search_path = '' as $$
declare n bigint;
begin
  perform set_config('app.gdpr_erasure', 'on', true);          -- transaction-local
  update public.auth_audit_logs
     set ip_address = null, ip_hash = null, user_agent = null, identifier_hash = null,
         metadata = '{}'::jsonb, user_id = null
   where user_id = p_user_id;
  get diagnostics n = row_count;
  return n;
end $$;
revoke execute on function public.erase_user_audit_pii(uuid) from public, anon, authenticated;
grant  execute on function public.erase_user_audit_pii(uuid) to service_role;

-- ---------- DAILY ROLLUP -----------------------------------------------------
create table public.daily_metrics_rollup (
  day                date primary key,
  total_users        int not null default 0,
  new_signups        int not null default 0,
  dau                int not null default 0,
  returning_users    int not null default 0,
  successful_logins  int not null default 0,
  failed_logins      int not null default 0,
  peak_concurrent    int not null default 0,
  updated_at         timestamptz not null default now()
);

create or replace function public.refresh_daily_metrics(
  p_day date default (now() at time zone 'utc')::date
) returns void language plpgsql security definer set search_path = '' as $$
declare
  d0 timestamptz := (p_day::timestamp at time zone 'utc');
  d1 timestamptz := d0 + interval '1 day';
  live int;
begin
  select count(*) into live from public.user_sessions
   where ended_at is null and not is_revoked and last_active_at > now() - interval '5 minutes';

  insert into public.daily_metrics_rollup as r
    (day, total_users, new_signups, dau, returning_users, successful_logins, failed_logins,
     peak_concurrent, updated_at)
  select p_day,
    (select count(*) from public.profiles where created_at < d1),
    (select count(*) from public.profiles where created_at >= d0 and created_at < d1),
    (select count(distinct user_id) from public.user_sessions
       where started_at < d1 and last_active_at >= d0),
    (select count(distinct s.user_id) from public.user_sessions s
       join public.profiles p on p.id = s.user_id
       where s.started_at < d1 and s.last_active_at >= d0 and p.created_at < d0),
    (select count(*) from public.auth_audit_logs
       where event_type = 'LOGIN_SUCCESS' and created_at >= d0 and created_at < d1),
    (select count(*) from public.auth_audit_logs
       where event_type = 'LOGIN_FAILED'  and created_at >= d0 and created_at < d1),
    live, now()
  on conflict (day) do update set
    total_users = excluded.total_users, new_signups = excluded.new_signups,
    dau = excluded.dau, returning_users = excluded.returning_users,
    successful_logins = excluded.successful_logins, failed_logins = excluded.failed_logins,
    peak_concurrent = greatest(r.peak_concurrent, excluded.peak_concurrent),
    updated_at = now();
end $$;
revoke execute on function public.refresh_daily_metrics(date) from public, anon, authenticated;

-- ---------- AUTHZ HELPERS ----------------------------------------------------
create function public.is_session_live() returns boolean
language sql stable security definer set search_path = '' as $$
  select not exists (
    select 1 from public.user_sessions s
    where s.session_token_hash = encode(extensions.digest(coalesce(auth.jwt() ->> 'session_id', ''), 'sha256'), 'hex')
      and s.is_revoked
  );
$$;

create function public.is_owner() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.profiles p
    where p.id = auth.uid() and p.role = 'owner' and p.status = 'active'
  ) and public.is_session_live();
$$;

-- ---------- RLS --------------------------------------------------------------
alter table public.profiles             enable row level security;
alter table public.user_sessions        enable row level security;
alter table public.auth_audit_logs      enable row level security;
alter table public.daily_metrics_rollup enable row level security;

revoke all on public.profiles, public.user_sessions, public.auth_audit_logs,
              public.daily_metrics_rollup from anon, authenticated;
grant select on public.profiles, public.user_sessions, public.auth_audit_logs,
                public.daily_metrics_rollup to authenticated;
grant update (display_name) on public.profiles to authenticated;

create policy profiles_select on public.profiles for select to authenticated
  using (id = auth.uid() or public.is_owner());
create policy profiles_update_self on public.profiles for update to authenticated
  using (id = auth.uid()) with check (id = auth.uid());
create policy sessions_owner_select on public.user_sessions for select to authenticated
  using (public.is_owner());
create policy audit_owner_select on public.auth_audit_logs for select to authenticated
  using (public.is_owner());
create policy rollup_owner_select on public.daily_metrics_rollup for select to authenticated
  using (public.is_owner());

-- ---------- SERVER-SIDE RECORDING (service_role only) ------------------------
create function public.is_login_blocked(p_email text, p_ip_hash text) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.profiles
                  where email = lower(p_email) and (locked_until > now() or status = 'suspended'))
      or (select count(*) from public.auth_audit_logs
           where event_type = 'LOGIN_FAILED' and ip_hash = p_ip_hash
             and created_at > now() - interval '15 minutes') >= 20;
$$;

create function public.record_login_failure(
  p_email text, p_ip inet, p_ip_hash text, p_identifier_hash text,
  p_country text, p_ua text
) returns void language plpgsql security definer set search_path = '' as $$
declare v_uid uuid; v_count int;
begin
  select id into v_uid from public.profiles where email = lower(p_email);
  insert into public.auth_audit_logs
    (user_id, event_type, identifier_hash, ip_address, ip_hash, country_code, user_agent)
  values (v_uid, 'LOGIN_FAILED', p_identifier_hash, p_ip, p_ip_hash, p_country, left(p_ua, 512));

  if v_uid is not null then
    update public.profiles
       set failed_login_count = failed_login_count + 1,
           locked_until = case when failed_login_count + 1 >= 5
                               then now() + interval '15 minutes' else locked_until end
     where id = v_uid
     returning failed_login_count into v_count;
    if v_count = 5 then
      insert into public.auth_audit_logs (user_id, event_type, ip_hash, metadata)
      values (v_uid, 'ACCOUNT_LOCKED', p_ip_hash, jsonb_build_object('minutes', 15));
    end if;
  end if;
end $$;

create function public.record_login_success(
  p_user_id uuid, p_auth_session_id text, p_ip inet, p_ip_hash text,
  p_country text, p_ua text, p_device jsonb
) returns uuid language plpgsql security definer set search_path = '' as $$
declare v_sid uuid; v_hash text := encode(extensions.digest(p_auth_session_id, 'sha256'), 'hex');
begin
  insert into public.user_sessions
    (user_id, session_token_hash, ip_address, ip_hash, country_code, user_agent, device_info)
  values (p_user_id, v_hash, p_ip, p_ip_hash, p_country, left(p_ua, 512), coalesce(p_device, '{}'))
  on conflict (session_token_hash) do update set last_active_at = now()
  returning id into v_sid;

  update public.profiles
     set failed_login_count = 0, locked_until = null, last_seen_at = now()
   where id = p_user_id;

  insert into public.auth_audit_logs
    (user_id, event_type, ip_address, ip_hash, country_code, user_agent, metadata)
  values (p_user_id, 'LOGIN_SUCCESS', p_ip, p_ip_hash, p_country, left(p_ua, 512),
          jsonb_build_object('session_id', v_sid, 'device', p_device));
  return v_sid;
end $$;

create function public.record_logout(p_auth_session_id text, p_reason text default 'logout')
returns void language plpgsql security definer set search_path = '' as $$
declare v_hash text := encode(extensions.digest(p_auth_session_id, 'sha256'), 'hex'); s public.user_sessions;
begin
  update public.user_sessions
     set ended_at = now(), end_reason = p_reason
   where session_token_hash = v_hash and ended_at is null
   returning * into s;
  if s.id is not null then
    insert into public.auth_audit_logs (user_id, event_type, ip_hash, metadata)
    values (s.user_id, 'LOGOUT', s.ip_hash, jsonb_build_object('session_id', s.id, 'reason', p_reason));
  end if;
end $$;

revoke execute on function
  public.is_login_blocked(text, text),
  public.record_login_failure(text, inet, text, text, text, text),
  public.record_login_success(uuid, text, inet, text, text, text, jsonb),
  public.record_logout(text, text)
from public, anon, authenticated;
grant execute on function
  public.is_login_blocked(text, text),
  public.record_login_failure(text, inet, text, text, text, text),
  public.record_login_success(uuid, text, inet, text, text, text, jsonb),
  public.record_logout(text, text)
to service_role;

-- ---------- HEARTBEAT + ZOMBIE SWEEP -----------------------------------------
create function public.session_heartbeat() returns boolean
language plpgsql security definer set search_path = '' as $$
declare v_hash text := encode(extensions.digest(coalesce(auth.jwt() ->> 'session_id', ''), 'sha256'), 'hex');
        v_ok boolean;
begin
  if auth.uid() is null then return false; end if;
  update public.user_sessions
     set last_active_at = now(), ended_at = null, end_reason = null
   where session_token_hash = v_hash and user_id = auth.uid() and not is_revoked
     and (ended_at is null or end_reason = 'timeout')
     and last_active_at < now() - interval '45 seconds';
  update public.profiles set last_seen_at = now()
   where id = auth.uid() and (last_seen_at is null or last_seen_at < now() - interval '5 minutes');
  select exists (select 1 from public.user_sessions
                  where session_token_hash = v_hash and user_id = auth.uid()
                    and not is_revoked and ended_at is null) into v_ok;
  return v_ok;
end $$;
revoke execute on function public.session_heartbeat() from public, anon;
grant  execute on function public.session_heartbeat() to authenticated;

create or replace function public.close_zombie_sessions(p_ttl interval default interval '5 minutes')
returns int language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  with dead as (
    update public.user_sessions
       set ended_at = last_active_at, end_reason = 'timeout'
     where ended_at is null and not is_revoked and last_active_at < now() - p_ttl
     returning id, user_id, ip_hash, last_active_at
  ), logged as (
    insert into public.auth_audit_logs (user_id, event_type, ip_hash, metadata)
    select user_id, 'LOGOUT', ip_hash,
           jsonb_build_object('session_id', id, 'reason', 'timeout', 'last_active_at', last_active_at)
    from dead returning 1
  )
  select count(*) into n from dead;
  return n;
end $$;
revoke execute on function public.close_zombie_sessions(interval) from public, anon, authenticated;

-- ---------- OWNER-ONLY CONTROLS ----------------------------------------------
create function public.owner_kpis() returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare t public.daily_metrics_rollup;
begin
  if not public.is_owner() then raise exception 'forbidden' using errcode = '42501'; end if;
  select * into t from public.daily_metrics_rollup order by day desc limit 1;
  return jsonb_build_object(
    'total_users',       coalesce(t.total_users, 0),
    'new_signups_today', coalesce(t.new_signups, 0),
    'dau',               coalesce(t.dau, 0),
    'returning_users',   coalesce(t.returning_users, 0),
    'peak_concurrent',   coalesce(t.peak_concurrent, 0),
    'active_now', (select count(*) from public.user_sessions
                    where ended_at is null and not is_revoked
                      and last_active_at > now() - interval '5 minutes'),
    'failed_24h', (select count(*) from public.auth_audit_logs
                    where event_type = 'LOGIN_FAILED' and created_at >= now() - interval '24 hours'),
    'rollup_updated_at', t.updated_at);
end $$;

create function public.owner_list_audit_logs(
  p_limit int default 51,
  p_cursor_ts timestamptz default null,
  p_cursor_id uuid default null,
  p_event_types public.audit_event_type[] default null,
  p_user_id uuid default null,
  p_from timestamptz default null,
  p_to timestamptz default null,
  p_search text default null
) returns table (
  id uuid, created_at timestamptz, user_id uuid, email text,
  event_type public.audit_event_type, ip_address inet, country_code char(2),
  user_agent text, metadata jsonb
) language sql stable set search_path = '' as $$
  select l.id, l.created_at, l.user_id, p.email, l.event_type, l.ip_address,
         l.country_code, l.user_agent, l.metadata
  from public.auth_audit_logs l
  left join public.profiles p on p.id = l.user_id
  where (p_cursor_ts is null or (l.created_at, l.id) < (p_cursor_ts, p_cursor_id))
    and (p_event_types is null or l.event_type = any (p_event_types))
    and (p_user_id is null or l.user_id = p_user_id)
    and (p_from is null or l.created_at >= p_from)
    and (p_to   is null or l.created_at <  p_to)
    and (p_search is null or p.email like
         replace(replace(replace(lower(p_search), '\', '\\'), '%', '\%'), '_', '\_') || '%')
  order by l.created_at desc, l.id desc
  limit least(greatest(p_limit, 1), 201);
$$;

create function public.owner_revoke_user_sessions(p_user_id uuid, p_reason text default null)
returns int language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  if not public.is_owner() then raise exception 'forbidden' using errcode = '42501'; end if;
  if p_user_id = auth.uid() then raise exception 'cannot revoke own sessions here' using errcode = '22023'; end if;

  update public.user_sessions
     set is_revoked = true, ended_at = coalesce(ended_at, now()), end_reason = 'revoked'
   where user_id = p_user_id and (ended_at is null or not is_revoked);
  get diagnostics n = row_count;

  delete from auth.sessions where user_id = p_user_id;

  insert into public.auth_audit_logs (user_id, actor_id, event_type, metadata)
  values (p_user_id, auth.uid(), 'SESSION_REVOKED',
          jsonb_build_object('count', n, 'reason', left(coalesce(p_reason, ''), 200)));
  return n;
end $$;

create function public.owner_set_status(p_user_id uuid, p_status public.user_status)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_owner() then raise exception 'forbidden' using errcode = '42501'; end if;
  if p_user_id = auth.uid() then raise exception 'cannot change own status' using errcode = '22023'; end if;
  update public.profiles set status = p_status,
         locked_until = case when p_status = 'active' then null else locked_until end,
         failed_login_count = case when p_status = 'active' then 0 else failed_login_count end
   where id = p_user_id;
  insert into public.auth_audit_logs (user_id, actor_id, event_type, metadata)
  values (p_user_id, auth.uid(), 'STATUS_CHANGED', jsonb_build_object('status', p_status));
  if p_status = 'suspended' then
    perform public.owner_revoke_user_sessions(p_user_id, 'account suspended');
  end if;
end $$;

create function public.owner_set_role(p_user_id uuid, p_role public.user_role)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_owner() then raise exception 'forbidden' using errcode = '42501'; end if;
  if p_user_id = auth.uid() then raise exception 'cannot change own role' using errcode = '22023'; end if;
  if p_role = 'owner' then raise exception 'ownership transfer is an out-of-band operation' using errcode = '22023'; end if;
  update public.profiles set role = p_role where id = p_user_id;
  insert into public.auth_audit_logs (user_id, actor_id, event_type, metadata)
  values (p_user_id, auth.uid(), 'ROLE_CHANGED', jsonb_build_object('role', p_role));
end $$;

create function public.owner_unlock_user(p_user_id uuid) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_owner() then raise exception 'forbidden' using errcode = '42501'; end if;
  update public.profiles set locked_until = null, failed_login_count = 0 where id = p_user_id;
  insert into public.auth_audit_logs (user_id, actor_id, event_type)
  values (p_user_id, auth.uid(), 'ACCOUNT_UNLOCKED');
end $$;

revoke execute on function
  public.owner_kpis(),
  public.owner_list_audit_logs(int, timestamptz, uuid, public.audit_event_type[], uuid, timestamptz, timestamptz, text),
  public.owner_revoke_user_sessions(uuid, text),
  public.owner_set_status(uuid, public.user_status),
  public.owner_set_role(uuid, public.user_role),
  public.owner_unlock_user(uuid)
from public, anon;
grant execute on function
  public.owner_kpis(),
  public.owner_list_audit_logs(int, timestamptz, uuid, public.audit_event_type[], uuid, timestamptz, timestamptz, text),
  public.owner_revoke_user_sessions(uuid, text),
  public.owner_set_status(uuid, public.user_status),
  public.owner_set_role(uuid, public.user_role),
  public.owner_unlock_user(uuid)
to authenticated;

-- ---------- REALTIME ---------------------------------------------------------
alter publication supabase_realtime add table public.auth_audit_logs;
alter publication supabase_realtime set (publish_via_partition_root = true);

commit;
