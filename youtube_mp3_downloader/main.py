import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import yt_dlp

def get_download_path():
    return str(Path.home() / "Downloads")

def download_audio():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return

    # Disable the button during download
    download_btn.config(state=tk.DISABLED)
    progress_bar['value'] = 0
    status_label.config(text="Starting download...")
    path_label.config(text="")

    def progress_hook(d):
        if d['status'] == 'downloading':
            if d.get('total_bytes') and d.get('downloaded_bytes'):
                progress = d['downloaded_bytes'] / d['total_bytes'] * 100
                progress_bar['value'] = progress
                status_label.config(text=f"Downloading... {progress:.1f}%")
            elif d.get('eta') is not None:
                status_label.config(text=f"Downloading... ETA: {d['eta']}s")
        elif d['status'] == 'finished':
            progress_bar['value'] = 100
            status_label.config(text="Download finished, converting...")
        elif d['status'] == 'error':
            status_label.config(text="Error during download.")

    def run_download():
        try:
            download_dir = get_download_path()
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Audio')
                downloaded_file = os.path.join(download_dir, f"{title}.mp3")

            status_label.config(text="Download and conversion completed!")
            path_label.config(text=f"Saved to: {downloaded_file}")
            print(f"Downloaded file saved at: {downloaded_file}")

            messagebox.showinfo("Success", f"🎉 '{title}' downloaded as MP3 to your Downloads folder!")

        except Exception as e:
            messagebox.showerror("Download Failed", f"❌ Something went wrong.\n\n{str(e)}")
            status_label.config(text="Download failed.")
            path_label.config(text="")
        finally:
            download_btn.config(state=tk.NORMAL)

    # Run download in a separate thread to avoid freezing the GUI
    threading.Thread(target=run_download, daemon=True).start()

# ---------------- GUI ----------------
app = tk.Tk()
app.title("YouTube to MP3 Downloader")
app.geometry("500x240")
app.resizable(False, False)

title = tk.Label(app, text="🎵 YouTube to MP3 Downloader", font=("Helvetica", 16, "bold"))
title.pack(pady=10)

url_label = tk.Label(app, text="Enter YouTube Video URL:")
url_label.pack()

url_entry = tk.Entry(app, width=60)
url_entry.pack(pady=5)

download_btn = tk.Button(app, text="Download MP3", bg="#4CAF50", fg="white", font=("Helvetica", 12), command=download_audio)
download_btn.pack(pady=10)

progress_bar = ttk.Progressbar(app, length=400, mode='determinate')
progress_bar.pack(pady=5)

status_label = tk.Label(app, text="Idle", font=("Helvetica", 10))
status_label.pack()

path_label = tk.Label(app, text="", font=("Helvetica", 10), fg="blue")
path_label.pack(pady=5)

app.mainloop()
