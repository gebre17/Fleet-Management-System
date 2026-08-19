/**
 * WebSocket client for real-time tracking
 */
export type { LocationUpdate, AlertMessage } from '@/types/location';
import type { LocationUpdate, AlertMessage } from '@/types/location';

export type SocketMessage = LocationUpdate | AlertMessage;

export class TrackingWebSocket {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private closedByClient = false;
  private path = '';
  private token = '';
  private onMessage: ((data: SocketMessage) => void) | null = null;
  private onError: ((error: Event) => void) | null = null;

  /**
   * Connect to a WebSocket endpoint under NEXT_PUBLIC_WS_URL.
   *
   * @param path Server path, e.g. `/ws/fleet` or `/ws/${vehicleId}`
   * @param token JWT access token (sent as a query param — the browser
   *   WebSocket API cannot set an Authorization header)
   */
  connect(
    path: string,
    token: string,
    onMessage: (data: SocketMessage) => void,
    onError?: (error: Event) => void
  ): void {
    this.path = path;
    this.token = token;
    this.onMessage = onMessage;
    this.onError = onError ?? null;
    this.closedByClient = false;

    const url = `${process.env.NEXT_PUBLIC_WS_URL}${path}?token=${encodeURIComponent(token)}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        this.onError?.(error);
      };

      this.ws.onclose = () => {
        if (!this.closedByClient) {
          this.attemptReconnect();
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.onMessage) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

      this.reconnectTimer = setTimeout(() => {
        this.connect(this.path, this.token, this.onMessage!, this.onError ?? undefined);
      }, delay);
    }
  }

  disconnect(): void {
    this.closedByClient = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}
