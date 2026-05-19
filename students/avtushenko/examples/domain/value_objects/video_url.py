from dataclasses import dataclass
import re

@dataclass(frozen=True)
class VideoURL:
    """Value Object: URL видеоурока (иммутабельный)"""
    url: str

    def __post_init__(self):
        if not self.url or not self.url.strip():
            raise ValueError("Video URL cannot be empty")

        # Поддерживаем YouTube, Vimeo, прямые ссылки
        pattern = r'^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be|vimeo\.com|[\w\-]+\.\w+)\/.+$'
        if not re.match(pattern, self.url):
            raise ValueError(f"Invalid video URL format: {self.url}")

    def get_embed_url(self) -> str:
        """Получить embed-ссылку (если применимо)"""
        if "youtube.com/watch?v=" in self.url:
            video_id = self.url.split("v=")[1].split("&")[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.url