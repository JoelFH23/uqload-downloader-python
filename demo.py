#!/usr/bin/env python3
"""
Demo script showcasing the enhanced UQLoad Downloader features.
This script demonstrates both single and batch downloading capabilities.
"""

import os
import tempfile
from uqload_dl import UQLoad, BatchDownloader
from uqload_dl.progress_bar import ProgressBar


def create_sample_urls_file():
    """Create a temporary file with sample URLs for demonstration."""
    sample_urls = [
        "@https://uqload.is/sbmujieyd2cj.html",
        "@https://uqload.is/vule3vel9n5q.html",
        "@https://uqload.is/0zmi1ulf0d60.html"
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        for url in sample_urls:
            f.write(url + '\n')
        temp_file = f.name
    
    return temp_file


def demo_single_download():
    """Demonstrate single video download with enhanced UI."""
    print("🎯 DEMO: Single Video Download")
    print("=" * 50)
    
    # Example URL (replace with a real one for testing)
    url = "https://uqload.is/sbmujieyd2cj.html"
    
    try:
        # Create UQLoad instance with progress bar
        uqload = UQLoad(
            url=url,
            output_dir="./downloads",
            on_progress_callback=lambda downloaded, total: ProgressBar(total).update(downloaded)
        )
        
        # Get video information
        print("📹 Getting video information...")
        video_info = uqload.get_video_info()
        
        print(f"✅ Video info retrieved successfully!")
        print(f"📝 Title: {video_info.get('title', 'Unknown')}")
        print(f"💾 Size: {video_info.get('size', 'Unknown')}")
        print(f"🖥️  Resolution: {video_info.get('resolution', 'Unknown')}")
        
        # Download the video
        print("\n🚀 Starting download...")
        uqload.download()
        
        print("✅ Single download demo completed!")
        
    except Exception as e:
        print(f"❌ Error in single download demo: {e}")


def demo_batch_download():
    """Demonstrate batch download with enhanced UI."""
    print("\n📁 DEMO: Batch Download")
    print("=" * 50)
    
    # Create sample URLs file
    urls_file = create_sample_urls_file()
    
    try:
        # Create batch downloader
        batch_downloader = BatchDownloader(
            max_workers=2,  # Use 2 concurrent downloads for demo
            output_dir="./downloads",
            on_progress_callback=lambda downloaded, total: ProgressBar(total).update(downloaded)
        )
        
        print(f"📄 Using URLs file: {urls_file}")
        print("🚀 Starting batch download...")
        
        # Download from file
        results = batch_downloader.download_from_file(urls_file)
        
        print(f"✅ Batch download demo completed!")
        print(f"📊 Results: {len([r for r in results if r['success']])}/{len(results)} successful")
        
    except Exception as e:
        print(f"❌ Error in batch download demo: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(urls_file):
            os.unlink(urls_file)


def demo_progress_bar():
    """Demonstrate the enhanced progress bar."""
    print("\n📊 DEMO: Enhanced Progress Bar")
    print("=" * 50)
    
    # Simulate a download with progress bar
    total_size = 1024 * 1024 * 10  # 10MB
    progress_bar = ProgressBar(total_size)
    
    print("🔄 Simulating download progress...")
    
    # Simulate download in chunks
    chunk_size = 1024 * 1024  # 1MB chunks
    downloaded = 0
    
    while downloaded < total_size:
        downloaded += chunk_size
        if downloaded > total_size:
            downloaded = total_size
        progress_bar.update(downloaded)
        
        # Small delay to see the progress
        import time
        time.sleep(0.1)
    
    progress_bar.finish()
    print("✅ Progress bar demo completed!")


def main():
    """Main demo function."""
    print("🚀 UQLoad Downloader Enhanced Features Demo")
    print("=" * 60)
    print("This demo showcases the new features and improvements:")
    print("• 🎨 Modern colored interface")
    print("• 📊 Enhanced progress bars")
    print("• 📁 Batch download capabilities")
    print("• ⚡ Parallel processing")
    print("• 🚀 Performance optimizations")
    print("=" * 60)
    
    # Create downloads directory if it doesn't exist
    os.makedirs("./downloads", exist_ok=True)
    
    # Run demos
    demo_progress_bar()
    demo_single_download()
    demo_batch_download()
    
    print("\n🎉 All demos completed!")
    print("📁 Check the './downloads' directory for downloaded files.")
    print("\n💡 To use the real tool:")
    print("   uqload-dl -u <url>                    # Single download")
    print("   uqload-dl -f urls.txt                 # Batch download")
    print("   uqload-dl -f urls.txt -w 5 -o /path   # Advanced batch download")


if __name__ == "__main__":
    main()
