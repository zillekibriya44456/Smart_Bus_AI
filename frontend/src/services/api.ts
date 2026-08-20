/*
Axios API client for the Smart Bus Stop AI backend.

The base URL is read from the VITE_API_URL environment variable so the same
build works in development (http://localhost:8000) and inside Docker
(http://backend:8000).
*/
import type { AxiosResponse } from 'axios';
import axios from 'axios';

// ── Types ──────────────────────────────────────────────────────────────────────

export interface LocationRequest {
  Passenger_Count: number;
  Boarding: number;
  Alighting: number;
  Road_Width: number;
  Walking_Distance_m: number;
  Distance_to_Next_Stop_m: number;
  Traffic_Level: 'Low' | 'Moderate' | 'High';
  Bus_Frequency: number;
  Waiting_Time_min: number;
  Occupancy_pct: number;
}

export interface SubScores {
  Demand: number;
  Road: number;
  Accessibility: number;
  Safety: number;
  Spacing: number;
}

export interface LocationResponse {
  Suitability_Score: number;
  Suitability_Category: string;
  SubScores: SubScores;
  Priority_Score: number | null;
  Priority_Category: string | null;
  Positive_Factors: string[];
  Negative_Factors: string[];
  Recommendations: string[];
  Analysis_Type: 'Explicit' | 'Derived';
  Derived_From_Coordinates: Record<string, unknown> | null;
}

export interface OptimizationCandidate {
  Rank: number;
  Latitude: number;
  Longitude: number;
  Suitability_Score: number;
  Suitability_Category: string;
  Positive_Factors: string[];
  Negative_Factors: string[];
  Derived_Features: Record<string, unknown>;
}

export interface OptimizationResponse {
  Center_Latitude: number;
  Center_Longitude: number;
  Radius_km: number;
  Disclaimer: string;
  Candidates: OptimizationCandidate[];
}

export interface CompareLocationsResponse {
  Location_A_Response: LocationResponse;
  Location_B_Response: LocationResponse;
  Recommended_Location: 'Location A' | 'Location B' | 'Tie';
  Recommendation_Reason: string;
}

export interface CorridorRequest {
  Start_Latitude: number;
  Start_Longitude: number;
  End_Latitude: number;
  End_Longitude: number;
  Buffer_m?: number;
}

export interface RelocationCandidate {
  Latitude: number;
  Longitude: number;
  New_Score: number;
  Improvement: number;
  Distance_Moved_m: number;
  Reason: string;
}

export interface CorridorDecision {
  Stop_ID: string;
  Current_Latitude: number;
  Current_Longitude: number;
  Current_Score: number;
  Decision: 'RETAIN' | 'IMPROVE' | 'RELOCATE' | 'REMOVE';
  Positive_Factors: string[];
  Negative_Factors: string[];
  Explanation: string;
  Recommended_Location: RelocationCandidate | null;
  Alternatives: RelocationCandidate[];
}

export interface CorridorAnalysisResponse {
  Total_Stops_Analyzed: number;
  Count_Retain: number;
  Count_Improve: number;
  Count_Relocate: number;
  Count_Remove: number;
  Average_Score_Before: number;
  Average_Score_After: number;
  Decisions: CorridorDecision[];
}

export interface BusStop {
  Stop_ID: string;
  Passenger_Count: number;
  Road_Width: number;
  Traffic_Level: string;
  Latitude: number | null;
  Longitude: number | null;
  Suitability_Score: number;
  Suitability_Category: string;
  Priority_Score: number;
  Priority_Category: string;
  Positive_Factors: string[];
  Negative_Factors: string[];
  Recommendations: string[];
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  version: string;
  environment: string;
  components: {
    database: 'ok' | 'unavailable';
    ml_models: 'ok' | 'unavailable';
  };
}

// ── Axios instance ─────────────────────────────────────────────────────────────

const API_BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — log outgoing requests in development
api.interceptors.request.use((config) => {
  if (import.meta.env.DEV) {
    console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  }
  return config;
});

// Response interceptor — normalize error messages
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    const message: string =
      error.response?.data?.detail ??
      error.message ??
      'An unexpected error occurred.';
    console.error('[API Error]', message);
    return Promise.reject(new Error(message));
  },
);

// ── API functions ──────────────────────────────────────────────────────────────

export const getHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/health');
  return response.data;
};

export const analyzeLocation = async (data: LocationRequest): Promise<LocationResponse> => {
  const response = await api.post<LocationResponse>('/analyze-location', data);
  return response.data;
};

export const analyzeCoordinates = async (lat: number, lon: number): Promise<LocationResponse> => {
  const response = await api.post<LocationResponse>('/analyze-coordinates', {
    Latitude: lat,
    Longitude: lon,
  });
  return response.data;
};

export const optimizeLocation = async (
  lat: number,
  lon: number,
  radiusKm: number,
): Promise<OptimizationResponse> => {
  const response = await api.post<OptimizationResponse>('/optimize-location', {
    Latitude: lat,
    Longitude: lon,
    Radius_km: radiusKm,
  });
  return response.data;
};

export const compareLocations = async (
  locA: LocationRequest,
  locB: LocationRequest,
): Promise<CompareLocationsResponse> => {
  const response = await api.post<CompareLocationsResponse>('/compare-locations', {
    Location_A: locA,
    Location_B: locB,
  });
  return response.data;
};

export const getBusStops = async (): Promise<BusStop[]> => {
  const response = await api.get<BusStop[]>('/bus-stops');
  return response.data;
};

export const getBusStopDetails = async (id: string): Promise<{ Data: Record<string, unknown>; Analysis: Partial<LocationResponse> }> => {
  const response = await api.get(`/bus-stops/${id}`);
  return response.data;
};

export const analyzeCorridor = async (req: CorridorRequest): Promise<CorridorAnalysisResponse> => {
  const response = await api.post<CorridorAnalysisResponse>('/analyze-corridor', req);
  return response.data;
};

export interface NominatimResult {
  place_id: number;
  lat: string;
  lon: string;
  display_name: string;
}

export const searchLocations = async (query: string): Promise<NominatimResult[]> => {
  // Bangalore bounding box: 77.4 to 77.8 E, 12.8 to 13.2 N
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&viewbox=77.4,13.2,77.8,12.8&bounded=1&limit=5`;
  const response = await axios.get<NominatimResult[]>(url);
  return response.data;
};
