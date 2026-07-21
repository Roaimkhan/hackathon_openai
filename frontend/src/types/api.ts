export interface CompatibilityScore {
  score: number;
  explanation: string;
}

export interface MealImage {
  id: string;
  public_url: string;
  position: number;
}

export interface MealCardItem {
  id: string;
  owner_id: string;
  owner_name?: string;
  title: string;
  description: string;
  cuisine: string;
  spice_level: number;
  dietary_tags: string[];
  allergens: string[];
  taste_notes: string[];
  location?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  image_url: string;
  distance_km: number;
  compatibility_score: number;
  explanation: string;
}

export interface SearchIntentResult {
  cuisine?: string | null;
  max_spice_level?: number | null;
  tags: string[];
  radius_km?: number | null;
}

export interface SearchRequest {
  q: string;
  latitude?: number;
  longitude?: number;
  radius_km?: number;
  limit?: number;
}

export interface FeedRequest {
  latitude?: number;
  longitude?: number;
  radius_km?: number;
  limit?: number;
}

export interface SearchResponse {
  items: MealCardItem[];
  count: number;
}

export interface FeedResponse extends SearchResponse {}

export interface MealCreateRequest {
  title?: string | null;
  description?: string | null;
  location?: string | null;
  latitude?: number;
  longitude?: number;
}

export interface MealResponse {
  id: string;
  owner_id: string;
  title: string;
  description: string;
  cuisine: string;
  spice_level: number;
  dietary_tags: string[];
  allergens: string[];
  taste_notes: string[];
  analysis_status: string;
  location?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  images: MealImage[];
  created_at: string;
  updated_at: string;
}
