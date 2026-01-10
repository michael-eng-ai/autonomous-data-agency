import { useEffect, useRef, useState, useCallback } from 'react';

const SOCKET_URL = 'ws://localhost:8000/ws';

export const useWebSocket = () => {
    const socket = useRef<WebSocket | null>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        socket.current = new WebSocket(SOCKET_URL);

        socket.current.onopen = () => {
            console.log('Connected to WebSocket');
            setIsConnected(true);
        };

        socket.current.onmessage = (event) => {
            const message = JSON.parse(event.data);
            setMessages((prev) => [...prev, message]);
        };

        socket.current.onclose = () => {
            console.log('Disconnected from WebSocket');
            setIsConnected(false);
        };

        return () => {
            socket.current?.close();
        };
    }, []);

    const sendMessage = useCallback((msg: any) => {
        if (socket.current?.readyState === WebSocket.OPEN) {
            socket.current.send(JSON.stringify(msg));
        }
    }, []);

    return { messages, isConnected, sendMessage };
};
