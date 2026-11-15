// supabase/functions/auth-gateway/index.ts
// Server-side login/logout/heartbeat gateway. The browser NEVER writes audit rows or
// session rows itself; IP and User-Agent are read from request headers here.
//
// Secrets (supabase secrets set ...): IP_HASH_PEPPER (random 32+ bytes), ALLOWED_ORIGIN
// Built-ins: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
import { createClient } from 'npm:@supabase/supabase-js@2'

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const ANON_KEY = Deno.env.get('SUPABASE_ANON_KEY')!
const SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const PEPPER = Deno.env.get('IP_HASH_PEPPER') || 'fluentmeet-default-pepper-secret-32b'
const ALLOWED_ORIGIN = Deno.env.get('ALLOWED_ORIGIN') || '*'

const admin = createClient(SUPABASE_URL, SERVICE_KEY, { auth: { persistSession: false } })

const cors = {
  'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
  'Access-Control-Allow-Headers': 'authorization, content-type, apikey',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Vary': 'Origin',
}
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, 'Content-Type': 'application/json' } })

// ---- helpers ---------------------------------------------------------------
async function hmacHex(value: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(PEPPER), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(value))
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('')
}

/** Real client IP. Behind Supabase/Cloudflare the first x-forwarded-for hop is the client. */
function clientIp(req: Request): string | null {
  const raw = req.headers.get('cf-connecting-ip') ?? req.headers.get('x-forwarded-for')?.split(',')[0]?.trim()
  return raw || null
}

/** Privacy: store a masked IP (IPv4 /24, IPv6 /48); keep an HMAC for correlation. */
function maskIp(ip: string | null): string | null {
  if (!ip) return null
  if (ip.includes('.')) {
    const p = ip.split('.')
    return p.length === 4 ? `${p[0]}.${p[1]}.${p[2]}.0/24` : null
  }
  const groups = ip.split(':').slice(0, 3)
  return groups.length === 3 ? `${groups.join(':')}::/48` : null
}

function parseUserAgent(ua: string) {
  const os = /Windows NT/.test(ua) ? 'Windows' : /Android/.test(ua) ? 'Android'
    : /iPhone|iPad|iOS/.test(ua) ? 'iOS' : /Mac OS X/.test(ua) ? 'macOS'
    : /CrOS/.test(ua) ? 'ChromeOS' : /Linux/.test(ua) ? 'Linux' : 'Unknown'
  const browser = /Edg\//.test(ua) ? 'Edge' : /OPR\//.test(ua) ? 'Opera'
    : /Firefox\//.test(ua) ? 'Firefox' : /Chrome\//.test(ua) ? 'Chrome'
    : /Safari\//.test(ua) ? 'Safari' : 'Unknown'
  const device = /Mobi|Android|iPhone/.test(ua) ? 'mobile' : /iPad|Tablet/.test(ua) ? 'tablet' : 'desktop'
  return { os, browser, device }
}

function jwtClaims(token: string): Record<string, unknown> {
  const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
  return JSON.parse(atob(payload.padEnd(Math.ceil(payload.length / 4) * 4, '=')))
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

// ---- handler ---------------------------------------------------------------
Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors })
  if (req.method !== 'POST') return json({ error: 'method_not_allowed' }, 405)

  const action = new URL(req.url).pathname.split('/').pop()
  const ip = clientIp(req)
  const ipHash = ip ? await hmacHex(ip) : null
  const ua = (req.headers.get('user-agent') ?? '').slice(0, 512)
  const country = (req.headers.get('cf-ipcountry') ?? '').slice(0, 2).toUpperCase() || null
  const device = parseUserAgent(ua)

  try {
    // ------------------------------------------------------------------ LOGIN
    if (action === 'login') {
      const body = await req.json().catch(() => null)
      const email = String(body?.email ?? '').trim().toLowerCase()
      const password = String(body?.password ?? '')
      if (!EMAIL_RE.test(email) || password.length < 1 || password.length > 256) {
        return json({ error: 'invalid_input' }, 400)
      }

      const { data: blocked } = await admin.rpc('is_login_blocked', { p_email: email, p_ip_hash: ipHash })
      if (blocked) return json({ error: 'temporarily_blocked' }, 429)

      const anon = createClient(SUPABASE_URL, ANON_KEY, { auth: { persistSession: false } })
      const { data, error } = await anon.auth.signInWithPassword({ email, password })

      if (error || !data.session) {
        await admin.rpc('record_login_failure', {
          p_email: email, p_ip: maskIp(ip), p_ip_hash: ipHash,
          p_identifier_hash: await hmacHex(email), p_country: country, p_ua: ua,
        })
        return json({ error: 'invalid_credentials' }, 401)
      }

      const claims = jwtClaims(data.session.access_token)
      const { error: recErr } = await admin.rpc('record_login_success', {
        p_user_id: data.user.id, p_auth_session_id: String(claims.session_id),
        p_ip: maskIp(ip), p_ip_hash: ipHash, p_country: country, p_ua: ua, p_device: device,
      })
      if (recErr) {
        console.error('record_login_success failed', recErr)
        await anon.auth.signOut()
        return json({ error: 'server_error' }, 500)
      }
      return json({ session: data.session })
    }

    // ----------------------------------------------------------------- LOGOUT
    if (action === 'logout') {
      const token = req.headers.get('authorization')?.replace(/^Bearer /i, '')
      if (!token) return json({ error: 'unauthorized' }, 401)
      const { data: { user }, error } = await admin.auth.getUser(token)
      if (error || !user) return json({ error: 'unauthorized' }, 401)
      await admin.rpc('record_logout', { p_auth_session_id: String(jwtClaims(token).session_id), p_reason: 'logout' })
      return json({ ok: true })
    }

    // ------------------------------------------------------------- BEACON END
    if (action === 'beacon-end') {
      const body = await req.json().catch(() => null)
      const token = String(body?.access_token ?? '')
      const { data: { user } } = await admin.auth.getUser(token)
      if (user) {
        await admin.rpc('record_logout', { p_auth_session_id: String(jwtClaims(token).session_id), p_reason: 'logout' })
      }
      return json({ ok: true })
    }

    return json({ error: 'not_found' }, 404)
  } catch (e) {
    console.error('auth-gateway error', e)
    return json({ error: 'server_error' }, 500)
  }
})
