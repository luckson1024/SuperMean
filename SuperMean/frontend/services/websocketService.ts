import { useEffect, useState } from 'react';
import { useMissionStore } from '../store/useMissionStore';
import { useAgentStore } from '../store/useAgentStore';

// WebSocket connection URL
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

// Message types for WebSocket communication
export enum MessageType {
  MISSION_UPDATE = 'MISSION_UPDATE',
  AGENT_UPDATE = 'AGENT_UPDATE',
  SYSTEM_NOTIFICATION = 'SYSTEM_NOTIFICATION',
}

// Interface for WebSocket messages
export interface WebSocketMessage {
  type: MessageType;
  data: any;
  timestamp: string;
}

// WebSocket connection status
export enum ConnectionStatus {
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
}

// WebSocket service for real-time updates
class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private messageHandlers: Map<MessageType, ((data: any) => void)[]> = new Map();
  private statusChangeCallbacks: ((status: ConnectionStatus) => void)[] = [];
  private connectionStatus: ConnectionStatus = ConnectionStatus.DISCONNECTED;

  // Initialize WebSocket connection
  connect() {
    if (this.socket?.readyState === WebSocket.OPEN) return;

    this.updateStatus(ConnectionStatus.CONNECTING);
    
    try {
      this.socket = new WebSocket(WS_URL);

      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.updateStatus(ConnectionStatus.ERROR);
      this.attemptReconnect();
    }
  }

  // Close WebSocket connection
  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    this.updateStatus(ConnectionStatus.DISCONNECTED);
  }

  // Send message through WebSocket
  sendMessage(type: MessageType, data: any) {
    if (this.socket?.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      return false;
    }

    const message: WebSocketMessage = {
      type,
      data,
      timestamp: new Date().toISOString(),
    };

    try {
      this.socket.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  // Register message handler
  onMessage(type: MessageType, handler: (data: any) => void) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type)?.push(handler);
  }

  // Remove message handler
  offMessage(type: MessageType, handler: (data: any) => void) {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }

  // Register connection status change handler
  onStatusChange(callback: (status: ConnectionStatus) => void) {
    this.statusChangeCallbacks.push(callback);
    // Immediately call with current status
    callback(this.connectionStatus);
  }

  // Remove connection status change handler
  offStatusChange(callback: (status: ConnectionStatus) => void) {
    const index = this.statusChangeCallbacks.indexOf(callback);
    if (index !== -1) {
      this.statusChangeCallbacks.splice(index, 1);
    }
  }

  // Get current connection status
  getStatus(): ConnectionStatus {
    return this.connectionStatus;
  }

  // Handle WebSocket open event
  private handleOpen() {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    this.updateStatus(ConnectionStatus.CONNECTED);
  }

  // Handle WebSocket message event
  private handleMessage(event: MessageEvent) {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      const handlers = this.messageHandlers.get(message.type);
      
      if (handlers) {
        handlers.forEach(handler => handler(message.data));
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  // Handle WebSocket close event
  private handleClose(event: CloseEvent) {
    console.log(`WebSocket closed: ${event.code} ${event.reason}`);
    this.updateStatus(ConnectionStatus.DISCONNECTED);
    this.attemptReconnect();
  }

  // Handle WebSocket error event
  private handleError(event: Event) {
    console.error('WebSocket error:', event);
    this.updateStatus(ConnectionStatus.ERROR);
  }

  // Update connection status and notify listeners
  private updateStatus(status: ConnectionStatus) {
    this.connectionStatus = status;
    this.statusChangeCallbacks.forEach(callback => callback(status));
  }

  // Attempt to reconnect WebSocket
  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached');
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    console.log(`Attempting to reconnect in ${delay}ms`);
    
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

// React hook for using WebSocket service
export function useWebSocket() {
  const [status, setStatus] = useState<ConnectionStatus>(websocketService.getStatus());
  const missionStore = useMissionStore();
  const agentStore = useAgentStore();

  useEffect(() => {
    // Connect to WebSocket when component mounts
    websocketService.connect();

    // Register status change handler
    websocketService.onStatusChange(setStatus);

    // Register message handlers
    websocketService.onMessage(MessageType.MISSION_UPDATE, (data) => {
      // Update mission in store
      missionStore.updateMissionFromWebSocket(data);
    });

    websocketService.onMessage(MessageType.AGENT_UPDATE, (data) => {
      // Update agent in store
      agentStore.updateAgentFromWebSocket(data);
    });

    // Cleanup on unmount
    return () => {
      websocketService.offStatusChange(setStatus);
      websocketService.disconnect();
    };
  }, [missionStore, agentStore]);

  return {
    status,
    sendMessage: websocketService.sendMessage.bind(websocketService),
    connect: websocketService.connect.bind(websocketService),
    disconnect: websocketService.disconnect.bind(websocketService),
  };
}

export default websocketService;