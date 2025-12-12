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
            _input("\nPress Enter to continue...")
            return
            

        header("🔍 Status Checker")
        total_urls = len(urls_dict)

        for idx, url in enumerate(urls_dict.keys(), 1):
            print(f"\n[{idx}/{total_urls}] 🔎 Fetching → {url}\n")
            try:
                info = lib.getInfo(url)
                if not info:
                    print("⚠️ No info • Possibly deleted or private")
                    print("═" * 60 + "\n")
                    continue

                print("════════════════════════════════════════════════════════════")
                print("                   🎬 YT-DLP VIDEO INFO")
                print("════════════════════════════════════════════════════════════")

                # ── PLAYLIST / CHANNEL ──
                if info.get('entries') is not None:
                    entries = [e for e in info['entries'] if e]
                    total = len(entries)
                    if info.get('entries') is not None:
                        if info.get('_type') == 'playlist' or info.get('playlist_id') or info.get('playlist_title'):
                            kind = "📁 Playlist"
                        else:
                            kind = "📺 Channel"

                    print(f"Type        : {kind}")
                    print(f"Title       : 📌 {info.get('title', 'N/A')}")
                    print(f"Channel     : 👤 {info.get('channel') or info.get('uploader', 'N/A')}")
                    print(f"Total       : 🎞️ {total:,} video{'s' if total != 1 else ''}")
                    print(f"URL         : 🔗 {info.get('webpage_url', url)}")
                    print("════════════════════════════════════════════════════════════\n")

                    # Show ALL videos beautifully with icons
                    for i, entry in enumerate(entries, 1):

                        # Duration fix
                        duration = entry.get('duration')
                        if duration is not None:
                            try:
                                duration = int(duration)
                            except:
                                duration = 0

                        title = entry.get('title', 'Untitled')

                        if duration is None or duration == 0:
                            icon = "🔴 LIVE"
                            time_str = "LIVE"
                        elif duration >= 3600:
                            h = duration // 3600
                            m = (duration % 3600) // 60
                            s = duration % 60
                            icon = "🎬 Full Video"
                            time_str = f"{h}:{m:02d}:{s:02d}"
                        else:
                            m = duration // 60
                            s = duration % 60
                            icon = "🎯 Short" if duration < 600 else "🎬 Full Video"
                            time_str = f"{m}:{s:02d}"

                        # Icon based on type
                        if "short" in title.lower() or "shorts" in title.lower():
                            prefix = "🎯 Short"
                        elif entry.get('duration', 0) == 0 or entry.get('live_status') == 'is_live':
                            prefix = "🔴 LIVE"
                        else:
                            prefix = "🎬 Full Video"

                        # FIX: force index to int → prevents float error
                        print(f"   {int(i):3d}. {prefix} {time_str} → {title}")

                    print(f"\n   Total: 🎞️ {total} video{'s' if total != 1 else ''} listed above ↑")

                # ── SINGLE VIDEO ──
                else:
                    duration = info.get('duration')
                    if duration is not None:
                        try:
                            duration = int(duration)
                        except:
                            duration = 0

                    if duration and duration > 0:
                        if duration >= 3600:
                            h = duration // 3600
                            m = (duration % 3600) // 60
                            s = duration % 60
                            dur_str = f"{h}:{m:02d}:{s:02d}"
                        else:
                            m = duration // 60
                            s = duration % 60
                            dur_str = f"{m}:{s:02d}"
                    else:
                        dur_str = "LIVE"

                    if 'shorts' in info.get('webpage_url', '') or duration <= 90:
                        kind = "Short Video"
                    elif info.get('duration', 0) > 600:
                        kind = "Long Video"
                        
                    def pretty(n):
                        if not n: return "N/A"
                        if n >= 1_000_000_000: return f"{n/1e9:.2f}B"
                        if n >= 1_000_000: return f"{n/1e6:.2f}M"
                        if n >= 1_000: return f"{n/1e3:.1f}K"
                        return f"{n:,}"

                    w, h = info.get('width'), info.get('height')
                    fps = info.get('fps')
                    reso = f"{w}x{h} @ {fps}fps" if w and h and fps else info.get('resolution', 'N/A')

                    date = info.get('upload_date', '')
                    if len(date) == 8:
                        nice_date = f"{date[6:]}/{date[4:6]}/{date[:4]}"
                    else:
                        nice_date = date or "N/A"

                    print(f"Type        : 🎥 {kind}")
                    print(f"Extractor   : 🧩 {info.get('extractor_key', 'Unknown').replace(':', '').title()}")
                    print(f"Title       : 📌 {info.get('title', 'N/A')}")
                    print(f"Uploader    : 👤 {info.get('uploader') or info.get('channel', 'N/A')}")
                    print(f"Duration    : ⏱️ {dur_str}")
                    print(f"Resolution  : 📺 {reso}")
                    print(f"Views       : 👁️ {pretty(info.get('view_count'))}")
                    print(f"Likes       : 👍 {pretty(info.get('like_count'))}")
                    print(f"Comments    : 💬 {pretty(info.get('comment_count'))}")
                    print(f"Upload Date : 📅 {nice_date}")
                    print(f"URL         : 🔗 {info.get('webpage_url', url)}")

                    desc = info.get('description') or ""
                    if desc.strip():
                        short = desc.replace('\n', ' ')[:380]
                        if len(desc) > 380:
                            short += "…"
                        print(f"Description : 📝 {short}")

                    tags = info.get('tags')
                    if tags:
                        shown = tags[:12]
                        tagline = ", ".join(shown)
                        if len(tags) > 12:
                            tagline += " …"
                        print(f"Tags        : 🏷️ {tagline} ({len(tags)} total)")

                print("════════════════════════════════════════════════════════════\n")
                print("Status: ✅ Available & Working\n")

            except Exception as e:
                print("════════════════════════════════════════════════════════════")
                print("                   ❌ ERROR")
                print("════════════════════════════════════════════════════════════")
                print(f"Failed to fetch: {e}")
                if "private" in str(e).lower() or "unavailable" in str(e).lower():
                    print("Reason: 🔒 Private, Deleted, or Region Blocked")
                elif "age" in str(e).lower():
                    print("Reason: 🔞 Age Restricted")
                print("════════════════════════════════════════════════════════════\n")

        print(f"All {total_urls} URL{'s' if total_urls != 1 else ''} processed! 🎉")
        _input("\nPress Enter to continue...")



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
