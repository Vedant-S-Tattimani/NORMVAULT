import { fetchApi } from './client';

export interface UserProfile {
  id: number;
  username: string;
  full_name: string;
  designation?: string;
  department?: string;
  role: 'PROCUREMENT_OFFICER' | 'STANDARDS_AUDITOR' | 'ADMIN';
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  user: UserProfile;
}

export async function switchDemoRole(role: string): Promise<TokenResponse> {
  return fetchApi<TokenResponse>(`/auth/demo-switch?role=${encodeURIComponent(role)}`, {
    method: 'POST',
  });
}

export async function getCurrentUser(): Promise<UserProfile> {
  return fetchApi<UserProfile>('/auth/me');
}
