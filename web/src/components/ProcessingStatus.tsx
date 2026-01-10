import React from 'react';
import { 
    MessageSquare, 
    Brain, 
    CheckCircle2, 
    Loader2, 
    AlertCircle,
    Users,
    FileText,
    Sparkles,
    Code2,
    Shield,
    Eye,
    TestTube,
    BarChart3
} from 'lucide-react';

export interface ProcessStep {
    id: string;
    label: string;
    status: 'pending' | 'active' | 'completed' | 'error';
    detail?: string;
}

interface ProcessingStatusProps {
    isActive?: boolean;
    steps: ProcessStep[];
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ 
    isActive = false, 
    steps 
}) => {
    const getIcon = (stepId: string, status: string) => {
        if (status === 'active') {
            return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
        }
        if (status === 'completed') {
            return <CheckCircle2 className="w-5 h-5 text-green-400" />;
        }
        if (status === 'error') {
            return <AlertCircle className="w-5 h-5 text-red-400" />;
        }
        
        // Pending icons by type
        const iconMap: Record<string, React.ReactNode> = {
            'received': <MessageSquare className="w-5 h-5 text-gray-500" />,
            'analyzing': <Brain className="w-5 h-5 text-gray-500" />,
            'product_owner': <FileText className="w-5 h-5 text-purple-400" />,
            'project_manager': <BarChart3 className="w-5 h-5 text-blue-400" />,
            'data_engineering': <Code2 className="w-5 h-5 text-green-400" />,
            'data_science': <Sparkles className="w-5 h-5 text-yellow-400" />,
            'governance': <Shield className="w-5 h-5 text-red-400" />,
            'observability': <Eye className="w-5 h-5 text-cyan-400" />,
            'qa': <TestTube className="w-5 h-5 text-orange-400" />,
            'planning': <Users className="w-5 h-5 text-gray-500" />,
        };
        
        return iconMap[stepId] || <CheckCircle2 className="w-5 h-5 text-gray-500" />;
    };

    const getStepColor = (status: string) => {
        switch (status) {
            case 'active':
                return 'border-blue-500 bg-blue-500/10';
            case 'completed':
                return 'border-green-500 bg-green-500/10';
            case 'error':
                return 'border-red-500 bg-red-500/10';
            default:
                return 'border-gray-600 bg-gray-800/50';
        }
    };

    return (
        <div className="bg-gray-800/50 rounded-xl p-4 backdrop-blur-sm border border-gray-700">
            <div className="flex items-center gap-2 mb-4">
                {isActive ? (
                    <>
                        <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                        <span className="text-blue-400 font-medium">Processando...</span>
                    </>
                ) : (
                    <>
                        <CheckCircle2 className="w-5 h-5 text-green-400" />
                        <span className="text-green-400 font-medium">Completo</span>
                    </>
                )}
            </div>

            <div className="space-y-2">
                {steps.map((step) => (
                    <div 
                        key={step.id}
                        className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 ${getStepColor(step.status)}`}
                    >
                        <div className="shrink-0">
                            {getIcon(step.id, step.status)}
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className={`font-medium text-sm ${
                                step.status === 'active' ? 'text-blue-300' :
                                step.status === 'completed' ? 'text-green-300' :
                                step.status === 'error' ? 'text-red-300' :
                                'text-gray-400'
                            }`}>
                                {step.label}
                            </div>
                            {step.detail && (
                                <div className="text-xs text-gray-500 truncate mt-0.5">
                                    {step.detail}
                                </div>
                            )}
                        </div>
                        {step.status === 'completed' && (
                            <span className="text-xs text-green-500">✓</span>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};
