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

if __name__ == "__main__":
    download_from_ftp_url(
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE276nnn/GSE276581/suppl/GSE276581_reference.cnn.txt.gz", 
        "/Users/panrong/"
    )