class DomainException(Exception):
    """Базовое исключение домена"""
    pass

class InvalidCourseDataException(DomainException):
    """Некорректные данные курса"""
    pass

class LessonNotUnlockedException(DomainException):
    """Урок заблокирован"""
    pass

class MaxAttemptsReachedException(DomainException):
    """Превышен лимит попыток теста"""
    pass

class CourseNotActiveException(DomainException):
    """Курс не активен"""
    pass

class InvalidProgressException(DomainException):
    """Некорректный прогресс"""
    pass