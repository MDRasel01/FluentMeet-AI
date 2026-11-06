"""Add SaaS auth, sessions, refresh tokens, invitations and org settings

Revision ID: 002_auth_and_organizations
Revises: 001_initial_schema
Create Date: 2026-11-06 20:30:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_auth_and_organizations'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Update users table
    op.add_column('users', sa.Column('status', sa.String(length=50), server_default='pending_verification', nullable=False))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(length=50), server_default='UTC', nullable=False))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # 2. Update organizations table
    op.add_column('organizations', sa.Column('org_type', sa.String(length=50), server_default='team', nullable=False))
    op.add_column('organizations', sa.Column('timezone', sa.String(length=50), server_default='UTC', nullable=False))
    op.add_column('organizations', sa.Column('default_language', sa.String(length=50), server_default='English', nullable=False))
    op.add_column('organizations', sa.Column('seat_limit', sa.Integer(), server_default='5', nullable=False))
    op.add_column('organizations', sa.Column('retention_days', sa.Integer(), server_default='7', nullable=False))
    op.add_column('organizations', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    # 3. Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('avatar_url', sa.String(length=1024), nullable=True),
        sa.Column('phone_number', sa.String(length=50), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('job_title', sa.String(length=100), nullable=True),
        sa.Column('english_learning_goal', sa.String(length=255), nullable=True),
        sa.Column('target_speaking_score', sa.Integer(), server_default='80', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'])

    # 4. Create auth_sessions table
    op.create_table(
        'auth_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_name', sa.String(length=100), nullable=True),
        sa.Column('device_type', sa.String(length=50), server_default='desktop', nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])

    # 5. Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('auth_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(length=255), unique=True, nullable=False),
        sa.Column('family_id', sa.String(length=36), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replaced_by_token_id', sa.String(length=36), nullable=True),
    )
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])
    op.create_index('ix_refresh_tokens_session_id', 'refresh_tokens', ['session_id'])
    op.create_index('ix_refresh_tokens_family_id', 'refresh_tokens', ['family_id'])

    # 6. Create email_verification_tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(length=255), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_email_verification_tokens_token_hash', 'email_verification_tokens', ['token_hash'])
    op.create_index('ix_email_verification_tokens_user_id', 'email_verification_tokens', ['user_id'])

    # 7. Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(length=255), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'])
    op.create_index('ix_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])

    # 8. Create organization_settings table
    op.create_table(
        'organization_settings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('organization_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('allow_manager_invites', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('require_2fa', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('enforce_recording_consent', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_organization_settings_organization_id', 'organization_settings', ['organization_id'])

    # 9. Create organization_invitations table
    op.create_table(
        'organization_invitations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('organization_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('invited_email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), server_default='member', nullable=False),
        sa.Column('token_hash', sa.String(length=255), unique=True, nullable=False),
        sa.Column('invited_by', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_org_invitations_token_hash', 'organization_invitations', ['token_hash'])
    op.create_index('ix_org_invitations_org_id', 'organization_invitations', ['organization_id'])
    op.create_index('ix_org_invitations_email', 'organization_invitations', ['invited_email'])

    # 10. Organization members unique constraint
    op.create_unique_constraint('uq_org_member', 'organization_members', ['organization_id', 'user_id'])
    op.add_column('organization_members', sa.Column('status', sa.String(length=50), server_default='active', nullable=False))
    op.add_column('organization_members', sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))
    op.add_column('organization_members', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

    # 11. Add organization_id to audit_logs
    op.add_column('audit_logs', sa.Column('organization_id', sa.String(length=36), sa.ForeignKey('organizations.id', ondelete='SET NULL'), nullable=True))
    op.create_index('ix_audit_logs_org_id', 'audit_logs', ['organization_id'])

def downgrade() -> None:
    op.drop_column('audit_logs', 'organization_id')
    op.drop_constraint('uq_org_member', 'organization_members', type_='unique')
    op.drop_column('organization_members', 'updated_at')
    op.drop_column('organization_members', 'joined_at')
    op.drop_column('organization_members', 'status')
    op.drop_table('organization_invitations')
    op.drop_table('organization_settings')
    op.drop_table('password_reset_tokens')
    op.drop_table('email_verification_tokens')
    op.drop_table('refresh_tokens')
    op.drop_table('auth_sessions')
    op.drop_table('user_profiles')
    op.drop_column('organizations', 'updated_at')
    op.drop_column('organizations', 'retention_days')
    op.drop_column('organizations', 'seat_limit')
    op.drop_column('organizations', 'default_language')
    op.drop_column('organizations', 'timezone')
    op.drop_column('organizations', 'org_type')
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'status')
