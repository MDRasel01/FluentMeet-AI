import { ApiResponse } from '@fluentmeet/shared-types';
import { API_ENDPOINTS } from '@fluentmeet/shared-constants';

export interface ClientConfig {
  baseUrl: string;
  getToken?: () => string | null | Promise<string | null>;
}

export class FluentMeetApiClient {
  private baseUrl: string;
  private getToken?: () => string | null | Promise<string | null>;

  constructor(config: ClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, '');
    this.getToken = config.getToken;
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

  async get<T>(path: string): Promise<ApiResponse<T>> {
    const headers = await this.getHeaders();
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: 'GET',
      headers,
    });
    return res.json();
  }

  async post<T>(path: string, body?: any): Promise<ApiResponse<T>> {
    const headers = await this.getHeaders();
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    return res.json();
  }

  async checkHealthLive(): Promise<boolean> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.HEALTH_LIVE}`);
      return res.ok;
    } catch {
      return false;
    }
  }

  async checkHealthReady(): Promise<boolean> {
    try {
      const res = await fetch(`${this.baseUrl}${API_ENDPOINTS.HEALTH_READY}`);
      return res.ok;
    } catch {
      return false;
    }
  }
}

