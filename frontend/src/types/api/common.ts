/** Standard API response envelope. */

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta?: {
    correlation_id?: string | null;
  };
}
