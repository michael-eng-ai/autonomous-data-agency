import React, { useState, useEffect } from 'react';
import { MessageSquare, Plus, Trash2, ChevronRight, Clock, Folder, Loader2 } from 'lucide-react';
import axios from 'axios';

interface ConversationSummary {
    session_id: string;
    project_id: string | null;
    project_name: string;
    phase: string;
    created_at: string;
    updated_at: string;
}

interface ConversationHistoryProps {
    currentSessionId: string | null;
    onSelectConversation: (sessionId: string) => void;
    onNewConversation: () => void;
}

export const ConversationHistory: React.FC<ConversationHistoryProps> = ({
    currentSessionId,
    onSelectConversation,
    onNewConversation
}) => {
    const [conversations, setConversations] = useState<ConversationSummary[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isDeleting, setIsDeleting] = useState<string | null>(null);

    // Carrega lista de conversas
    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {
        try {
            setIsLoading(true);
            const response = await axios.get('http://localhost:8000/conversations');
            setConversations(response.data.conversations || []);
        } catch (error) {
            console.error('Error loading conversations:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (sessionId: string, e: React.MouseEvent) => {
        e.stopPropagation();

        if (!confirm('Tem certeza que deseja excluir esta conversa?')) {
            return;
        }

        try {
            setIsDeleting(sessionId);
            await axios.delete(`http://localhost:8000/conversations/${sessionId}`);
            setConversations(prev => prev.filter(c => c.session_id !== sessionId));

            // Se deletou a conversa atual, cria uma nova
            if (sessionId === currentSessionId) {
                onNewConversation();
            }
        } catch (error) {
            console.error('Error deleting conversation:', error);
        } finally {
            setIsDeleting(null);
        }
    };

    const formatDate = (isoString: string) => {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        } else if (days === 1) {
            return 'Ontem';
        } else if (days < 7) {
            return `${days} dias atrás`;
        } else {
            return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
        }
    };

    const getPhaseLabel = (phase: string) => {
        const labels: Record<string, { text: string; color: string }> = {
            'greeting': { text: 'Iniciada', color: 'text-gray-400' },
            'discovery': { text: 'Descoberta', color: 'text-blue-400' },
            'clarification': { text: 'Esclarecimento', color: 'text-yellow-400' },
            'confirmation': { text: 'Confirmação', color: 'text-purple-400' },
            'ready': { text: 'Pronto', color: 'text-green-400' },
            'in_development': { text: 'Em Desenvolvimento', color: 'text-emerald-400' }
        };
        return labels[phase] || { text: phase, color: 'text-gray-400' };
    };

    return (
        <div className="flex flex-col h-full bg-gray-900/50 rounded-xl border border-gray-800">
            {/* Header */}
            <div className="p-3 border-b border-gray-800">
                <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-gray-300 flex items-center gap-2">
                        <MessageSquare className="w-4 h-4" />
                        Conversas
                    </h3>
                    <button
                        onClick={onNewConversation}
                        className="p-1.5 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors"
                        title="Nova conversa"
                    >
                        <Plus className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {isLoading ? (
                    <div className="flex items-center justify-center p-6 text-gray-500">
                        <Loader2 className="w-5 h-5 animate-spin" />
                    </div>
                ) : conversations.length === 0 ? (
                    <div className="p-4 text-center text-gray-500 text-sm">
                        <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p>Nenhuma conversa salva</p>
                        <p className="text-xs mt-1">Inicie uma nova conversa para começar</p>
                    </div>
                ) : (
                    <div className="p-2 space-y-1">
                        {conversations.map((conv) => {
                            const phaseInfo = getPhaseLabel(conv.phase);
                            const isSelected = conv.session_id === currentSessionId;

                            return (
                                <div
                                    key={conv.session_id}
                                    onClick={() => onSelectConversation(conv.session_id)}
                                    className={`group p-3 rounded-lg cursor-pointer transition-all ${
                                        isSelected
                                            ? 'bg-blue-500/20 border border-blue-500/30'
                                            : 'hover:bg-gray-800/50 border border-transparent'
                                    }`}
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                {conv.project_id ? (
                                                    <Folder className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                                                ) : (
                                                    <MessageSquare className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                                                )}
                                                <span className="text-sm text-white truncate">
                                                    {conv.project_name}
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-2 mt-1.5">
                                                <span className={`text-xs ${phaseInfo.color}`}>
                                                    {phaseInfo.text}
                                                </span>
                                                <span className="text-gray-600">•</span>
                                                <span className="text-xs text-gray-500 flex items-center gap-1">
                                                    <Clock className="w-3 h-3" />
                                                    {formatDate(conv.updated_at)}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-1">
                                            <button
                                                onClick={(e) => handleDelete(conv.session_id, e)}
                                                disabled={isDeleting === conv.session_id}
                                                className="p-1.5 rounded text-gray-500 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
                                                title="Excluir conversa"
                                            >
                                                {isDeleting === conv.session_id ? (
                                                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                                ) : (
                                                    <Trash2 className="w-3.5 h-3.5" />
                                                )}
                                            </button>
                                            <ChevronRight className={`w-4 h-4 transition-colors ${
                                                isSelected ? 'text-blue-400' : 'text-gray-600'
                                            }`} />
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="p-2 border-t border-gray-800">
                <button
                    onClick={loadConversations}
                    className="w-full px-3 py-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
                >
                    Atualizar lista
                </button>
            </div>
        </div>
    );
};
