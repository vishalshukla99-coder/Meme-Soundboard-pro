import datetime
import os
import threading
import time
import tkinter as tk
import urllib.parse
import webbrowser
import pygame

pygame.init()
pygame.mixer.init()

root = tk.Tk()
root.title("Meme Soundboard Pro v2.12")
root.attributes("-fullscreen", True)
root.configure(bg="#0a0a19")

# --- Global Control Variables ---
current_playing_channel = None
night_mode_enabled = tk.BooleanVar(value=True)
upi_id = "vishalshukla99@oksbi"  # अपनी यूपीआई आईडी

# OWNER_MODE = True रखने पर आपके फोन में सारे बटन खुले रहेंगे (टेस्टिंग के लिए)
OWNER_MODE = False


# --- Top Header ---
top_frame = tk.Frame(root, bg="#0a0a19")
top_frame.pack(side="top", fill="x", pady=(30, 5))

title_label = tk.Label(
    top_frame,
    text="Meme Soundboard Pro",
    font=("Arial", 16, "bold"),
    fg="#ffffff",
    bg="#0a0a19",
)
title_label.pack()

status_label = tk.Label(
    top_frame,
    text="Status: Ready | Tap to Play",
    font=("Arial", 9),
    fg="#00ffff",
    bg="#0a0a19",
)
status_label.pack(pady=2)


# --- Screen Flash Effect ---
def trigger_screen_flash():
  def flash():
    try:
      root.configure(bg="#ffffff")
      time.sleep(0.2)
      root.configure(bg="#0a0a19")
    except:
      pass

  threading.Thread(target=flash, daemon=True).start()


# --- Secure Audio Playback with Interruption & Flash ---
def play_meme_and_time(meme_filename, time_filename, is_premium=False):
  global current_playing_channel

  if current_playing_channel and current_playing_channel.get_busy():
    current_playing_channel.stop()

  if is_premium and not OWNER_MODE:
    amount = 7
    note = f"Unlock_Premium_{meme_filename}"
    upi_url = f"upi://pay?pa={upi_id}&pn=MemeApp&am={amount}&cu=INR&tn={note}"
    status_label.config(text=f"Opening UPI to Unlock Premium for ₹{amount}...")
    webbrowser.open(upi_url)
    return

  def play_sequence():
    global current_playing_channel
    try:
      meme_paths = [
          f"/storage/emulated/0/Download/{meme_filename}.wav",
          f"/sdcard/Download/{meme_filename}.wav",
          f"/storage/emulated/0/Download/{meme_filename}.mp3",
          f"/sdcard/Download/{meme_filename}.mp3",
      ]

      meme_path = None
      for mp in meme_paths:
        if os.path.exists(mp):
          meme_path = mp
          break

      if not meme_path:
        status_label.config(text=f"File missing: {meme_filename}")
        return

      time_paths = [
          f"/storage/emulated/0/Download/{time_filename}",
          f"/sdcard/Download/{time_filename}",
          "/storage/emulated/0/Download/Time.wav",
          "/sdcard/Download/Time.wav",
      ]

      time_audio_path = None
      for tp in time_paths:
        if os.path.exists(tp):
          time_audio_path = tp
          break

      if not time_audio_path:
        status_label.config(text=f"Time file missing: {time_filename}")
        return

      now = datetime.datetime.now()
      trigger_screen_flash()

      # 1. Play Meme Sound
      sound_meme = pygame.mixer.Sound(meme_path)
      current_playing_channel = sound_meme.play()
      status_label.config(
          text=f"Playing: {meme_filename} | {now.strftime('%I:%M %p')}"
      )

      if current_playing_channel:
        while current_playing_channel.get_busy():
          time.sleep(0.1)

      time.sleep(0.3)

      # 2. Play Time Sound
      sound_time = pygame.mixer.Sound(time_audio_path)
      current_playing_channel = sound_time.play()
      status_label.config(text="Announcing Time...")

      if current_playing_channel:
        while current_playing_channel.get_busy():
          time.sleep(0.1)

      status_label.config(text="Status: Ready")

    except Exception as ex:
      print("Audio Error:", ex)
      status_label.config(text="Playback error!")

  threading.Thread(target=play_sequence, daemon=True).start()


# --- Background Hourly Scheduler ---
def background_scheduler():
  last_hour = -1
  while True:
    now = datetime.datetime.now()
    current_hour = now.hour

    is_night = 22 <= current_hour or current_hour < 6
    silence_period = night_mode_enabled.get() and is_night

    if current_hour != last_hour and not silence_period:
      last_hour = current_hour
      play_meme_and_time("Sitaram", "Time.wav", is_premium=False)

    time.sleep(30)


