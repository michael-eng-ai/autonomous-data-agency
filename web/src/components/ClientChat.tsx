import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Sparkles, Loader2 } from 'lucide-react';
import axios from 'axios';

interface ChatMessage {
    sender: 'user' | 'bot';
    text: string;
    timestamp: Date;
}

interface ClientChatProps {
    onProcessingStart?: () => void;
    onProcessingEnd?: () => void;
}

export const ClientChat: React.FC<ClientChatProps> = ({ onProcessingStart, onProcessingEnd }) => {
    const [input, setInput] = useState('');
    const [history, setHistory] = useState<ChatMessage[]>([
        { 
            sender: 'bot', 
            text: '👋 Olá! Sou o Product Owner da Autonomous Data Agency.\n\nPosso ajudá-lo a construir pipelines de dados, dashboards, modelos de ML e muito mais.\n\n**O que você gostaria de criar hoje?**',
            timestamp: new Date()
        }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-scroll para última mensagem
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history]);

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
        }
    }, [input]);

    const formatMessage = (text: string) => {
        // Formatar markdown básico
        return text.split('\n').map((line, idx) => {
            if (line.startsWith('**') && line.endsWith('**')) {
                return <p key={idx} className="font-semibold text-blue-300">{line.replace(/\*\*/g, '')}</p>;
            }
            if (line.startsWith('- ')) {
                return <li key={idx} className="ml-4 list-disc">{line.substring(2)}</li>;
            }
            if (line.trim() === '') {
                return <br key={idx} />;
            }
            return <p key={idx}>{line}</p>;
        });
    };

    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: ChatMessage = { 
            sender: 'user', 
            text: input,
            timestamp: new Date()
        };
        setHistory(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        onProcessingStart?.();

        try {
            const response = await axios.post('http://localhost:8000/chat', { message: input });
            
            const botResponse = response.data?.response || 'Recebido! Os agentes estão trabalhando na sua solicitação...';
            setHistory(prev => [...prev, { 
                sender: 'bot', 
                text: botResponse,
                timestamp: new Date()
            }]);
        } catch (error) {
            console.error('Error sending message:', error);
            setHistory(prev => [...prev, { 
                sender: 'bot', 
                text: '❌ Erro ao conectar com o servidor.\n\nVerifique se a API está rodando em http://localhost:8000',
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
            onProcessingEnd?.();
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="flex flex-col h-full bg-gradient-to-b from-gray-900 to-gray-950 rounded-2xl border border-gray-800 overflow-hidden shadow-xl">
            {/* Header */}
            <div className="p-4 border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <span className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-900"></span>
                    </div>
                    <div>
                        <h2 className="text-base font-semibold text-white">Data Agency Assistant</h2>
                        <p className="text-xs text-gray-400">Pronto para ajudar</p>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                {history.map((msg, idx) => (
                    <div 
                        key={idx} 
                        className={`flex gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-fadeIn`}
                    >
                        {/* Avatar */}
                        <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                            msg.sender === 'user' 
                                ? 'bg-blue-600' 
                                : 'bg-gradient-to-br from-purple-500 to-pink-500'
                        }`}>
                            {msg.sender === 'user' 
                                ? <User className="w-4 h-4 text-white" /> 
                                : <Bot className="w-4 h-4 text-white" />
                            }
                        </div>
                        
                        {/* Message Bubble */}
                        <div className={`max-w-[75%] ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                            <div className={`p-3 rounded-2xl ${
                                msg.sender === 'user' 
                                    ? 'bg-blue-600 text-white rounded-br-md' 
                                    : 'bg-gray-800 text-gray-100 rounded-bl-md border border-gray-700'
                            }`}>
                                <div className="text-sm leading-relaxed whitespace-pre-wrap">
                                    {msg.sender === 'bot' ? formatMessage(msg.text) : msg.text}
                                </div>
                            </div>
                            <span className="text-[10px] text-gray-500 mt-1 px-2 block">
                                {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    </div>
                ))}
                
                {/* Loading indicator */}
                {isLoading && (
                    <div className="flex gap-3 animate-fadeIn">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-bl-md p-3">
                            <div className="flex items-center gap-2 text-gray-400">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="text-sm">Processando sua solicitação...</span>
                            </div>
                        </div>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t border-gray-800 bg-gray-900/80 backdrop-blur-sm">
                <div className="flex gap-3 items-end">
                    <div className="flex-1 relative">
                        <textarea
                            ref={textareaRef}
                            className="w-full bg-gray-800 text-white rounded-xl px-4 py-3 pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 border border-gray-700 transition-all placeholder:text-gray-500"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Descreva o que você precisa construir..."
                            disabled={isLoading}
                            rows={1}
                        />
                        <span className="absolute right-3 bottom-3 text-[10px] text-gray-500">
                            Enter ↵
                        </span>
                    </div>
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        className={`p-3 rounded-xl transition-all duration-200 ${
                            isLoading || !input.trim()
                                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white shadow-lg hover:shadow-blue-500/25'
                        }`}
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Send className="w-5 h-5" />
                        )}
                    </button>
                </div>
                <p className="text-[10px] text-gray-500 mt-2 text-center">
                    Shift + Enter para nova linha
                </p>
            </div>
        </div>
    );
};
