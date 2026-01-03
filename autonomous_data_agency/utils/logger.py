"""Logging utilities for the autonomous data agency."""

import logging
import sys
from typing import Optional


class AgencyLogger:
    """
    Custom logger for the autonomous data agency.
    
    Provides structured logging with context about agents and tasks.
    """

    def __init__(
        self,
        name: str = "autonomous_data_agency",
        level: str = "INFO",
        log_file: Optional[str] = None,
    ):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            level: Logging level
            log_file: Optional file path for logging
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs: any) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: any) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: any) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs: any) -> None:
        """Log error message."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs: any) -> None:
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)

    def log_agent_action(
        self,
        agent_name: str,
        action: str,
        details: Optional[str] = None,
    ) -> None:
        """
        Log an agent action.
        
        Args:
            agent_name: Name of the agent
            action: Action being performed
            details: Optional additional details
        """
        message = f"Agent '{agent_name}' - {action}"
        if details:
            message += f": {details}"
        self.info(message)

    def log_task_event(
        self,
        task_id: str,
        event: str,
        details: Optional[str] = None,
    ) -> None:
        """
        Log a task event.
        
        Args:
            task_id: ID of the task
            event: Event description
            details: Optional additional details
        """
        message = f"Task '{task_id}' - {event}"
        if details:
            message += f": {details}"
        self.info(message)


# Global logger instance
_global_logger: Optional[AgencyLogger] = None


def get_logger(
    name: str = "autonomous_data_agency",
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> AgencyLogger:
    """
    Get or create the global logger instance.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file path for logging
        
    Returns:
        AgencyLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = AgencyLogger(name, level, log_file)
    return _global_logger