threading.Thread(target=background_scheduler, daemon=True).start()

# --- Scrollable Main UI Container ---
canvas_container = tk.Canvas(root, bg="#0a0a19", highlightthickness=0)
scrollbar = tk.Scrollbar(
    root, orient="vertical", command=canvas_container.yview
)
scrollable_frame = tk.Frame(canvas_container, bg="#0a0a19")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas_container.configure(
        scrollregion=canvas_container.bbox("all")
    ),
)
canvas_container.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas_container.configure(yscrollcommand=scrollbar.set)

canvas_container.pack(side="top", fill="both", expand=True, padx=5, pady=5)

# --- Sound List ---
# Format: (Display Name, File Name, Time File Name, Is_Premium)
memes = [
    ("Sitaram", "Sitaram", "Time.wav", False),
    ("Khuch", "Khuch", "Time7.wav", False),
    ("Money", "Money", "Time8.wav", False),
    ("Randikhana", "Randikhana", "Time9.wav", False),
    ("Ramram", "Ramram", "Time10.wav", False),
    ("Neta", "Neta", "Time11.wav", False),
    ("Chudail", "Chudail", "Time12.wav", False),
    ("Balla", "Balla", "Time2.wav", False),
    ("Dikha", "Dikha", "Time1.wav", False),
    ("Terimaa", "Terimaa", "Time3.wav", False),
    ("Maaka", "Maaka", "Time4.wav", False),
    (
        "Sexy Meme",
        "Sexy",
        "Time5.wav",
        True,
    ),  # प्रीमियम (शाम 5 बजे)
]


# --- WhatsApp Custom Order Integration ---
def open_whatsapp():
  phone_number = "919876543210"
  message = "Hello, mujhe apni pasand ka custom meme alarm sound chahiye!"
  url = f"https://wa.me/{phone_number}?text={urllib.parse.quote(message)}"
  webbrowser.open(url)


# --- Refresh Grid Interface ---
def refresh_grid():
  for widget in scrollable_frame.winfo_children():
    widget.destroy()

  row_val = 0
  col_val = 0

  for btn_text, meme_file, time_file, is_premium in memes:
    if is_premium and not OWNER_MODE:
      btn_bg = "#ffa502"  # प्रीमियम के लिए अलग रंग (गोल्डन/ऑरेंज)
      display_label = (
          f"{btn_text}\n(⭐ Premium ₹7)"  # यहाँ स्टार और ₹7 जोड़ दिया गया है
      )
    else:
      btn_bg = "#ff4757"
      display_label = btn_text

    btn = tk.Button(
        scrollable_frame,
        text=display_label,
        font=("Arial", 11, "bold"),
        bg=btn_bg,
        fg="#000000" if (is_premium and not OWNER_MODE) else "#ffffff",
        width=13,
        height=2,
        command=lambda m=meme_file, t=time_file, p=is_premium: play_meme_and_time(
            m, t, p
        ),
    )
    btn.grid(row=row_val, column=col_val, padx=6, pady=6)

    col_val += 1
    if col_val > 1:
      col_val = 0
      row_val += 1


refresh_grid()

# --- Bottom Controls & Settings Panel ---
bottom_frame = tk.Frame(root, bg="#0a0a19")
bottom_frame.pack(side="bottom", fill="x", pady=5)

night_toggle = tk.Checkbutton(
    bottom_frame,
    text="Enable Night Mode (10 PM - 6 AM Silent)",
    variable=night_mode_enabled,
    font=("Arial", 9, "bold"),
    fg="#ffa502",
    bg="#0a0a19",
    selectcolor="#0a0a19",
    activebackground="#0a0a19",
    activeforeground="#ffa502",
)
night_toggle.pack(pady=2)

custom_btn = tk.Button(
    bottom_frame,
    text="Order Custom Voice on WhatsApp",
    font=("Arial", 9, "bold"),
    bg="#2ed573",
    fg="#000000",
    width=32,
    command=open_whatsapp,
)
custom_btn.pack(pady=3)

exit_btn = tk.Button(
    bottom_frame,
    text="Exit App",
    font=("Arial", 8, "bold"),
    bg="#3742fa",
    fg="#ffffff",
    width=8,
    command=root.destroy,
)
exit_btn.pack(pady=2)

root.mainloop()
