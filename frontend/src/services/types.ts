export interface User {
  id: string;
  email: string;
  display_name: string;
  created_at: string;
}

export interface Profile {
  user_id: string;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
  updated_at: string;
}

export interface TasteProfile {
  user_id: string;
  preferences: string[];
  dietary_tags: string[];
  created_at: string;
  updated_at: string;
}

export interface AuthSession {
  access_token: string;
  token_type: "bearer";
  user: User;
}

export interface RegisterPayload {
  display_name: string;
  email: string;
  password: string;
  latitude?: number;
  longitude?: number;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export type SwapStatus = "pending" | "accepted" | "rejected" | "completed";

export interface SwapResponse {
  id: string;
  meal_id: string;
  requester_id: string;
  recipient_id: string;
  message: string | null;
  status: SwapStatus;
  meal: {
    id: string;
    title: string;
    image_url?: string | null;
  };
  history: Array<{ id: string; swap_request_id: string; action: string; actor_id: string; details: Record<string, unknown>; created_at: string }>;
  created_at: string;
  updated_at: string;
}

export interface ApiEnvelope<T> {
  data: T;
  meta: Record<string, unknown>;
}

export interface ApiErrorPayload {
  error: {
    code: string;
    message: string;
  };
}
