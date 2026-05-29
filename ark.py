import requests, zipfile, shutil, os, platform, re
import subprocess as sp
from bs4 import BeautifulSoup
from colorama import Fore, init
init()


class APKToolsInstaller(object):
    def __init__(self):
        super(APKToolsInstaller, self).__init__()

        self.test = True
        self.session = requests.Session()
        self.dl_host = "https://bitbucket.org"
        self.dl_host_ep = "/iBotPeaches/apktool/downloads/"
        self.target_dir = "./extracted_wrappers"
        self.target_filename = "apktool_source.zip"
        self.wrapper_dir = None
        

    def available_versions(self):
        for link in BeautifulSoup(requests.get("https://bitbucket.org/iBotPeaches/apktool/downloads/", params={'iframe': 'true'}).content, "html.parser").find_all("a", class_="execute"):
            print(link.get("href").split("_")[1][:-4])

    def source_link(self):
        return self.dl_host + BeautifulSoup(requests.get(f"{self.dl_host}/iBotPeaches/apktool/downloads/", params={'iframe': 'true'}).content, "html.parser").find('a', class_="lfs-warn-link").get('href')

    def download_file(self, url, filename):
        r = requests.get(url)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            print(f"{filename} downloaded successfully.")
        else:
            print(f"Failed to download {filename}. Status code: {r.status_code}")

    def extract_wrappers(self, folder_name):
        try:
            with zipfile.ZipFile(self.target_filename, 'r') as zip_ref:
                zip_file_list = zip_ref.namelist()
                files_in_folder = [f for f in zip_file_list if f.startswith(folder_name)]
                if files_in_folder:
                    for file in files_in_folder:
                        zip_ref.extract(file, path=self.target_dir)
                    print(f"Folder '{folder_name}' extracted successfully.")
                else:
                    print(f"Folder '{folder_name}' not found in the ZIP file.")
        except Exception as e:
            print(f"Error extracting folder '{folder_name}' from ZIP file: {e}")

class Decomp(object):
    def __init__(self):
        super(Decomp, self).__init__()

        #self.detected_system = os.name # The name of the operating system dependent module imported. The following names have currently been registered: 'posix', 'nt', 'java'.
        self.detected_system = platform.system() # Darwin, Linux, Windows

    def backup_file(self, file):
        backup_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'APK Backup')
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy(file, backup_dir)

    def rename_file(self, file, renamed):
        return os.rename(file, renamed)

    def apktool_d_file(self, wrapper_dir, file, platform):
        wshell = True
        platforms = {'Darwin':'osx', 'Linux':'linux','Windows':'windows'}
        
        platform_dir = platforms.get(platform)
        if platform_dir is None:
            raise ValueError(f"Unsupported platform: {platform}")

        shutil.move("apktool.jar", f"./extracted_wrappers/{wrapper_dir}/scripts/{platform_dir}/apktool.jar")
        
        decompile_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Decompiled')
        os.makedirs(decompile_dir, exist_ok=True)
        
        apktool_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                                    'extracted_wrappers', wrapper_dir, 'scripts', platform_dir, 'apktool')
        if platform in ['Linux', 'Darwin']:
            wshell=False
            sp.call(f"chmod +x {apktool_path}", shell=True)
            os.chmod(apktool_path, 0o755)

        sp.call([os.path.join(os.path.dirname(os.path.realpath(__file__)), 
                               'extracted_wrappers', wrapper_dir, 'scripts', platform_dir, 'apktool'), 'd', file], shell=wshell)
        
    def decompress_apk(self, file):
        extracted_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Decompressed')
        os.makedirs(extracted_dir, exist_ok=True)
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)    
        return extracted_dir

    def remove_renamed_apk(self, file):
        os.remove(file)

class ARK(object):
    def __init__(self):
        super(ARK, self).__init__()

        self.encodings = ['utf-8', 'latin-1', 'iso-8859-1']

    def search_exposed_endpoints(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    lines = self.read_file(file_path)
                    for line_number, line in enumerate(lines, start=1):
                        if re.search(r'const-string v0, ".*?/.*?/.*?"', line):
                            print(f'{"\\".join(file_path.split("\\")[2:])}:{line_number}:{line.strip()}')
                except Exception as e:
                    #print(f"Error processing file: {file_path}. Error: {str(e)}")
                    continue

    def read_file(self, file_path):
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.readlines()
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                raise  # Let FileNotFoundError propagate up
            except Exception as e:
                #print(f"Error opening file: {file_path}. Error: {str(e)}")
                continue
        # If all encodings fail, return an empty list
        return []

if __name__ == "__main__":
    decomp = Decomp()
    apktools = APKToolsInstaller()
    ark = ARK()
    
    os.makedirs(apktools.target_dir, exist_ok=True)
    apktools.available_versions()

    version = input("Enter version ID to download: ")

    dl_link = apktools.source_link()
    apktools.wrapper_dir = f'iBotPeaches-apktool-{dl_link.split("/")[-1].split(".")[0]}/scripts'
    apktools.download_file(dl_link, apktools.target_filename)
    apktools.extract_wrappers(apktools.wrapper_dir)
    os.remove(apktools.target_filename)
    apktools.download_file(f"https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_{version}.jar", f"apktool.jar")

    print(f"[{Fore.YELLOW}!{Fore.WHITE}] {decomp.detected_system} system detected!")
    filename = input(f"{Fore.WHITE}Enter APK filename: ")
    
    #decomp.windows_apktool_d_file(apktools.wrapper_dir.split('/')[0], filename)
    decomp.apktool_d_file(apktools.wrapper_dir.split('/')[0], filename, decomp.detected_system)

    print(f"[{Fore.YELLOW}!{Fore.WHITE}] Backing up APK")
    shutil.move(filename.split(".apk")[0], "Decompiled")
    decomp.backup_file(filename)

    print(f"[{Fore.GREEN}+{Fore.WHITE}] Renaming APK to extract")
    decomp.rename_file(filename, f"{os.path.splitext(filename)[0]}.zip")

    print(f"[{Fore.GREEN}+{Fore.WHITE}] Extracting APK")
    filename = filename.replace(".apk", ".zip")
    decomp.decompress_apk(filename)
    
    print(f"[{Fore.YELLOW}!{Fore.WHITE}] Removed extracted file")
    decomp.remove_renamed_apk(filename)

    ark.search_exposed_endpoints("Decompiled")
    print(f"\n~{Fore.CYAN}Closing script{Fore.WHITE}")
