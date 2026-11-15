/**
 * One-time Founder Account Seed Script (scripts/seed-founder.ts)
 * 
 * Securely provisions the single platform owner account via Supabase Auth Admin API.
 * Password and credentials are read strictly from environment variables.
 * 
 * Usage:
 *   FOUNDER_INITIAL_PASSWORD="your-strong-password" \
 *   SUPABASE_URL="https://your-project.supabase.co" \
 *   SUPABASE_SERVICE_ROLE_KEY="your-service-role-key" \
 *   npx tsx scripts/seed-founder.ts
 */

import { createClient } from '@supabase/supabase-js';

const FOUNDER_EMAIL = 'russell7@gmail.com';

async function seedFounder() {
  const supabaseUrl = process.env.SUPABASE_URL;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const initialPassword = process.env.FOUNDER_INITIAL_PASSWORD;

  if (!supabaseUrl || !serviceRoleKey) {
    console.error('❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment.');
    process.exit(1);
  }

  if (!initialPassword || initialPassword.length < 8) {
    console.error('❌ Error: FOUNDER_INITIAL_PASSWORD must be provided and be at least 8 characters long.');
    process.exit(1);
  }

  console.log(`🔐 Initializing Supabase Admin client for founder seeding...`);
  const adminClient = createClient(supabaseUrl, serviceRoleKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });

  try {
    // 1. Create or fetch user in auth.users
    console.log(`👤 Checking / creating user: ${FOUNDER_EMAIL}`);
    const { data: userData, error: createError } = await adminClient.auth.admin.createUser({
      email: FOUNDER_EMAIL,
      password: initialPassword,
      email_confirm: true,
      user_metadata: {
        full_name: 'Founder (Russell)',
        role: 'owner',
      },
    });

    let userId: string;

    if (createError) {
      if (createError.message.includes('already registered')) {
        console.log(`ℹ️ User already exists in auth.users, looking up user ID...`);
        const { data: listData, error: listError } = await adminClient.auth.admin.listUsers();
        if (listError) throw listError;
        const existing = listData.users.find((u) => u.email?.toLowerCase() === FOUNDER_EMAIL.toLowerCase());
        if (!existing) throw new Error('Could not find existing user ID.');
        userId = existing.id;
      } else {
        throw createError;
      }
    } else {
      userId = userData.user.id;
      console.log(`✅ Auth user created successfully with ID: ${userId}`);
    }

    // 2. Insert or update single profile with role = 'owner' and must_change_password = true
    console.log(`🛡️ Provisioning profiles entry with role='owner' and must_change_password=true...`);
    const { error: profileError } = await adminClient
      .from('profiles')
      .upsert(
        {
          id: userId,
          email: FOUNDER_EMAIL,
          role: 'owner',
          must_change_password: true,
          theme: 'system',
          updated_at: new Date().toISOString(),
        },
        { onConflict: 'id' }
      );

    if (profileError) {
      throw profileError;
    }

    console.log(`\n🎉 SUCCESS: Founder account seeded successfully!`);
    console.log(`   - Email: ${FOUNDER_EMAIL}`);
    console.log(`   - Role: owner`);
    console.log(`   - must_change_password: true`);
    console.log(`\n⚠️ SECURITY REMINDER: Clear FOUNDER_INITIAL_PASSWORD from your terminal history/environment now.\n`);
  } catch (err: any) {
    console.error('❌ Failed to seed founder account:', err?.message || err);
    process.exit(1);
  }
}

seedFounder();
