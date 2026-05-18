"""
Демонстрация работы гексагональной архитектуры
"""
from infrastructure.config.dependency_injection import DependencyContainer
from application.port.in.update_progress_use_case import UpdateProgressCommand
from application.port.in.submit_test_use_case import SubmitTestCommand

def main():
    # Инициализация DI контейнера
    container = DependencyContainer()
    
    # Получаем сервисы
    progress_service = container.get_progress_service()
    
    print("🎓 Мини-курсы 'Учусь быстро'")
    print("=" * 40)
    
    # Пример: обновление прогресса
    command = UpdateProgressCommand(
        user_id="user-123",
        course_id="course-001",
        lesson_id="lesson-1",
        video_percent=100.0
    )
    
    try:
        result = progress_service.execute(command)
        print(f"✅ Прогресс обновлён: {result.video_percent}%")
        print(f"   Урок завершён: {result.is_completed}")
        print(f"   Следующий урок открыт: {result.next_lesson_unlocked}")
    except NotImplementedError:
        print("⚠️  Метод будет реализован в Lab #4")
    
    print("\n🏗  Гексагональная архитектура работает!")
    print("   Domain ← Application ← Infrastructure")

if __name__ == "__main__":
    main()