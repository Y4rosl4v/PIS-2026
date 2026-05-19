class DomainException(Exception):
    """Базовое исключение домена"""
    pass

class InvalidProgressError(DomainException):
    """Некорректное значение прогресса"""
    pass

class InvalidVideoUrlError(DomainException):
    """Некорректный URL видео"""
    pass

class LessonAlreadyCompletedError(DomainException):
    """Урок уже завершён"""
    pass

class TestNotAvailableError(DomainException):
    """Тест недоступен (урок не завершён)"""
    pass