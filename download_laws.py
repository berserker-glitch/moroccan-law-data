"""
Moroccan Justice Portal PDF Downloader

Downloads all PDF files from https://adala.justice.gov.ma maintaining the 
category/subcategory folder structure.

Usage:
    python download_laws.py

This script will:
1. Recursively traverse resource categories 12 and 569
2. Create matching folder structure in ./laws/
3. Download all PDF files preserving their names
"""

import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import unquote


# Configuration
BASE_URL = "https://adala.justice.gov.ma"
API_URL = f"{BASE_URL}/api/folders"
OUTPUT_DIR = Path("laws")

# Starting resource IDs
ROOT_FOLDER_IDS = [12, 569]

# Request settings
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8,fr;q=0.7",
    "Referer": BASE_URL,
}

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
DOWNLOAD_DELAY = 0.5  # seconds between downloads to be polite


def sanitize_filename(name: str) -> str:
    """
    Sanitize a filename by removing/replacing invalid characters.
    Keeps Arabic characters but removes Windows-invalid chars.
    """
    # Replace invalid Windows filename characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', name)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    # Limit length (Windows max path component is 255)
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized if sanitized else "unnamed"


def get_folder_data(folder_id: int) -> dict | None:
    """
    Fetch folder data from the API.
    Returns dict with 'folders' and 'files' arrays, or None on error.
    """
    url = f"{API_URL}/{folder_id}"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"  ⚠ Error fetching folder {folder_id} (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    
    return None


def download_file(file_path: str, save_path: Path) -> bool:
    """
    Download a file from the server.
    Returns True on success, False on failure.
    """
    # Construct full URL
    url = f"{BASE_URL}/api/{file_path}"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=60, stream=True)
            response.raise_for_status()
            
            # Write file in chunks
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except requests.RequestException as e:
            print(f"    ⚠ Error downloading (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            # Clean up partial file
            if save_path.exists():
                save_path.unlink()
    
    return False


def process_folder(folder_id: int, current_path: Path, depth: int = 0) -> tuple[int, int]:
    """
    Recursively process a folder and its subfolders.
    Returns tuple of (files_downloaded, files_failed).
    """
    indent = "  " * depth
    downloaded = 0
    failed = 0
    
    # Fetch folder data
    data = get_folder_data(folder_id)
    if data is None:
        print(f"{indent}✗ Failed to fetch folder {folder_id}")
        return 0, 0
    
    # Get folder name (for display)
    folder_name = data.get('name', f'folder_{folder_id}')
    print(f"{indent}📁 {folder_name}")
    
    # Process files in this folder
    files = data.get('files', [])
    for file_info in files:
        file_path = file_info.get('path', '')
        file_name = file_info.get('name', '')
        
        if not file_path:
            continue
        
        # Extract filename from path if name not provided
        if not file_name:
            file_name = unquote(file_path.split('/')[-1])
        
        # Ensure it's a PDF
        if not file_name.lower().endswith('.pdf'):
            file_name += '.pdf'
        
        # Sanitize filename
        safe_name = sanitize_filename(file_name)
        save_path = current_path / safe_name
        
        # Skip if already exists
        if save_path.exists():
            print(f"{indent}  ⏭ Skipping (exists): {safe_name[:50]}...")
            downloaded += 1
            continue
        
        # Download file
        print(f"{indent}  ⬇ Downloading: {safe_name[:50]}...")
        if download_file(file_path, save_path):
            print(f"{indent}  ✓ Saved: {safe_name[:50]}...")
            downloaded += 1
        else:
            print(f"{indent}  ✗ Failed: {safe_name[:50]}...")
            failed += 1
        
        time.sleep(DOWNLOAD_DELAY)
    
    # Process subfolders
    folders = data.get('folders', [])
    for subfolder in folders:
        subfolder_id = subfolder.get('id')
        subfolder_name = subfolder.get('name', f'folder_{subfolder_id}')
        
        if subfolder_id is None:
            continue
        
        # Create directory for subfolder
        safe_folder_name = sanitize_filename(subfolder_name)
        subfolder_path = current_path / safe_folder_name
        subfolder_path.mkdir(parents=True, exist_ok=True)
        
        # Recursively process subfolder
        sub_downloaded, sub_failed = process_folder(subfolder_id, subfolder_path, depth + 1)
        downloaded += sub_downloaded
        failed += sub_failed
    
    return downloaded, failed


def main():
    """Main entry point."""
    print("=" * 60)
    print("Moroccan Justice Portal PDF Downloader")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print()
    
    # Create base output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    total_downloaded = 0
    total_failed = 0
    
    # Process each root folder
    for root_id in ROOT_FOLDER_IDS:
        print(f"\n{'='*60}")
        print(f"Processing resource ID: {root_id}")
        print('='*60)
        
        # Get root folder info to create top-level directory
        root_data = get_folder_data(root_id)
        if root_data is None:
            print(f"✗ Failed to fetch root folder {root_id}")
            continue
        
        root_name = root_data.get('name', f'resources_{root_id}')
        safe_root_name = sanitize_filename(root_name)
        root_path = OUTPUT_DIR / safe_root_name
        root_path.mkdir(parents=True, exist_ok=True)
        
        # Process the root folder
        downloaded, failed = process_folder(root_id, root_path)
        total_downloaded += downloaded
        total_failed += failed
    
    # Summary
    print()
    print("=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"Total files downloaded: {total_downloaded}")
    print(f"Total files failed: {total_failed}")
    print(f"Files saved to: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()
