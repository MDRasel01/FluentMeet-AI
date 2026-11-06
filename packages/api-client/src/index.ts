import {
  ApiResponse,
  AuthTokens,
  UserProfile,
  UserDetail,
  AuthSession,
  Organization,
  OrganizationMember,
  OrganizationInvitation,
} from '@fluentmeet/shared-types';

export interface ClientConfig {
  baseUrl: string;
  getToken?: () => string | null | Promise<string | null>;
  onTokenExpired?: () => void;
}

export class FluentMeetApiClient {
  private baseUrl: string;
  private getToken?: () => string | null | Promise<string | null>;
  private onTokenExpired?: () => void;

  constructor(config: ClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, '');
    this.getToken = config.getToken;
    this.onTokenExpired = config.onTokenExpired;
  }

  private async getHeaders(): Promise<HeadersInit> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (this.getToken) {
      const token = await this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  private async request<T>(path: string, options: RequestInit): Promise<ApiResponse<T>> {
    const headers = await this.getHeaders();
    const res = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        ...headers,
        ...(options.headers || {}),
      },
    });

    if (res.status === 401 && this.onTokenExpired) {
      this.onTokenExpired();
    }

    return res.json();
  }

  async get<T>(path: string): Promise<ApiResponse<T>> {
    return this.request<T>(path, { method: 'GET' });
  }

  async post<T>(path: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T>(path: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(path, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(path: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(path, {
      method: 'DELETE',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  // --- Authentication Endpoints ---
  async register(payload: {
    email: string;
    password: string;
    confirm_password?: string;
    full_name: string;
    native_language?: string;
  }): Promise<ApiResponse<UserProfile>> {
    return this.post<UserProfile>('/api/v1/auth/register', payload);
  }

  async verifyEmail(token: string): Promise<ApiResponse<boolean>> {
    return this.post<boolean>('/api/v1/auth/verify-email', { token });
  }

  async resendVerification(email: string): Promise<ApiResponse<boolean>> {
    return this.post<boolean>('/api/v1/auth/resend-verification', { email });
  }

  async login(payload: {
    email: string;
    password: string;
    device_type?: string;
    session_name?: string;
  }): Promise<ApiResponse<AuthTokens>> {
    return this.post<AuthTokens>('/api/v1/auth/login', payload);
  }

  async refreshTokens(refreshToken: string): Promise<ApiResponse<AuthTokens>> {
    return this.post<AuthTokens>('/api/v1/auth/refresh', { refresh_token: refreshToken });
  }

  async logout(): Promise<ApiResponse<boolean>> {
    return this.post<boolean>('/api/v1/auth/logout');
  }

  async logoutAll(): Promise<ApiResponse<number>> {
    return this.post<number>('/api/v1/auth/logout-all');
  }

  async forgotPassword(email: string): Promise<ApiResponse<boolean>> {
    return this.post<boolean>('/api/v1/auth/forgot-password', { email });
  }

  async resetPassword(payload: {
    token: string;
    new_password: string;
    confirm_password?: string;
  }): Promise<ApiResponse<boolean>> {
    return this.post<boolean>('/api/v1/auth/reset-password', payload);
  }

  async changePassword(payload: {
    current_password: string;
    new_password: string;
    confirm_password?: string;
  }): Promise<ApiResponse<boolean>> {
    return this.post<boolean>('/api/v1/auth/change-password', payload);
  }

  async listSessions(): Promise<ApiResponse<AuthSession[]>> {
    return this.get<AuthSession[]>('/api/v1/auth/sessions');
  }

  async revokeSession(sessionId: string): Promise<ApiResponse<boolean>> {
    return this.delete<boolean>(`/api/v1/auth/sessions/${sessionId}`);
  }

  // --- User Profile Endpoints ---
  async getMyProfile(): Promise<ApiResponse<UserDetail>> {
    return this.get<UserDetail>('/api/v1/users/me');
  }

  async updateMyProfile(payload: Partial<UserDetail>): Promise<ApiResponse<UserDetail>> {
    return this.patch<UserDetail>('/api/v1/users/me', payload);
  }

  async deactivateAccount(password: string, reason?: string): Promise<ApiResponse<boolean>> {
    return this.delete<boolean>('/api/v1/users/me', { password, reason });
  }

  // --- Organization Endpoints ---
  async createOrganization(payload: {
    name: string;
    slug?: string;
    org_type?: string;
    timezone?: string;
    default_language?: string;
  }): Promise<ApiResponse<Organization>> {
    return this.post<Organization>('/api/v1/organizations', payload);
  }

  async listMyOrganizations(): Promise<ApiResponse<Organization[]>> {
    return this.get<Organization[]>('/api/v1/organizations');
  }

  async getOrganization(orgId: string): Promise<ApiResponse<Organization>> {
    return this.get<Organization>(`/api/v1/organizations/${orgId}`);
  }

  async updateOrganization(orgId: string, payload: Partial<Organization>): Promise<ApiResponse<Organization>> {
    return this.patch<Organization>(`/api/v1/organizations/${orgId}`, payload);
  }

  async deleteOrganization(orgId: string): Promise<ApiResponse<boolean>> {
    return this.delete<boolean>(`/api/v1/organizations/${orgId}`);
  }

  async listOrganizationMembers(orgId: string): Promise<ApiResponse<OrganizationMember[]>> {
    return this.get<OrganizationMember[]>(`/api/v1/organizations/${orgId}/members`);
  }

  async updateMemberRole(orgId: string, userId: string, role: string): Promise<ApiResponse<OrganizationMember>> {
    return this.patch<OrganizationMember>(`/api/v1/organizations/${orgId}/members/${userId}`, { role });
  }

  async removeMember(orgId: string, userId: string): Promise<ApiResponse<boolean>> {
    return this.delete<boolean>(`/api/v1/organizations/${orgId}/members/${userId}`);
  }

  async transferOwnership(orgId: string, newOwnerUserId: string, password: string): Promise<ApiResponse<boolean>> {
    return this.post<boolean>(`/api/v1/organizations/${orgId}/transfer-ownership`, {
      new_owner_user_id: newOwnerUserId,
      password,
    });
  }

  // --- Invitations Endpoints ---
  async sendInvitation(orgId: string, invitedEmail: string, role: string = 'member'): Promise<ApiResponse<OrganizationInvitation>> {
    return this.post<OrganizationInvitation>(`/api/v1/organizations/${orgId}/invitations`, {
      invited_email: invitedEmail,
      role,
    });
  }

  async listInvitations(orgId: string): Promise<ApiResponse<OrganizationInvitation[]>> {
    return this.get<OrganizationInvitation[]>(`/api/v1/organizations/${orgId}/invitations`);
  }

  async acceptInvitation(token: string): Promise<ApiResponse<OrganizationMember>> {
    return this.post<OrganizationMember>('/api/v1/invitations/accept', { token });
  }

  async revokeInvitation(invitationId: string): Promise<ApiResponse<boolean>> {
    return this.delete<boolean>(`/api/v1/invitations/${invitationId}`);
  }
}
