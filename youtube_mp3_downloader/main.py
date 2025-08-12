import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk, font
from pathlib import Path
import yt_dlp
import json

class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                'bg': '#0f0f0f',
                'card_bg': '#1a1a1a',
                'secondary_bg': '#2d2d2d',
                'accent': '#6366f1',
                'accent_hover': '#4f46e5',
                'success': '#10b981',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'text': '#ffffff',
                'text_secondary': '#9ca3af',
                'text_muted': '#6b7280',
                'input_bg': '#374151',
                'input_border': '#4b5563',
                'border': '#374151',
                'shadow': '#000000'
            },
            "light": {
                'bg': '#ffffff',
                'card_bg': '#f8fafc',
                'secondary_bg': '#f1f5f9',
                'accent': '#6366f1',
                'accent_hover': '#4f46e5',
                'success': '#10b981',
                'error': '#ef4444',
                'warning': '#f59e0b',
                'text': '#1f2937',
                'text_secondary': '#4b5563',
                'text_muted': '#9ca3af',
                'input_bg': '#ffffff',
                'input_border': '#d1d5db',
                'border': '#e5e7eb',
                'shadow': '#00000020'
            }
        }
    
    def get_colors(self):
        return self.themes[self.current_theme]
    
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        return self.get_colors()

theme_manager = ThemeManager()

def get_download_path():
    return str(Path.home() / "Downloads")

class ModernButton(tk.Frame):
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.style = style
        colors = theme_manager.get_colors()
        
        if style == "primary":
            self.bg_color = colors['accent']
            self.hover_color = colors['accent_hover']
            self.text_color = '#ffffff'
        elif style == "secondary":
            self.bg_color = colors['secondary_bg']
            self.hover_color = colors['border']
            self.text_color = colors['text']
        
        self.configure(bg=self.bg_color, cursor='hand2')
        
        self.label = tk.Label(self, text=text, 
                             bg=self.bg_color, 
                             fg=self.text_color,
                             font=("SF Pro Display", 12, "bold"),
                             cursor='hand2')
        self.label.pack(expand=True, fill='both', padx=20, pady=12)
        
        # Bind events
        self.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
    
    def _on_click(self, event):
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        self.configure(bg=self.hover_color)
        self.label.configure(bg=self.hover_color)
    
    def _on_leave(self, event):
        self.configure(bg=self.bg_color)
        self.label.configure(bg=self.bg_color)
    
    def update_theme(self):
        colors = theme_manager.get_colors()
        if self.style == "primary":
            self.bg_color = colors['accent']
            self.hover_color = colors['accent_hover']
            self.text_color = '#ffffff'
        elif self.style == "secondary":
            self.bg_color = colors['secondary_bg']
            self.hover_color = colors['border']
            self.text_color = colors['text']
        
        self.configure(bg=self.bg_color)
        self.label.configure(bg=self.bg_color, fg=self.text_color)

class ModernEntry(tk.Frame):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, **kwargs)
        colors = theme_manager.get_colors()
        
        self.configure(bg=colors['input_bg'], relief='solid', bd=1, highlightthickness=0)
        
        self.entry = tk.Entry(self, 
                             font=("SF Pro Display", 12),
                             bg=colors['input_bg'],
                             fg=colors['text'],
                             insertbackground=colors['text'],
                             relief='flat',
                             bd=0,
                             highlightthickness=0)
        self.entry.pack(fill='both', expand=True, padx=15, pady=12)
        
        self.placeholder = placeholder
        self.placeholder_active = False
        
        if placeholder:
            self._show_placeholder()
        
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Button-1>", lambda e: self.entry.focus())
    
    def _show_placeholder(self):
        colors = theme_manager.get_colors()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.configure(fg=colors['text_muted'])
        self.placeholder_active = True
    
    def _hide_placeholder(self):
        colors = theme_manager.get_colors()
        if self.placeholder_active:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=colors['text'])
            self.placeholder_active = False
    
    def _on_focus_in(self, event):
        colors = theme_manager.get_colors()
        self.configure(highlightbackground=colors['accent'], highlightcolor=colors['accent'], highlightthickness=2)
        self._hide_placeholder()
    
    def _on_focus_out(self, event):
        colors = theme_manager.get_colors()
        self.configure(highlightthickness=0)
        if not self.entry.get():
            self._show_placeholder()
    
    def get(self):
        if self.placeholder_active:
            return ""
        return self.entry.get()
    
    def update_theme(self):
        colors = theme_manager.get_colors()
        self.configure(bg=colors['input_bg'])
        if self.placeholder_active:
            self.entry.configure(bg=colors['input_bg'], fg=colors['text_muted'])
        else:
            self.entry.configure(bg=colors['input_bg'], fg=colors['text'], insertbackground=colors['text'])

