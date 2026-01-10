import React, { useState } from 'react';
import { Send, User } from 'lucide-react';
import axios from 'axios';
// import { useWebSocket } from '../useWebSocket';

interface ChatMessage {
    sender: 'user' | 'bot';
    text: string;
}

export const ClientChat: React.FC = () => {
    const [input, setInput] = useState('');
    const [history, setHistory] = useState<ChatMessage[]>([
        { sender: 'bot', text: 'Olá! Sou o Product Owner da agência. O que você gostaria de construir hoje?' }
    ]);
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const newMessage: ChatMessage = { sender: 'user', text: input };
        setHistory([...history, newMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // Send to backend API
            await axios.post('http://localhost:8000/chat', { message: input });
            // Response will come via WebSocket (in a real app), or we can mock it here for now
            setHistory(prev => [...prev, { sender: 'bot', text: 'Recebido! Analisando sua solicitação...' }]);
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-900 border-r border-gray-700">
            <div className="p-4 border-b border-gray-700 bg-gray-800">
                <h2 className="text-lg font-bold flex items-center gap-2 text-white">
                    <User className="w-5 h-5" /> Chat com Cliente
                </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {history.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-lg ${msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200'}`}>
                            {msg.text}
                        </div>
                    </div>
                ))}
            </div>

            <div className="p-4 border-t border-gray-700 bg-gray-800">
                <div className="flex gap-2">
                    <input
                        className="flex-1 bg-gray-700 text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Digite sua solicitação..."
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded transition-colors disabled:opacity-50"
                        disabled={isLoading}
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
};
