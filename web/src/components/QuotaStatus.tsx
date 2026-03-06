import React, { useState, useEffect } from 'react';
import { Zap, AlertTriangle, Clock, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface QuotaData {
    status: 'ok' | 'warning' | 'rate_limited';
    status_color: string;
    is_rate_limited: boolean;
    retry_after_seconds: number;
    rpm: {
        current: number;
        limit: number;
        percent: number;
        remaining: number;
    };
    rpd: {
        current: number;
        limit: number;
        percent: number;
        remaining: number;
    };
    message: string;
    last_error: string | null;
}

interface QuotaStatusProps {
    className?: string;
}

export const QuotaStatus: React.FC<QuotaStatusProps> = ({ className = '' }) => {
    const [quota, setQuota] = useState<QuotaData | null>(null);
    const [countdown, setCountdown] = useState(0);
    const [isLoading, setIsLoading] = useState(false);

    // Carrega status da quota
    const loadQuota = async () => {
        try {
            setIsLoading(true);
            const response = await axios.get('http://localhost:8000/api/quota');
            setQuota(response.data);
            if (response.data.is_rate_limited) {
                setCountdown(response.data.retry_after_seconds);
            }
        } catch (error) {
            console.error('Error loading quota:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Carrega ao montar e a cada 10s
    useEffect(() => {
        loadQuota();
        const interval = setInterval(loadQuota, 10000);
        return () => clearInterval(interval);
    }, []);

    // Countdown timer quando em rate limit
    useEffect(() => {
        if (countdown > 0) {
            const timer = setTimeout(() => {
                setCountdown(c => c - 1);
                if (countdown === 1) {
                    loadQuota(); // Recarrega quando countdown termina
                }
            }, 1000);
            return () => clearTimeout(timer);
        }
    }, [countdown]);

    if (!quota) return null;

    const getStatusIcon = () => {
        if (quota.is_rate_limited) {
            return <AlertTriangle className="w-4 h-4 text-red-400" />;
        }
        if (quota.status === 'warning') {
            return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
        }
        return <Zap className="w-4 h-4 text-green-400" />;
    };

    const getProgressColor = (percent: number) => {
        if (percent >= 90) return 'bg-red-500';
        if (percent >= 70) return 'bg-yellow-500';
        return 'bg-green-500';
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        if (mins > 0) {
            return `${mins}m ${secs}s`;
        }
        return `${secs}s`;
    };

    return (
        <div className={`bg-gray-900/80 rounded-xl border border-gray-800 ${className}`}>
            {/* Header */}
            <div className="px-3 py-2 border-b border-gray-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    {getStatusIcon()}
                    <span className="text-xs font-medium text-gray-300">
                        API Quota
                    </span>
                </div>
                <button
                    onClick={loadQuota}
                    disabled={isLoading}
                    className="p-1 text-gray-500 hover:text-gray-300 transition-colors"
                    title="Atualizar"
                >
                    <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Content */}
            <div className="p-3 space-y-3">
                {/* Rate Limit Warning */}
                {quota.is_rate_limited && (
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-2">
                        <div className="flex items-center gap-2 text-red-400">
                            <Clock className="w-4 h-4" />
                            <span className="text-xs font-medium">
                                Rate Limit - Aguarde {formatTime(countdown)}
                            </span>
                        </div>
                    </div>
                )}

                {/* RPM Progress */}
                <div>
                    <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] text-gray-500 uppercase">
                            Por Minuto
                        </span>
                        <span className="text-xs text-gray-400">
                            {quota.rpm.current}/{quota.rpm.limit}
                        </span>
                    </div>
                    <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div
                            className={`h-full ${getProgressColor(quota.rpm.percent)} transition-all duration-300`}
                            style={{ width: `${Math.min(quota.rpm.percent, 100)}%` }}
                        />
                    </div>
                    <div className="mt-0.5 text-[10px] text-gray-500">
                        {quota.rpm.remaining} restantes
                    </div>
                </div>

                {/* RPD Progress */}
                <div>
                    <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] text-gray-500 uppercase">
                            Por Dia
                        </span>
                        <span className="text-xs text-gray-400">
                            {quota.rpd.current}/{quota.rpd.limit}
                        </span>
                    </div>
                    <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div
                            className={`h-full ${getProgressColor(quota.rpd.percent)} transition-all duration-300`}
                            style={{ width: `${Math.min(quota.rpd.percent, 100)}%` }}
                        />
                    </div>
                    <div className="mt-0.5 text-[10px] text-gray-500">
                        {quota.rpd.remaining} restantes
                    </div>
                </div>

                {/* Status Message */}
                <div className={`text-[10px] p-2 rounded ${
                    quota.is_rate_limited
                        ? 'bg-red-500/10 text-red-400'
                        : quota.status === 'warning'
                        ? 'bg-yellow-500/10 text-yellow-400'
                        : 'bg-green-500/10 text-green-400'
                }`}>
                    {quota.message}
                </div>
            </div>
        </div>
    );
};
