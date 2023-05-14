from validations.input_validations import remove_special_characters, is_string_empty
import requests, re, colorama, datetime, os, tldextract, sys
from urllib.parse import urlparse
from tqdm import tqdm

# The class "VideoDownloader" downloads any video 
# as long as the url is the following: https://*/*/*/xxxxx.mp4
# Test: https://assets.mixkit.co/videos/preview/mixkit-white-cat-lying-among-the-grasses-seen-up-close-22732-large.mp4

class VideoDownloader:
    def __init__(self, url: str, filename: str = None) -> None:
        # Validate input arguments
        self.url = self.__validate_url(url)
        self.filename = self.__validate_filename(filename)
    
    def __validate_filename(self, filename: str) -> str:
        video_name, self.file_extension = self.url.rsplit('.', 1)
        
        # If a video name is not indicated, the name of the video will be taken from the url.
        # For example: https://*/my_video.mp4 the name of the video will be "my_video".
        if filename is None:
            filename = remove_special_characters(video_name.split('/')[-1])
        else:
            if is_string_empty(filename):
                raise ValueError("Filename must be a non-empty string.")
            filename = remove_special_characters(filename)
        
        return filename.strip()
    
    def __validate_url(self, url: str) -> str:
        if is_string_empty(url):
            raise ValueError("URL must be a non-empty string.")
        
        regex = r'^https?://.*\.(mp4|mov|avi|wmv|flv|mkv|webm)$' # You can add more video file formats.
        video_url_regex = re.compile(regex, re.IGNORECASE) 
        if not re.match(video_url_regex, url):
            raise ValueError("Please enter a valid URL. Example: https://*/*/*/my_video.mp4")
        return url.strip()
    
    def download(self) -> None:
        try:
            folder_name = "videos"
            # Check if folder exists
            if not os.path.exists(folder_name):
                os.makedirs(folder_name) # Create folder if it does not exist
            
            self.file_path = os.path.join(folder_name, f"{self.filename}.{self.file_extension}")
            
            # Extract domain information using tldextract
            extracted = tldextract.extract(self.url)
            domain, tld = extracted.domain, extracted.suffix
            
            # Extract the protocol
            protocol = urlparse(self.url).scheme
            base_domain = f"{protocol}://{domain}.{tld}/"
            
            # add headers to avoid "error_wrong_ip" on the uqload site
            headers = {'Referer': base_domain }
            
            response = requests.get(self.url, headers=headers, stream=True)
            response.raise_for_status()  # raise an exception if the status code is not 200
            
            if os.path.exists(self.file_path): # Rename the file if already exist
                timestamp = remove_special_characters(str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")))
                
                new_filename = f"{self.filename}_{timestamp}.{self.file_extension}"
                self.file_path = os.path.join(folder_name, new_filename)
                
                print(f"{colorama.Fore.YELLOW}The file already exist. \nThe file has been renamed as: {new_filename}")
                
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            
            if not total_size:
                raise Exception(("Error: Content-Length header is missing"))
            
            tqdm_bar = tqdm(
                total=total_size,
                unit='iB',
                unit_scale=True,
                desc=f"{colorama.Fore.LIGHTBLUE_EX}Downloading file... ")
            
            with requests.get(self.url, headers=headers, stream=True) as response:
                with open(self.file_path, 'wb') as file:
                    for data in response.iter_content(block_size):
                        tqdm_bar.update(len(data))
                        file.write(data)
            
            tqdm_bar.close()
            print(f"{colorama.Fore.LIGHTGREEN_EX}The file {self.filename} has been downloaded successfully!")
        
        except requests.exceptions.HTTPError as http_err:
            print(f"\n{colorama.Fore.LIGHTRED_EX}Error HTTP: {http_err}")
            self.delete_file()
            sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n\n{colorama.Fore.YELLOW}Operation canceled.  ", end="")
            self.delete_file()
            sys.exit(1)
        except Exception as ex:
            print(f'\n{colorama.Fore.LIGHTRED_EX}Error downloading file: {ex}')
            self.delete_file()
            sys.exit(1)
    
    def delete_file(self) -> None:
        if os.path.exists(self.file_path): # if file exist remove
            os.remove(self.file_path)
            print(f"{colorama.Fore.YELLOW}File '{self.filename}' deleted.\n")

# url = ""