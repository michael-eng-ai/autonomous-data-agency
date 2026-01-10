import React from 'react';
import { Activity } from 'lucide-react';

interface ProjectEvent {
    type: string;
    data: any;
    timestamp: string;
}

export const ProjectFeed: React.FC<{ events: ProjectEvent[] }> = ({ events }) => {
    return (
        <div className="flex flex-col h-full bg-gray-900">
            <div className="p-4 border-b border-gray-700 bg-gray-800">
                <h2 className="text-lg font-bold flex items-center gap-2 text-white">
                    <Activity className="w-5 h-5" /> Status do Projeto
                </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
                {events.length === 0 && (
                    <div className="text-gray-500 text-center italic mt-10">Aguardando início do projeto...</div>
                )}
                {events.map((evt, idx) => (
                    <div key={idx} className="bg-gray-800 p-3 rounded border border-gray-700">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span className="font-bold text-blue-400">{evt.type.toUpperCase()}</span>
                            <span>{new Date(evt.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <pre className="text-gray-300 whitespace-pre-wrap font-mono text-xs overflow-x-auto">
                            {JSON.stringify(evt.data, null, 2)}
                        </pre>
                    </div>
                ))}
            </div>
        </div>
    );
};
