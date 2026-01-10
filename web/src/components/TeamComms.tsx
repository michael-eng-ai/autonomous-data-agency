import React from 'react';
import { Users } from 'lucide-react';

interface TeamDialog {
    team: string;
    message: string;
    agent: string;
    summary?: string;
}

export const TeamComms: React.FC<{ dialogs: TeamDialog[] }> = ({ dialogs }) => {
    return (
        <div className="flex flex-col h-full bg-gray-900 border-l border-gray-700">
            <div className="p-4 border-b border-gray-700 bg-gray-800">
                <h2 className="text-lg font-bold flex items-center gap-2 text-white">
                    <Users className="w-5 h-5" /> Comunicação da Equipe (Master Bots)
                </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {dialogs.length === 0 && (
                    <div className="text-gray-500 text-center italic mt-10">Nenhuma comunicação ativa...</div>
                )}
                {dialogs.map((dialog, idx) => (
                    <div key={idx} className="bg-gray-800 rounded-lg p-3 border border-gray-600">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 rounded-full bg-green-600 flex items-center justify-center text-xs font-bold text-white">
                                {dialog.team?.[0]?.toUpperCase()}
                            </div>
                            <span className="font-bold text-green-400">{dialog.team || 'Unknown'} (Master)</span>
                        </div>
                        <div className="text-sm text-gray-300">
                            {dialog.summary || dialog.message || JSON.stringify(dialog)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
