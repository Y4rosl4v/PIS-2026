import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("COURSE_DATABASE_URL", "postgresql://courses_user:password@course-db:5432/courses")
    
    # RabbitMQ
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    
    # Service
    SERVICE_PORT = int(os.getenv("COURSE_SERVICE_PORT", 8001))
    SERVICE_HOST = os.getenv("COURSE_SERVICE_HOST", "0.0.0.0")