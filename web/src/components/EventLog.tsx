import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Terminal, Clock } from 'lucide-react';

interface LogEvent {
    type: string;
    data: any;
    timestamp: string;
}

interface EventLogProps {
    events: LogEvent[];
}

export const EventLog: React.FC<EventLogProps> = ({ events }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [selectedEvent, setSelectedEvent] = useState<LogEvent | null>(null);

    const getEventIcon = (type: string) => {
        if (type.includes('completed')) return '✅';
        if (type.includes('started')) return '🚀';
        if (type.includes('error')) return '❌';
        if (type.includes('phase')) return '📊';
        if (type.includes('message')) return '💬';
        return '📌';
    };

    const getEventColor = (type: string) => {
        if (type.includes('completed')) return 'text-green-400';
        if (type.includes('started')) return 'text-blue-400';
        if (type.includes('error')) return 'text-red-400';
        if (type.includes('phase')) return 'text-purple-400';
        return 'text-gray-400';
    };

    const formatEventType = (type: string) => {
        return type
            .replace(/_/g, ' ')
            .toLowerCase()
            .replace(/\b\w/g, c => c.toUpperCase());
    };

    const latestEvents = isExpanded ? events : events.slice(0, 3);

    return (
        <div className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden">
            {/* Header */}
            <button 
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full p-3 flex items-center justify-between bg-gray-800 hover:bg-gray-750 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-300">Log de Eventos</span>
                    <span className="text-xs bg-gray-700 px-2 py-0.5 rounded-full text-gray-400">
                        {events.length}
                    </span>
                </div>
                {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                )}
            </button>

            {/* Event List */}
            <div className={`transition-all duration-300 ${isExpanded ? 'max-h-96' : 'max-h-40'} overflow-y-auto`}>
                {events.length === 0 ? (
                    <div className="p-4 text-center text-gray-500 text-sm">
                        Nenhum evento registrado ainda...
                    </div>
                ) : (
                    <div className="divide-y divide-gray-700/50">
                        {latestEvents.map((evt, idx) => (
                            <div 
                                key={idx}
                                onClick={() => setSelectedEvent(selectedEvent === evt ? null : evt)}
                                className="p-3 hover:bg-gray-700/30 cursor-pointer transition-colors"
                            >
                                <div className="flex items-center gap-2">
                                    <span className="text-sm">{getEventIcon(evt.type)}</span>
                                    <span className={`text-sm font-medium ${getEventColor(evt.type)}`}>
                                        {formatEventType(evt.type)}
                                    </span>
                                    <span className="ml-auto text-xs text-gray-500 flex items-center gap-1">
                                        <Clock className="w-3 h-3" />
                                        {new Date(evt.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                                
                                {/* Expanded details */}
                                {selectedEvent === evt && (
                                    <div className="mt-2 p-2 bg-gray-900/50 rounded text-xs font-mono text-gray-400 overflow-x-auto">
                                        <pre className="whitespace-pre-wrap">
                                            {JSON.stringify(evt.data, null, 2)}
                                        </pre>
                                    </div>
                                )}

                                {/* Summary preview */}
                                {evt.data?.summary && selectedEvent !== evt && (
                                    <div className="mt-1 text-xs text-gray-500 truncate pl-6">
                                        {evt.data.summary.substring(0, 80)}...
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Show more button */}
            {events.length > 3 && !isExpanded && (
                <button 
                    onClick={() => setIsExpanded(true)}
                    className="w-full p-2 text-xs text-blue-400 hover:text-blue-300 hover:bg-gray-700/30 transition-colors"
                >
                    Ver mais {events.length - 3} eventos...
                </button>
            )}
        </div>
    );
};
