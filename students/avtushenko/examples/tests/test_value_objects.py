import pytest
from domain.value_objects import VideoURL, TestQuestion, ProgressPercent, Rating

def test_video_url_valid():
    url = VideoURL("https://www.youtube.com/watch?v=abc123")
    assert url.url == "https://www.youtube.com/watch?v=abc123"

def test_video_url_invalid():
    with pytest.raises(ValueError):
        VideoURL("")

def test_test_question_valid():
    q = TestQuestion("What is 2+2?", ["2", "3", "4", "5"], 2)
    assert q.is_correct(2) == True

def test_test_question_wrong_options():
    with pytest.raises(ValueError):
        TestQuestion("Q", ["1"], 0)

def test_progress_percent_valid():
    p = ProgressPercent(75)
    assert p.value == 75
    assert p.is_completed() == False

def test_progress_percent_invalid():
    with pytest.raises(ValueError):
        ProgressPercent(101)

def test_rating_valid():
    r = Rating(4.5)
    assert r.value == 4.5
    assert "★" in r.as_stars()

def test_rating_invalid():
    with pytest.raises(ValueError):
        Rating(5.5)