import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.video import Video
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.utils import platform

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

class MediaDownloaderApp(App):
    def build(self):
        self.title = "Universal Media Player & Downloader"
        
        # Base UI layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Status Label
        self.status_label = Label(
            text="Loading global trending media feed...", 
            size_hint_y=0.08,
            halign="center"
        )
        self.layout.add_widget(self.status_label)
        
        # Link / Keyword Input Field
        self.url_input = TextInput(
            hint_text="Search keywords or paste URL link here...", 
            multiline=False, 
            size_hint_y=0.08
        )
        self.layout.add_widget(self.url_input)

        # Quality Selector Row
        self.quality_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=10)
        self.quality_label = Label(text="Quality:", size_hint_x=0.3)
        self.quality_spinner = Spinner(
            text='High Quality',
            values=('High Quality', 'Medium Quality (720p)', 'Low Quality (Data Saver)'),
            size_hint_x=0.7
        )
        self.quality_layout.add_widget(self.quality_label)
        self.quality_layout.add_widget(self.quality_spinner)
        self.layout.add_widget(self.quality_layout)
        
        # Visual Progress Bar
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=0.04)
        self.layout.add_widget(self.progress_bar)
        
        # Action Buttons for Online Links
        self.button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=10)
        self.search_btn = Button(text="Search/Stream", on_press=self.start_search_or_stream)
        self.download_video_btn = Button(text="Get Video", on_press=self.start_video_download)
        self.download_audio_btn = Button(text="Get MP3", on_press=self.start_audio_download)
        
        self.button_layout.add_widget(self.search_btn)
        self.button_layout.add_widget(self.download_video_btn)
        self.button_layout.add_widget(self.download_audio_btn)
        self.layout.add_widget(self.button_layout)
        
        # Split Window: Video Player (Top) & Dynamic Results/Offline Browser (Bottom)
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=0.6, spacing=10)
        
        # Native Video Player
        self.video_player = Video(source='', state='stop', options={'eos': 'loop'}, size_hint_y=0.5)
        self.content_layout.add_widget(self.video_player)
        
        # Dynamic Results / Offline Container
        self.browser_container = BoxLayout(orientation='vertical', size_hint_y=0.5, spacing=5)
        self.browser_label = Label(text="📁 Search Results & Saved Files:", size_hint_y=0.15, halign="left")
        self.browser_container.add_widget(self.browser_label)
        
        self.scroll_view = ScrollView(size_hint_y=0.85)
        self.dynamic_list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.dynamic_list_layout.bind(minimum_height=self.dynamic_list_layout.setter('height'))
        self.scroll_view.add_widget(self.dynamic_list_layout)
        self.browser_container.add_widget(self.scroll_view)
        
        self.content_layout.add_widget(self.browser_container)
        self.layout.add_widget(self.content_layout)
        
        # Configure storage paths for your Samsung phone
        if platform == 'android':
            self.download_path = "/storage/emulated/0/Download/MediaDownloader"
        else:
            self.download_path = os.path.join(os.path.expanduser("~"), "Downloads", "MediaDownloader")
            
        if not os.path.exists(self.download_path):
            try: os.makedirs(self.download_path)
            except Exception: pass

        # Load your library right away
        self.refresh_offline_library()
        
        # Load trending feed safely on startup
        threading.Thread(target=self.safe_load_trending, daemon=True).start()

        return self.layout

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))

    def update_progress(self, percent):
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', percent))

    def refresh_offline_library(self):
        self.dynamic_list_layout.clear_widgets()
        if not os.path.exists(self.download_path): return
            
        files = [f for f in os.listdir(self.download_path) if f.endswith(('.mp4', '.mp3', '.mkv', '.webm'))]
        if not files:
            self.dynamic_list_layout.add_widget(Label(text="No local files found.", size_hint_y=None, height=40))
            return

        for filename in files:
            full_path = os.path.join(self.download_path, filename)
            btn = Button(text=f"📁 Local: {filename[:40]}...", size_hint_y=None, height=45, background_color=(0.2, 0.6, 0.8, 1))
            btn.bind(on_press=lambda inst, p=full_path: self.play_media(p))
            self.dynamic_list_layout.add_widget(btn)

    def play_media(self, file_path):
        self.video_player.unload()
        self.video_player.source = file_path
        self.video_player.state = 'play'
        self.update_status(f"Playing: {os.path.basename(file_path)[:30]}")

    def ytdl_progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = (downloaded / total) * 100
                self.update_progress(percent)
                self.update_status(f"Downloading... {int(percent)}%")
        elif d['status'] == 'finished':
            self.update_progress(100)
            self.update_status("Finalizing file...")

    def safe_load_trending(self):
        if yt_dlp is None: return
        opts = {'format': 'best', 'nocheckcertificate': True, 'quiet': True, 'extract_flat': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                res = ydl.extract_info("https://youtube.com", download=False)
                if 'entries' in res and res['entries']:
                    Clock.schedule_once(lambda dt: self.populate_results(res['entries'][:5], "🔥 Trend"))
                    self.update_status("Trending feed loaded!")
                else:
                    self.update_status("App ready! Enter search terms.")
        except Exception:
            self.update_status("Ready! Type above to search.")

    def populate_results(self, entries, label_prefix):
        self.dynamic_list_layout.clear_widgets()
        for entry in entries:
            url = entry.get('url') or f"https://youtube.com{entry.get('id')}"
            title = entry.get('title', 'Media Item')
            
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
            lbl = Label(text=f"{label_prefix}: {title[:25]}...", size_hint_x=0.5, halign="left")
            p_btn = Button(text="Stream", size_hint_x=0.2, background_color=(0, 0, 1, 1))
            d_btn = Button(text="Get", size_hint_x=0.3, background_color=(0, 1, 0, 1))
            
            p_btn.bind(on_press=lambda inst, u=url: self.start_async_action(u, "stream"))
            d_btn.bind(on_press=lambda inst, u=url: self.start_async_action(u, "video"))
            
            row.add_widget(lbl)
            row.add_widget(p_btn)
            row.add_widget(d_btn)
            self.dynamic_list_layout.add_widget(row)

    def start_search_or_stream(self, instance):
        text = self.url_input.text.strip()
        if not text: return
        self.update_progress(20)
        
        if text.startswith(("http://", "https://", "www.")):
            self.start_async_action(text, "stream")
        else:
            self.update_status(f"Searching for '{text}'...")
            threading.Thread(target=self._async_search, args=(text,), daemon=True).start()

    def _async_search(self, query):
        opts = {'format': 'best', 'nocheckcertificate': True, 'quiet': True, 'extract_flat': True, 'skip_download': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                res = ydl.extract_info(f"ytsearch3:{query}", download=False)
                if 'entries' in res and res['entries']:
                    Clock.schedule_once(lambda dt: self.populate_results(res['entries'], "🔍 Result"))
                    self.update_status(f"Found matches for '{query}'")
                else:
                    self.update_status("No results found.")
        except Exception as e:
            self.update_status("Search failed.")
        self.update_progress(100)

    def start_async_action(self, url, action_type):
        self.update_progress(0)
        if action_type == "stream":
            self.update_status("Extracting stream link...")
            threading.Thread(target=self._async_stream, args=(url,), daemon=True).start()
        elif action_type == "video":
            self.update_status("Queuing video...")
            threading.Thread(target=self._async_download, args=(url, False), daemon=True).start()

    def _async_stream(self, url):
        opts = {'format': 'best[ext=mp4]/best', 'nocheckcertificate': True, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
