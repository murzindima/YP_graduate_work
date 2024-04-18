from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from core.config import settings


def configure_tracer() -> None:
    """Настройка трассировки."""

    # Добавляем в метаданные имя сервиса
    resource = Resource.create({SERVICE_NAME: settings.auth_fastapi_host})
    # Инициализация экземпляра трейсера
    trace.set_tracer_provider(TracerProvider(resource=resource))
    # Определяем спан-процессор (хранит и обрабатывают спаны (трассировки))
    # BatchSpanProcessor пакетно экспортирует спаны в JaegerExporter
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
        )
    )
    # Добавляем еще один спан-процессор - ConsoleSpanExporter,
    # который выводит спаны в консоль приложения
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