def download_audio():
    url = url_entry.get().strip()
    if not url:
        show_notification("Please enter a YouTube URL", "error")
        return

    # Update UI for download state
    download_btn.label.config(text="⏳ Downloading...")
    download_btn.configure(bg='#6b7280')
    download_btn.label.configure(bg='#6b7280')
    progress_bar['value'] = 0
    update_status("🚀 Initializing download...", "info")
    path_label.config(text="")

    def progress_hook(d):
        colors = theme_manager.get_colors()
        if d['status'] == 'downloading':
            if d.get('total_bytes') and d.get('downloaded_bytes'):
                progress = d['downloaded_bytes'] / d['total_bytes'] * 100
                progress_bar['value'] = progress
                update_status(f"⬇️ Downloading... {progress:.1f}%", "info")
            elif d.get('eta') is not None:
                update_status(f"⬇️ Downloading... ETA: {d['eta']}s", "info")
        elif d['status'] == 'finished':
            progress_bar['value'] = 100
            update_status("🔄 Converting to MP3...", "success")
        elif d['status'] == 'error':
            update_status("❌ Download error occurred", "error")

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

            update_status("✅ Download completed successfully!", "success")
            colors = theme_manager.get_colors()
            path_label.config(text=f"💾 Saved: {os.path.basename(downloaded_file)}", 
                            fg=colors['success'])
            
            show_notification(f"🎉 '{title}' downloaded successfully!", "success")

        except Exception as e:
            show_notification(f"❌ Download failed: {str(e)}", "error")
            update_status("❌ Download failed", "error")
            path_label.config(text="")
        finally:
            download_btn.label.config(text="⬇️ Download MP3")
            download_btn.update_theme()

    # Run download in a separate thread to avoid freezing the GUI
    threading.Thread(target=run_download, daemon=True).start()

def update_status(message, status_type="info"):
    colors = theme_manager.get_colors()
    color_map = {
        "info": colors['accent'],
        "success": colors['success'],
        "error": colors['error'],
        "warning": colors['warning']
    }
    status_label.config(text=message, fg=color_map.get(status_type, colors['text']))

def show_notification(message, notification_type="info"):
    if notification_type == "error":
        messagebox.showerror("Error", message)
    elif notification_type == "success":
        messagebox.showinfo("Success", message)
    else:
        messagebox.showinfo("Info", message)

def toggle_theme():
    colors = theme_manager.toggle_theme()
    update_theme_colors(colors)

def update_theme_colors(colors):
    # Update main app
    app.configure(bg=colors['bg'])
    main_frame.configure(bg=colors['bg'])
    
    # Update all frames
    for frame in [header_frame, input_card, progress_card, path_card]:
        frame.configure(bg=colors['card_bg'])
    
    # Update labels
    title.configure(bg=colors['card_bg'], fg=colors['text'])
    subtitle.configure(bg=colors['bg'], fg=colors['text_secondary'])
    url_label.configure(bg=colors['card_bg'], fg=colors['text'])
    progress_label.configure(bg=colors['card_bg'], fg=colors['text'])
    status_label.configure(bg=colors['card_bg'])
    path_icon_label.configure(bg=colors['card_bg'], fg=colors['text'])
    path_label.configure(bg=colors['card_bg'])
    
    # Update custom components
    url_entry.update_theme()
    download_btn.update_theme()
    theme_btn.update_theme()
    
    # Update progress bar
    style.configure("Custom.Horizontal.TProgressbar",
                    background=colors['accent'],
                    troughcolor=colors['secondary_bg'])

# ---------------- MODERN UI WITH THEME TOGGLE ----------------
app = tk.Tk()
app.title("YouTube to MP3 Downloader")
app.geometry("700x600")
app.resizable(False, False)

# Get initial colors
colors = theme_manager.get_colors()
app.configure(bg=colors['bg'])

# Create main container with padding
main_frame = tk.Frame(app, bg=colors['bg'])
main_frame.pack(expand=True, fill='both', padx=40, pady=30)

# Header section with theme toggle
header_frame = tk.Frame(main_frame, bg=colors['card_bg'], relief='flat', bd=0)
header_frame.pack(fill='x', pady=(0, 25))

