import pytest
from app.domain.value_objects import VideoURL, TestQuestion, ProgressPercent, Rating

class TestVideoURL:
    def test_valid_youtube_url(self):
        url = VideoURL("https://www.youtube.com/watch?v=abc123")
        assert url.url == "https://www.youtube.com/watch?v=abc123"
    
    def test_valid_vimeo_url(self):
        url = VideoURL("https://vimeo.com/12345678")
        assert url.url == "https://vimeo.com/12345678"
    
    def test_empty_url_raises_error(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            VideoURL("")
    
    def test_invalid_format_raises_error(self):
        with pytest.raises(ValueError, match="Invalid video URL"):
            VideoURL("not-a-url")
    
    def test_get_embed_url_youtube(self):
        url = VideoURL("https://www.youtube.com/watch?v=abc123&t=10s")
        embed = url.get_embed_url()
        assert embed == "https://www.youtube.com/embed/abc123"
    
    def test_immutability(self):
        url = VideoURL("https://example.com/video.mp4")
        with pytest.raises(Exception):  # frozen=True prevents modification
            url.url = "new-url"

class TestTestQuestion:
    def test_valid_question(self):
        q = TestQuestion("What is Python?", ["A language", "A snake", "Both"], 2)
        assert q.text == "What is Python?"
        assert len(q.options) == 3
        assert q.correct_option_index == 2
    
    def test_empty_text_raises_error(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            TestQuestion("", ["A", "B"], 0)
    
    def test_less_than_two_options_raises_error(self):
        with pytest.raises(ValueError, match="at least 2 options"):
            TestQuestion("Q", ["A"], 0)
    
    def test_invalid_correct_index_raises_error(self):
        with pytest.raises(ValueError, match="index out of range"):
            TestQuestion("Q", ["A", "B"], 5)
    
    def test_duplicate_options_raises_error(self):
        with pytest.raises(ValueError, match="Options must be unique"):
            TestQuestion("Q", ["A", "A", "B"], 0)
    
    def test_is_correct(self):
        q = TestQuestion("Q", ["A", "B", "C"], 1)
        assert q.is_correct(1) is True
        assert q.is_correct(0) is False

class TestProgressPercent:
    def test_valid_progress(self):
        p = ProgressPercent(75)
        assert p.value == 75
        assert p.as_float() == 0.75
        assert p.is_completed() is False
    
    def test_zero_progress(self):
        p = ProgressPercent(0)
        assert p.is_completed() is False
    
    def test_completed_progress(self):
        p = ProgressPercent(100)
        assert p.is_completed() is True
    
    def test_invalid_negative_raises_error(self):
        with pytest.raises(ValueError, match="between 0 and 100"):
            ProgressPercent(-10)
    
    def test_invalid_above_100_raises_error(self):
        with pytest.raises(ValueError, match="between 0 and 100"):
            ProgressPercent(150)
    
    def test_addition(self):
        p1 = ProgressPercent(30)
        p2 = ProgressPercent(20)
        p3 = p1 + p2
        assert p3.value == 50
    
    def test_addition_caps_at_100(self):
        p1 = ProgressPercent(80)
        p2 = ProgressPercent(50)
        p3 = p1 + p2
        assert p3.value == 100

class TestRating:
    def test_valid_rating(self):
        r = Rating(4.5)
        assert r.value == 4.5
    
    def test_min_rating(self):
        r = Rating(1.0)
        assert r.value == 1.0
    
    def test_max_rating(self):
        r = Rating(5.0)
        assert r.value == 5.0
    
    def test_invalid_below_1_raises_error(self):
        with pytest.raises(ValueError, match="between 1.0 and 5.0"):
            Rating(0.5)
    
    def test_invalid_above_5_raises_error(self):
        with pytest.raises(ValueError, match="between 1.0 and 5.0"):
            Rating(5.5)
    
    def test_as_stars(self):
        r = Rating(4.5)
        stars = r.as_stars()
        assert "★" in stars
        assert "½" in stars