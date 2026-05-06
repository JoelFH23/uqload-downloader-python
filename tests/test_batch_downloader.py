import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from uqload_dl.batch_downloader import BatchDownloader
from uqload_dl.exceptions import VideoNotFound


@pytest.fixture
def sample_urls_file():
    """Create a temporary file with sample URLs."""
    content = """@https://uqload.cx/sbmujieyd2cj.html
@https://uqload.cx/vule3vel9n5q.html
@https://uqload.cx/0zmi1ulf0d60.html"""
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


def test_batch_downloader_initialization():
    """Test BatchDownloader initialization."""
    downloader = BatchDownloader(max_workers=5, output_dir="/tmp")
    
    assert downloader.max_workers == 5
    assert downloader.output_dir == "/tmp"
    assert downloader.results == []


def test_read_urls_from_file(sample_urls_file):
    """Test reading URLs from a text file."""
    downloader = BatchDownloader()
    urls = downloader.read_urls_from_file(sample_urls_file)
    
    assert len(urls) == 3
    assert all(url.startswith("https://uqload.cx/") for url in urls)


def test_read_urls_from_file_not_found():
    """Test reading URLs from a non-existent file."""
    downloader = BatchDownloader()
    
    with pytest.raises(FileNotFoundError):
        downloader.read_urls_from_file("non_existent_file.txt")


def test_read_urls_from_file_no_valid_urls():
    """Test reading URLs from a file with no valid URLs."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("This file has no valid URLs\nJust some random text")
        temp_file = f.name
    
    try:
        downloader = BatchDownloader()
        with pytest.raises(ValueError, match="No valid URLs found"):
            downloader.read_urls_from_file(temp_file)
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@patch('uqload_dl.batch_downloader.UQLoad')
def test_download_single_video_success(mock_uqload_class):
    """Test successful single video download."""
    # Mock UQLoad instance
    mock_uqload = MagicMock()
    mock_uqload.get_video_info.return_value = {
        'title': 'Test Video',
        'size': 1024
    }
    mock_uqload_class.return_value = mock_uqload
    
    downloader = BatchDownloader()
    result = downloader.download_single_video("https://uqload.cx/test.html", 1, 1)
    
    assert result['success'] is True
    assert result['filename'] == 'Test Video'
    assert result['size'] == 1024
    assert result['error'] is None


@patch('uqload_dl.batch_downloader.UQLoad')
def test_download_single_video_not_found(mock_uqload_class):
    """Test single video download when video is not found."""
    # Mock UQLoad to raise VideoNotFound
    mock_uqload_class.side_effect = VideoNotFound("Video not found")
    
    downloader = BatchDownloader()
    result = downloader.download_single_video("https://uqload.cx/test.html", 1, 1)
    
    assert result['success'] is False
    assert "Video not found" in result['error']


@patch('uqload_dl.batch_downloader.UQLoad')
def test_download_single_video_exception(mock_uqload_class):
    """Test single video download when an exception occurs."""
    # Mock UQLoad to raise a generic exception
    mock_uqload_class.side_effect = Exception("Network error")
    
    downloader = BatchDownloader()
    result = downloader.download_single_video("https://uqload.cx/test.html", 1, 1)
    
    assert result['success'] is False
    assert "Network error" in result['error']


@patch('uqload_dl.batch_downloader.ThreadPoolExecutor')
def test_download_urls(mock_executor_class):
    """Test downloading multiple URLs."""
    # Mock ThreadPoolExecutor
    mock_executor = MagicMock()
    mock_executor_class.return_value.__enter__.return_value = mock_executor
    
    # Mock futures
    mock_future1 = MagicMock()
    mock_future1.result.return_value = {
        'url': 'https://uqload.cx/test1.html',
        'success': True,
        'filename': 'Video 1',
        'error': None
    }
    
    mock_future2 = MagicMock()
    mock_future2.result.return_value = {
        'url': 'https://uqload.cx/test2.html',
        'success': False,
        'filename': None,
        'error': 'Video not found'
    }
    
    mock_executor.submit.side_effect = [mock_future1, mock_future2]
    mock_executor.__enter__.return_value.as_completed.return_value = [mock_future1, mock_future2]
    
    downloader = BatchDownloader(max_workers=2)
    urls = ["https://uqload.cx/test1.html", "https://uqload.cx/test2.html"]
    
    results = downloader.download_urls(urls)
    
    assert len(results) == 2
    assert results[0]['success'] is True
    assert results[1]['success'] is False


def test_download_urls_empty_list():
    """Test downloading with empty URL list."""
    downloader = BatchDownloader()
    
    with pytest.raises(ValueError, match="No URLs provided"):
        downloader.download_urls([])


@patch('uqload_dl.batch_downloader.BatchDownloader.read_urls_from_file')
@patch('uqload_dl.batch_downloader.BatchDownloader.download_urls')
def test_download_from_file(mock_download_urls, mock_read_urls):
    """Test downloading from file."""
    mock_read_urls.return_value = ["https://uqload.cx/test1.html", "https://uqload.cx/test2.html"]
    mock_download_urls.return_value = [
        {'success': True, 'filename': 'Video 1'},
        {'success': True, 'filename': 'Video 2'}
    ]
    
    downloader = BatchDownloader()
    results = downloader.download_from_file("test.txt")
    
    mock_read_urls.assert_called_once_with("test.txt")
    mock_download_urls.assert_called_once_with(["https://uqload.cx/test1.html", "https://uqload.cx/test2.html"])
    assert len(results) == 2