# Top bar with theme toggle
top_bar = tk.Frame(header_frame, bg=colors['card_bg'])
top_bar.pack(fill='x', padx=25, pady=(20, 0))

# Theme toggle button
theme_btn = ModernButton(top_bar, 
                        text="🌙" if theme_manager.current_theme == "dark" else "☀️",
                        command=lambda: [toggle_theme(), 
                                       theme_btn.label.config(text="☀️" if theme_manager.current_theme == "dark" else "🌙")],
                        style="secondary")
theme_btn.pack(side='right')

# App title
title_container = tk.Frame(header_frame, bg=colors['card_bg'])
title_container.pack(fill='x', padx=25, pady=(20, 25))

title = tk.Label(title_container, 
                text="🎵 YouTube to MP3", 
                font=("SF Pro Display", 28, "bold"),
                bg=colors['card_bg'], 
                fg=colors['text'])
title.pack()

subtitle = tk.Label(header_frame,
                   text="Transform YouTube videos into high-quality MP3 files",
                   font=("SF Pro Display", 14),
                   bg=colors['bg'],
                   fg=colors['text_secondary'])
subtitle.pack(pady=(0, 15))

# Input card
input_card = tk.Frame(main_frame, bg=colors['card_bg'], relief='flat', bd=0)
input_card.pack(fill='x', pady=(0, 25))

input_content = tk.Frame(input_card, bg=colors['card_bg'])
input_content.pack(fill='x', padx=30, pady=25)

url_label = tk.Label(input_content, 
                    text="🔗 YouTube URL",
                    font=("SF Pro Display", 16, "bold"),
                    bg=colors['card_bg'],
                    fg=colors['text'])
url_label.pack(anchor='w', pady=(0, 12))

# Modern entry with placeholder
url_entry = ModernEntry(input_content, placeholder="https://www.youtube.com/watch?v=...")
url_entry.pack(fill='x', pady=(0, 20))

# Download button
download_btn = ModernButton(input_content, 
                           text="⬇️ Download MP3",
                           command=download_audio,
                           style="primary")
download_btn.pack(fill='x')

# Progress card
progress_card = tk.Frame(main_frame, bg=colors['card_bg'], relief='flat', bd=0)
progress_card.pack(fill='x', pady=(0, 25))

progress_content = tk.Frame(progress_card, bg=colors['card_bg'])
progress_content.pack(fill='x', padx=30, pady=25)

progress_label = tk.Label(progress_content,
                         text="📊 Download Progress",
                         font=("SF Pro Display", 16, "bold"),
                         bg=colors['card_bg'],
                         fg=colors['text'])
progress_label.pack(anchor='w', pady=(0, 15))

# Custom progress bar style
style = ttk.Style()
style.theme_use('clam')
style.configure("Custom.Horizontal.TProgressbar",
                background=colors['accent'],
                troughcolor=colors['secondary_bg'],
                borderwidth=0,
                lightcolor=colors['accent'],
                darkcolor=colors['accent'])

progress_bar = ttk.Progressbar(progress_content, 
                              length=600, 
                              mode='determinate',
                              style="Custom.Horizontal.TProgressbar")
progress_bar.pack(fill='x', pady=(0, 15))

status_label = tk.Label(progress_content,
                       text="Ready to download your favorite music",
                       font=("SF Pro Display", 12),
                       bg=colors['card_bg'],
                       fg=colors['text_secondary'])
status_label.pack(anchor='w')

# File path card
path_card = tk.Frame(main_frame, bg=colors['card_bg'], relief='flat', bd=0)
path_card.pack(fill='x')

path_content = tk.Frame(path_card, bg=colors['card_bg'])
path_content.pack(fill='x', padx=30, pady=25)

path_icon_label = tk.Label(path_content,
                          text="📁 Save Location",
                          font=("SF Pro Display", 16, "bold"),
                          bg=colors['card_bg'],
                          fg=colors['text'])
path_icon_label.pack(anchor='w', pady=(0, 10))

path_label = tk.Label(path_content,
                     text="Files will be saved to your Downloads folder",
                     font=("SF Pro Display", 12),
                     bg=colors['card_bg'],
                     fg=colors['text_secondary'],
                     wraplength=600,
                     justify='left')
path_label.pack(anchor='w')

# Footer
footer = tk.Frame(main_frame, bg=colors['bg'], height=30)
footer.pack(fill='x', pady=(20, 0))

app.mainloop()
