from datetime import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime

Base = declarative_base()


class TimeCheckInterface:
    """
    Интерфейс фиксирования даты и времени
    создания и изменения записи
    """
    created_at = Column(DateTime, index=True, nullable=False,
                        default=datetime.utcnow,
                        comment="Время создания записи")
    updated_at = Column(DateTime, index=True, nullable=False,
                        default=datetime.utcnow, onupdate=datetime.utcnow,
                        comment="Время последнего изменения записи")
