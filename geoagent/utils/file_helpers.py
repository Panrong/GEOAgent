import os
from urllib.request import urlretrieve

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


if __name__ == "__main__":
    print(list_files(r"C:\Users\Administrator.DESKTOP-U1P64U3\Desktop\immunity5"))