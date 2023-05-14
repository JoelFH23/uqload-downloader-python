from uqload import UQLoad
import colorama, argparse

colorama.init(autoreset=True)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()

        # Add arguments
        parser.add_argument('-u', '--url', type=str, help='Video url from uqload', required=True)
        parser.add_argument('-n', '--name', type=str, help='Video name')

        # Read arguments from command line
        args = parser.parse_args()
        
        video = UQLoad(args.url)
        video.download(video_name=args.name)
    
    except Exception as ex:
        print(f"{colorama.Fore.LIGHTRED_EX}{ex}")

#https://uqload.com/embed-0zmi1ulf0d60.html
#https://uqload.com/embed-h63yfu9dkw1r.html