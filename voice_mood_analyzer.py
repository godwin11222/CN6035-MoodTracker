import speech_recognition as sr
import tkinter as tk
from textblob import TextBlob
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
from datetime import datetime, timedelta

# --- Data storage ---
mood_data = {'Happy': 0, 'Sad': 0, 'Neutral': 0}
weekly_mood = []

# --- Core logic ---
def update_mood(text):
    """Analyze text sentiment, send to API, record mood locally."""
    # 1) Determine mood from text
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        mood = 'Happy'
    elif polarity < 0:
        mood = 'Sad'
    else:
        mood = 'Neutral'

    # 2) Send to Flask back-end
    try:
        resp_post = requests.post(
            "http://127.0.0.1:5000/set_mood",
            json={"mood": mood},
            timeout=5
        )
        resp_post.raise_for_status()
        # 3) Fetch last stored mood to confirm
        resp_get = requests.get(
            "http://127.0.0.1:5000/get_mood",
            timeout=5
        )
        resp_get.raise_for_status()
        server_mood = resp_get.json().get("lastMood")
        print(f"✅ Server says lastMood = {server_mood}")
    except Exception as e:
        print(f"❌ API error: {e}")

    # 4) Update local data and timestamp
    mood_data[mood] += 1
    weekly_mood.append((mood, datetime.now()))


def manual_mood_select(mood):
    """Record a manually-selected mood and refresh GUI."""
    mood_data[mood] += 1
    weekly_mood.append((mood, datetime.now()))
    refresh_display()


def get_weekly_mood():
    """Return the most frequent mood this week, or 'No data'."""
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    recent = [m for m, ts in weekly_mood if ts >= week_start]
    if not recent:
        return "No data"
    return max(set(recent), key=recent.count)


def record_and_analyze():
    """Capture speech, update mood, and refresh display."""
    text = speech_to_text()
    update_mood(text)
    refresh_display()


def speech_to_text():
    """Use microphone to capture daily mood as text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something about your day...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Speech not recognized"
    except sr.RequestError as e:
        return f"Error: {e}"


def refresh_display():
    """Redraw pie chart and update weekly mood label."""
    pie_chart.clear()
    pie_chart.pie(
        mood_data.values(),
        labels=mood_data.keys(),
        autopct='%1.1f%%',
        startangle=140
    )
    pie_chart.axis('equal')
    canvas.draw()
    weekly_label.config(text="Weekly Overall Mood: " + get_weekly_mood())

# --- GUI setup ---
root = tk.Tk()
root.title("Mood Analyzer")

tk.Button(root, text="🎤 Record and Analyze", command=record_and_analyze).pack(pady=10)

emoji_frame = tk.Frame(root)
emoji_frame.pack(pady=5)
tk.Label(emoji_frame, text="Or select your mood manually:").pack()
tk.Button(emoji_frame, text="😊 Happy", command=lambda: manual_mood_select('Happy')).pack(side='left', padx=5)
tk.Button(emoji_frame, text="😔 Sad", command=lambda: manual_mood_select('Sad')).pack(side='left', padx=5)
tk.Button(emoji_frame, text="😐 Neutral", command=lambda: manual_mood_select('Neutral')).pack(side='left', padx=5)

chart_frame = ttk.Frame(root)
chart_frame.pack(pady=10)
fig = Figure(figsize=(4, 4))
pie_chart = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, chart_frame)
canvas.get_tk_widget().pack()

weekly_label = tk.Label(root, text="Weekly Overall Mood: " + get_weekly_mood())
weekly_label.pack(pady=10)

root.mainloop()
