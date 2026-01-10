import React from 'react';
import { User, Bot, Briefcase, Code2, BarChart3, Shield, Eye, TestTube, Sparkles } from 'lucide-react';

interface ResultSummaryProps {
    results: {
        agent: string;
        output: string;
        timestamp?: string;
    }[];
}

const agentConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
    product_owner: {
        icon: <Briefcase className="w-5 h-5" />,
        color: 'bg-purple-500',
        label: 'Product Owner'
    },
    project_manager: {
        icon: <BarChart3 className="w-5 h-5" />,
        color: 'bg-blue-500',
        label: 'Project Manager'
    },
    data_engineering: {
        icon: <Code2 className="w-5 h-5" />,
        color: 'bg-green-500',
        label: 'Data Engineering'
    },
    data_science: {
        icon: <Sparkles className="w-5 h-5" />,
        color: 'bg-yellow-500',
        label: 'Data Science'
    },
    governance: {
        icon: <Shield className="w-5 h-5" />,
        color: 'bg-red-500',
        label: 'Governance'
    },
    observability: {
        icon: <Eye className="w-5 h-5" />,
        color: 'bg-cyan-500',
        label: 'Observability'
    },
    qa: {
        icon: <TestTube className="w-5 h-5" />,
        color: 'bg-orange-500',
        label: 'QA'
    },
    default: {
        icon: <Bot className="w-5 h-5" />,
        color: 'bg-gray-500',
        label: 'Agent'
    }
};

export const ResultSummary: React.FC<ResultSummaryProps> = ({ results }) => {
    const getAgentConfig = (agent: string) => {
        const key = agent.toLowerCase().replace(/\s+/g, '_');
        return agentConfig[key] || agentConfig.default;
    };

    const formatOutput = (output: string) => {
        // Tentar extrair seções do markdown
        const lines = output.split('\n');
        return lines.map((line, idx) => {
            if (line.startsWith('##')) {
                return (
                    <h4 key={idx} className="text-sm font-semibold text-white mt-3 mb-1">
                        {line.replace(/^#+\s*/, '')}
                    </h4>
                );
            }
            if (line.startsWith('- ') || line.startsWith('* ')) {
                return (
                    <li key={idx} className="text-sm text-gray-300 ml-4 list-disc">
                        {line.replace(/^[-*]\s*/, '')}
                    </li>
                );
            }
            if (line.startsWith('**') && line.endsWith('**')) {
                return (
                    <p key={idx} className="text-sm font-medium text-blue-300 mt-2">
                        {line.replace(/\*\*/g, '')}
                    </p>
                );
            }
            if (line.trim()) {
                return (
                    <p key={idx} className="text-sm text-gray-300">
                        {line}
                    </p>
                );
            }
            return null;
        });
    };

    if (results.length === 0) {
        return (
            <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6 text-center">
                <Bot className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">
                    Aguardando resultados dos agentes...
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {results.map((result, idx) => {
                const config = getAgentConfig(result.agent);
                return (
                    <div 
                        key={idx}
                        className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden"
                    >
                        {/* Header do agente */}
                        <div className={`${config.color} p-3 flex items-center gap-3`}>
                            <div className="p-2 bg-white/20 rounded-lg text-white">
                                {config.icon}
                            </div>
                            <div>
                                <h3 className="font-semibold text-white">{config.label}</h3>
                                {result.timestamp && (
                                    <p className="text-xs text-white/70">
                                        {new Date(result.timestamp).toLocaleTimeString()}
                                    </p>
                                )}
                            </div>
                        </div>
                        
                        {/* Conteúdo */}
                        <div className="p-4 max-h-64 overflow-y-auto custom-scrollbar">
                            <div className="prose prose-invert prose-sm max-w-none">
                                {formatOutput(result.output)}
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
