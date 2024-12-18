import pandas as pd
import os
import gzip
import itertools
import subprocess
import time
from urllib.request import urlretrieve
from datetime import datetime


def download_from_ftp_url(ftp_url, local_dir):
    try:
        # Create local directory if it doesn't exist
        os.makedirs(local_dir, exist_ok=True)
        
        # Get the filename from the URL
        filename = os.path.basename(ftp_url)
        
        # Create the full local file path
        local_file_path = os.path.join(local_dir, filename)
        
        # Download the file
        urlretrieve(ftp_url, local_file_path)
        print(f"Downloaded {filename} successfully")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def list_files(directory_path: str, exclude_suffixes: list[str] = None) -> list[str]:
    """
    List all filenames in the specified directory, excluding files with specified extensions.
    
    Args:
        directory_path (str): Path to the directory to scan
        exclude_types (list[str], optional): List of file extensions to exclude (e.g., ['.txt', '.pdf'])
    
    Returns:
        list[str]: List of filenames that match the criteria
    """
    # Initialize empty list for results
    file_list = []
    
    # Walk through directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Check if file ends with any of the excluded suffixes
            if exclude_suffixes is None or not any(file.lower().endswith(suffix) for suffix in exclude_suffixes):
                file_list.append(file)
    
    return file_list


def wget_ftp_url(ftp_url: str, data_dir: str, log_dir: str, read_timeout: int = 10, max_retries: int = 3):
    """
    Download file from FTP URL using wget with timeout and retry mechanism.
    
    Args:
        ftp_url (str): FTP URL to download from
        data_dir (str): Local directory to save the file
        log_dir (str): Directory to store log files
        read_timeout (int): Timeout in seconds for read operations
        max_retries (int): Maximum number of retry attempts
    """
    # Create local directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    # Get the filename from the URL
    filename = os.path.basename(ftp_url)
    local_file_path = os.path.join(data_dir, filename)
    log_file_path = os.path.join(log_dir, 'download.logs')
    
    # Skip if file already exists
    # todo: handle incomplete files form previous download
    if os.path.exists(local_file_path):
        with open(log_file_path, 'a') as f:
            f.write(f"[{datetime.now()}] File {filename} already exists, skipping download\n")
        return
    
    # Prepare wget command with timeout
    wget_cmd = [
        'wget',
        '--read-timeout', str(read_timeout),
        '--tries', '1',  # Set to 1 as we'll handle retries manually
        '-P', data_dir,
        ftp_url
    ]
    
    # Try downloading with retries
    for attempt in range(max_retries):
        try:
            result = subprocess.run(wget_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                with open(log_file_path, 'a') as f:
                    f.write(f"[{datetime.now()}] Downloaded {filename} successfully\n")
                return
            else:
                raise Exception(f"wget failed with error: {result.stderr}")
                
        except Exception as e:
            error_msg = f"[{datetime.now()}] Attempt {attempt + 1}/{max_retries} failed: {str(e)}\n"
            
            # On last attempt, log the failure
            if attempt == max_retries - 1:
                with open(os.path.join(data_dir, 'download_failures.log'), 'a') as f:
                    f.write(f"Failed to download {ftp_url}: {error_msg}")
                with open(log_file_path, 'a') as f:
                    f.write(f"[{datetime.now()}] Max retries reached for {filename}. Error logged.\n")
            else:
                with open(log_file_path, 'a') as f:
                    f.write(f"[{datetime.now()}] Attempt {attempt + 1} failed, retrying...\n")
                time.sleep(2)  # Wait before retry

def head_file(file_path: str, n: int) -> str:
    """Get the first n rows of a file efficiently.
    
    Args:
        file_path: Path to the file to read
        n: Number of rows to read
        
    Returns:
        String containing the first n rows of the file
    """
    # Handle Excel files
    if file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path, nrows=n)
        return df.to_string()
        
    # Handle gzipped files
    opener = gzip.open if file_path.endswith('.gz') else open
    
    with opener(file_path, 'rt') as f:
        # Use itertools.islice for memory efficient reading of first n lines
        return ''.join(itertools.islice(f, n))
    

def list_files_with_content(file_dir: str, peek_types: list[str], peek_limits: int = 10) -> dict:
    res = {"file_dir": file_dir, "files": [], "content": []}
    for file_name in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file_name)
        if os.path.isfile(file_path):
            res["files"].append(file_name)
            if any(ext in file_name.lower() for ext in peek_types):
                res["content"].append(head_file(file_path, peek_limits))
            else:
                res["content"].append(None)
    return res


if __name__ == "__main__":
    print(list_files_with_content("/Users/panrong/Downloads/GSM8636828", peek_types=["csv", "tsv", "mtx"]))