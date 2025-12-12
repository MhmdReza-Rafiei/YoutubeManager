import yaml 
from pathlib import Path
from typing import Dict, Any , List , Optional
import time 

try: 
    import base.main as lib
except:
    print("Could Not Find base\\main as lib")
    print("Pls Install Requirements Using (pip install -r requirements.txt)")
    input("Press Enter To leave...")
    exit()

CONFIG_FILE = 'config'
CONFIG = {
    'User_Name': None,
    'Defult_Urls': []
}

# ====================== Helpers ======================
_print = print
def print(*args, end="\n" , flush = False):
    time.sleep(0.15)
    _print(*args, end=end , flush = flush)
_input = input
def input(text:str , type:str = "string" , allow_empty: bool = False):
    while True:
        Input = _input(text).strip()
        if not Input or type != "none" and type != "number" and Input.isdigit():
            continue
        else:
            break
    return Input

def clear_screen():
    print("\n" * 1)

def header(title: str):
    print(f"\n{'='*15} {title} {'='*15}")

def getUser():
   return CONFIG["User_Name"] if CONFIG["User_Name"] else False
# ====================== Config Handler ======================
def load_config() -> Dict[str, Any]:
    global CONFIG
    Config = Path(CONFIG_FILE)
    if Config and (Config.is_dir if Config else False):
        try:
            with open(f"{CONFIG_FILE}\\system.yaml", "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                CONFIG = data
        except Exception as e:
            print(f"⚠️  Failed to load config: {e} Using defaults")
    else: 
        print("ℹ️  No config found Using default settings")
load_config()

def saveConfig() -> CONFIG:
    try:
        with open(f"{CONFIG_FILE}\\system.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(CONFIG, f, sort_keys=False, allow_unicode=True)
            print(f"💽 Settings saved to config/system.yaml")
    except Exception as e:
        print(f"❌ Failed to save settings: {e}")

def changeConfig(key:str,value:Any):
    CONFIG[key] = value


# ====================== Panel ======================
class Panel:
    def __init__(self, selection: dict, help: bool = True, exit: bool = True):
        self.selection = selection.copy()
        self.closed = False

        if help:
            self.selection["help"] = {
                "action": self.show_help,
                "arg": None,
                "desc": "Show help"
            }

        self.selection["exit"] = {
            "action": self.close if exit else goodbye,
            "arg": None,
            "desc": "Exit / Go back"
        }

    def close(self):
        self.closed = True

    def show_help(self):
        header("Help")
        print("You can type the option name or its number.")
        print("Available options:\n")
        for key, item in self.selection.items():
            if key.lower() in ["help", "exit"]:
                continue
            desc = item.get("desc", "")
            print(f"{key.title():<15} → {desc}")
        print("Help              → Show this help")
        print("Exit              → Go back / close panel")
        print()

    def draw(self):
        header("Menu")
        num = 1
        for key, item in self.selection.items():
            item["id"] = num
            print(f"{num}. {key.title():<15} → {item.get('desc', '')}")
            num += 1
        print()

    def handle(self):
        while not self.closed:
            self.draw()
            choice = input("🛠️   What would you like to do? > ", type="none").strip().lower()

            if choice in self.selection:
                item = self.selection[choice]
                arg = item.get("arg")
                if arg is not None:
                    if isinstance(arg, (tuple, list)):
                        item["action"](*arg)
                    else:
                        item["action"](arg)
                else:
                    item["action"]()
                continue

            if choice.isdigit():
                n = int(choice)
                for item in self.selection.values():
                    if item.get("id") == n:
                        arg = item.get("arg")
                        if arg is not None:
                            if isinstance(arg, (tuple, list)):
                                item["action"](*arg)
                            else:
                                item["action"](arg)
                        else:
                            item["action"]()
                        break
                else:
                    print("Invalid choice.")
            elif choice:
                print("Not recognized.")
            time.sleep(0.5)

    def run(self):
        self.handle()
# ====================== Actions ======================
def welcome():
    header(f"{getUser() + " " if getUser() else ""}Welcome to (Youtube Manager) 📰")
    print("🔔   GitHub: https://github.com/MhmdReza-Rafiei/YoutubeManager")
    print("🎗️   MadeBy: @MhmdReza Rafiei")

def download(urls_dict: Optional[Dict[str, dict]] = None):
    if urls_dict is not None:
        if not urls_dict:
            print("\nNo URLs to download!")
            return

        set_settings = input(
            "Do you want to customize settings for these URLs (type, format, quality, thumbnail, organize)? (y/n): "
        ).strip().lower() != "n"

        final_urls = {}

        if set_settings:
            print("\nCustomizing settings for each URL...\n")
            for url in urls_dict.keys():
                print(f"Settings for: {url}")
                Type = input("  Type (video/audio) [video]: ").strip().lower() or "video"
                Type = "audio" if Type == "audio" else "video"
                Format = input("  Format (mp4/mp3/etc) [mp4]: ").strip() or "mp4"
                Quality = input("  Quality (highest/high/mid/low) [highest]: ").strip() or "highest"
                Thumbnail = input("  Embed thumbnail? (y/n) [y]: ").strip().lower() != "n"
                Organize = input("  Organize by channel? (y/n) [y]: ").strip().lower() != "n"

                final_urls[url] = {
                    'type': Type,
                    'format': Format,
                    'quality': Quality,
                    'thumbnail': Thumbnail,
                    'organize': Organize
                }
        else:
            final_urls = urls_dict

        header("Download Started")
        for url, opts in final_urls.items():
            print(f"\nDownloading: {url}")
            try:
                done = lib.Download(
                    url=url,
                    type=opts.get("type", "video"),
                    format=opts.get("format", "mp4"),
                    quality=opts.get("quality", "highest"),
                    thumbnail=opts.get("thumbnail", True),
                    organize=opts.get("organize", True)
                )
            except Exception as e:
                print(f"Failed: {e}")
        if done:
            header("All Downloads Complete")
        _input("\nPress Enter to continue...")
        return

    # Menu mode when no urls_dict provided
    if urls_dict is None:
        header("Download")
        Panel({
            "default urls": {
                "desc": "Use Default_Urls from config",
                "action": lambda: download(CONFIG.get("Default_Urls", {}))
            },
            "custom url": {
                "desc": "Enter custom URLs",
                "action": lambda: download(
                    {url.strip(): {} for url in input("Enter URLs (separate with comma): ").split(",") if url.strip()}
                )
            }
        }, help=True, exit=True).run()

def status(urls_dict: Optional[Dict[str, dict]] = None):
    if urls_dict is not None:
        if not urls_dict:
            print("\n📭 No URLs to check!")
            input("\nPress Enter to continue...")
            return

        header("Status Information")
        for url in urls_dict.keys():
            print(f"\n🔍 Fetching info for:\n   {url}\n")
            try:
                info = lib.getInfo(url)
                if info:
                    if 'entries' in info:  # Playlist or Channel
                        total = len([e for e in info['entries'] if e])
                        print(f"📂 Type: {'Channel' if info.get('channel') else 'Playlist'}")
                        print(f"📌 Title: {info.get('title', 'N/A')}")
                        print(f"👤 Uploader: {info.get('uploader', 'N/A')}")
                        print(f"🎥 Total items: {total}")
                    else:  # Single video
                        print(f"🎥 Title: {info.get('title', 'N/A')}")
                        print(f"👤 Uploader: {info.get('uploader', 'N/A')}")
                        duration = info.get('duration')
                        if duration:
                            mins, secs = divmod(duration, 60)
                            print(f"🎬 Duration: {mins}:{secs:02d}")
                        else:
                            print(f"🎬 Duration: N/A")
                        print(f"👀 Views: {info.get('view_count', 'N/A')}")
                        print(f"📅 Upload Date: {info.get('upload_date', 'N/A')}")
                        desc = info.get('description', 'N/A')
                        short_desc = desc[:200] + ("..." if len(desc) > 200 else "")
                        print(f"📄 Description: {short_desc}")
                else:
                    print("❌ No information available (possibly removed or private)")
            except Exception as e:
                print(f"⚠️ Failed to fetch info: {e}")
            print("-" * 50)
            _input("\n✅ Status check complete! Press Enter to continue...")
            return


    # Menu mode
    if urls_dict is None:
        header("Status Check")
        Panel({
            "default urls": {
                "desc": "Check status of Default_Urls from config",
                "action": lambda: status(CONFIG.get("Default_Urls", {}))
            },
            "custom url": {
                "desc": "Enter custom URLs to check status",
                "action": lambda: status(
                    {url.strip(): {} for url in input("Enter URLs (separate with comma): ").split(",") if url.strip()}
                )
            }
        }, help=True, exit=True).run()

def setting(mode="start", key=None, value=None):
    if mode == "change" and key and value is not None:
        if key == "Defult_Urls":
            value = [path.strip() for path in value.split(",") if path.strip()]
            print(f"Updating Defult_Urls → {value}")
        else:
            print(f"Updating {key} → {value}")
        changeConfig(key, value)
        saveConfig()
        print("Saved successfully!")
        _input("\nPress Enter to continue...")
        return

    if mode == "status":
        header("Current Settings")
        paths = CONFIG.get('Defult_Urls', [])
        urls_display = ", ".join(paths) if paths else "Not set"
        print(f"User Name     : {CONFIG.get('User_Name', 'Not Set')}")
        print(f"Defult_Urls   : {urls_display}")
        _input("\nPress Enter to continue...")
        return

    if mode == "start":
        Panel({
            "change": {"desc": "Change Settings", "action": lambda: setting("change")},
            "status": {"desc": "View Current Settings", "action": lambda: setting("status")},
        }, help=True, exit=True).run()
        return

    if mode == "change":
        header("Change Settings")
        Panel({
            "username": {
                "desc": "Change your username",
                "action": lambda: setting(
                    "change",
                    key="User_Name",
                    value=input("New username: ").strip()
                )
            },
            "default urls": {
                "desc": "Set default URLs (comma separated)",
                "action": lambda: setting(
                    "change",
                    key="Defult_Urls",
                    value=input("Enter URLs (comma separated): ").strip()
                )
            },
        }, help=True, exit=True).run()

def goodbye():

    header("Goodbye!")
    print(f"{getUser() + "' " if getUser() else ""}Thanks you for using (Youtube Manager) 📰")
    for i in range(5, 0, -1):
        print(f"   Closing in {i}...", end="\r")
        time.sleep(1)
    print("\n   See you next time! 👋\n")
    time.sleep(1)
    exit()
# ====================== Run ======================
def main():
    while True:
        welcome()
        if not getUser():
          header("Need Verification")
          UserName = input("Enter Your UserName: ")
          
          changeConfig("User_Name",UserName)
          saveConfig()
          _input("\nPress Enter to continue...")

        header("System - Panel")
        SystemPanel = Panel({
            "download":{"desc":"Download (Videos/PlayList/...)","action":download},
            "status":{"desc":"Status (Get Status of an (Video/PlayList/...))","action":status},
            "setting":{"desc":"Setting (Change UserName/Defult_Urls)","action":setting},
        },True)
        SystemPanel.run()
        goodbye()

if __name__ == "__main__":
    main()
