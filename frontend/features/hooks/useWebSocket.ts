import { useEffect, useRef, useState } from 'react';

interface WebSocketMessage {
  type: 'transcription_update' | 'progress_update' | 'error';
  session_id: string;
  progress?: number;
  stage?: string;
  status?: string;
  details?: string;
  error?: string;
  error_code?: string;
  data?: any;
  timestamp?: string;
}

interface UseWebSocketProps {
  sessionId: string;
  enabled?: boolean;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export const useWebSocket = ({
  sessionId,
  enabled = true,
  onMessage,
  onError,
  onConnect,
  onDisconnect,
}: UseWebSocketProps) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  const connect = () => {
    if (!enabled || !sessionId) return;

    try {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL 
        ? `${process.env.NEXT_PUBLIC_WS_URL}/ws/${sessionId}`
        : `ws://localhost:8000/api/v1/ws/${sessionId}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        setReconnectAttempts(0);
        if (onConnect) onConnect();
        console.log(`WebSocket connected for session ${sessionId}`);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          if (onMessage) onMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        if (onDisconnect) onDisconnect();
        console.log(`WebSocket disconnected for session ${sessionId}`);

        // Attempt to reconnect
        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, reconnectDelay);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (onError) onError(error);
      };

      websocketRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
    setIsConnected(false);
  };

  const sendMessage = (message: any) => {
    if (websocketRef.current && isConnected) {
      websocketRef.current.send(JSON.stringify(message));
    }
  };

  useEffect(() => {
    if (enabled && sessionId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [sessionId, enabled]);

  return {
    isConnected,
    lastMessage,
    reconnectAttempts,
    sendMessage,
    connect,
    disconnect,
  };
};