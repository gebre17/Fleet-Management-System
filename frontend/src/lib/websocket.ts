/**
 * WebSocket client for real-time tracking
 */
export interface LocationUpdate {
  type: string;
  vehicle_id: string;
  latitude: number;
  longitude: number;
  speed?: number;
  heading?: number;
  timestamp: string;
}

export class TrackingWebSocket {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;

  connect(
    vehicleId: string,
    onMessage: (data: LocationUpdate) => void,
    onError?: (error: Event) => void
  ): void {
    const url = `${process.env.NEXT_PUBLIC_WS_URL}/ws/${vehicleId}`;
    
    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log(`WebSocket connected to vehicle ${vehicleId}`);
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (onError) onError(error);
      };

      this.ws.onclose = () => {
        console.log(`WebSocket closed for vehicle ${vehicleId}`);
        this.attemptReconnect(vehicleId, onMessage, onError);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.attemptReconnect(vehicleId, onMessage, onError);
    }
  }

  private attemptReconnect(
    vehicleId: string,
    onMessage: (data: LocationUpdate) => void,
    onError?: (error: Event) => void
  ): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      
      this.reconnectTimer = setTimeout(() => {
        console.log(
          `Attempting to reconnect to vehicle ${vehicleId} (attempt ${this.reconnectAttempts})`
        );
        this.connect(vehicleId, onMessage, onError);
      }, delay);
    }
  }

  disconnect(): void {
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
