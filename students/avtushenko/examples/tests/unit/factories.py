import factory
from faker import Faker
from app.domain.entities import Course, Lesson
from app.domain.value_objects import VideoURL, TestQuestion, Rating, ProgressPercent
from app.domain.aggregates import Enrollment

fake = Faker()

class VideoURLFactory(factory.Factory):
    class Meta:
        model = VideoURL
    
    url = factory.LazyAttribute(lambda _: f"https://youtube.com/watch?v={fake.uuid4()[:8]}")

class TestQuestionFactory(factory.Factory):
    class Meta:
        model = TestQuestion
    
    text = factory.LazyAttribute(lambda _: fake.sentence())
    options = factory.LazyAttribute(lambda _: [fake.word() for _ in range(4)])
    correct_option_index = 0

class RatingFactory(factory.Factory):
    class Meta:
        model = Rating
    
    value = factory.LazyAttribute(lambda _: fake.random_int(1, 5) * 1.0)

class CourseFactory(factory.Factory):
    class Meta:
        model = Course
    
    id = factory.LazyAttribute(lambda _: f"COURSE-{fake.uuid4()[:8].upper()}")
    title = factory.LazyAttribute(lambda _: fake.catch_phrase())
    description = factory.LazyAttribute(lambda _: fake.paragraph())

class LessonFactory(factory.Factory):
    class Meta:
        model = Lesson
    
    id = factory.LazyAttribute(lambda _: f"LESSON-{fake.uuid4()[:8].upper()}")
    title = factory.LazyAttribute(lambda _: fake.sentence())
    video_url = factory.SubFactory(VideoURLFactory)

class EnrollmentFactory(factory.Factory):
    class Meta:
        model = Enrollment
    
    id = factory.LazyAttribute(lambda _: f"ENR-{fake.uuid4()[:8].upper()}")
    student_id = factory.LazyAttribute(lambda _: f"STU-{fake.uuid4()[:6].upper()}")
    course_id = factory.LazyAttribute(lambda _: f"COURSE-{fake.uuid4()[:8].upper()}")