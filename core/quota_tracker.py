"""
Quota Tracker Module

Rastreia o uso de API e estima a quota restante.
Gemini Free Tier limits (por minuto):
- 15 RPM (requests per minute)
- 1 million TPM (tokens per minute)
- 1,500 RPD (requests per day)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from collections import deque
import threading


@dataclass
class QuotaInfo:
    """Informações de quota."""
    requests_per_minute: int = 15  # Gemini free tier
    requests_per_day: int = 1500
    current_rpm: int = 0
    current_rpd: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    retry_after_seconds: int = 0
    is_rate_limited: bool = False


class QuotaTracker:
    """
    Rastreia uso de API e estima quota disponível.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # Guarda timestamps das últimas requisições
        self._minute_requests: deque = deque(maxlen=100)
        self._day_requests: deque = deque(maxlen=2000)

        # Limites do Gemini Free Tier
        self.rpm_limit = 15  # requests per minute
        self.rpd_limit = 1500  # requests per day

        # Estado de rate limit
        self._rate_limited = False
        self._rate_limit_until: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._retry_after: int = 0

    def record_request(self):
        """Registra uma requisição feita."""
        now = datetime.now()
        with self._lock:
            self._minute_requests.append(now)
            self._day_requests.append(now)

    def record_rate_limit(self, error_message: str, retry_after_seconds: int = 60):
        """Registra um erro de rate limit."""
        now = datetime.now()
        with self._lock:
            self._rate_limited = True
            self._rate_limit_until = now + timedelta(seconds=retry_after_seconds)
            self._last_error = error_message
            self._retry_after = retry_after_seconds

    def clear_rate_limit(self):
        """Limpa o estado de rate limit."""
        with self._lock:
            self._rate_limited = False
            self._rate_limit_until = None
            self._retry_after = 0

    def _count_recent_requests(self, requests: deque, window: timedelta) -> int:
        """Conta requisições dentro de uma janela de tempo."""
        now = datetime.now()
        cutoff = now - window
        count = 0
        for ts in requests:
            if ts > cutoff:
                count += 1
        return count

    def get_quota_info(self) -> QuotaInfo:
        """Retorna informações atuais de quota."""
        with self._lock:
            # Conta requisições no último minuto
            rpm = self._count_recent_requests(
                self._minute_requests,
                timedelta(minutes=1)
            )

            # Conta requisições nas últimas 24h
            rpd = self._count_recent_requests(
                self._day_requests,
                timedelta(hours=24)
            )

            # Verifica se ainda está em rate limit
            is_limited = self._rate_limited
            if self._rate_limit_until and datetime.now() > self._rate_limit_until:
                is_limited = False
                self._rate_limited = False

            # Calcula retry_after restante
            retry_after = 0
            if is_limited and self._rate_limit_until:
                remaining = (self._rate_limit_until - datetime.now()).total_seconds()
                retry_after = max(0, int(remaining))

            return QuotaInfo(
                requests_per_minute=self.rpm_limit,
                requests_per_day=self.rpd_limit,
                current_rpm=rpm,
                current_rpd=rpd,
                last_error=self._last_error,
                last_error_time=self._rate_limit_until,
                retry_after_seconds=retry_after,
                is_rate_limited=is_limited
            )

    def get_status_dict(self) -> Dict:
        """Retorna status como dicionário para API."""
        info = self.get_quota_info()

        # Calcula porcentagens
        rpm_percent = (info.current_rpm / info.requests_per_minute) * 100
        rpd_percent = (info.current_rpd / info.requests_per_day) * 100

        # Define status geral
        if info.is_rate_limited:
            status = "rate_limited"
            status_color = "red"
        elif rpm_percent >= 80 or rpd_percent >= 80:
            status = "warning"
            status_color = "yellow"
        else:
            status = "ok"
            status_color = "green"

        return {
            "status": status,
            "status_color": status_color,
            "is_rate_limited": info.is_rate_limited,
            "retry_after_seconds": info.retry_after_seconds,
            "rpm": {
                "current": info.current_rpm,
                "limit": info.requests_per_minute,
                "percent": round(rpm_percent, 1),
                "remaining": max(0, info.requests_per_minute - info.current_rpm)
            },
            "rpd": {
                "current": info.current_rpd,
                "limit": info.requests_per_day,
                "percent": round(rpd_percent, 1),
                "remaining": max(0, info.requests_per_day - info.current_rpd)
            },
            "last_error": info.last_error,
            "message": self._get_status_message(info)
        }

    def _get_status_message(self, info: QuotaInfo) -> str:
        """Gera mensagem de status amigável."""
        if info.is_rate_limited:
            return f"Rate limit atingido. Aguarde {info.retry_after_seconds}s para continuar."

        rpm_remaining = info.requests_per_minute - info.current_rpm
        rpd_remaining = info.requests_per_day - info.current_rpd

        if rpm_remaining <= 2:
            return f"Quase no limite por minuto! {rpm_remaining} requisições restantes."

        if rpd_remaining <= 100:
            return f"Atenção: {rpd_remaining} requisições restantes hoje."

        return f"OK - {rpm_remaining} req/min disponíveis"


# Singleton
_quota_tracker: Optional[QuotaTracker] = None


def get_quota_tracker() -> QuotaTracker:
    """Retorna instância singleton do QuotaTracker."""
    global _quota_tracker
    if _quota_tracker is None:
        _quota_tracker = QuotaTracker()
    return _quota_tracker
