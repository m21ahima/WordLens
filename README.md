# 📖 WordLens

> Highlight any word, anywhere on your screen — and instantly see its meaning.

WordLens runs silently in the background. The moment you copy or highlight a single word (in any app — browser, PDF reader, VS Code, notes, anything), a clean floating card pops up near your cursor showing the definition. Dismiss it with one click.

---

## ✨ Features

- **System-wide** — works in every app, not just browsers
- **Instant lookup** — definition appears within a second
- **Clean card UI** — word, phonetic, part-of-speech pill, up to 2 definitions
- **Auto-dismisses** after 8 seconds, or click ✕ to close
- **No API key needed** — uses the free [DictionaryAPI.dev](https://dictionaryapi.dev/)
- **Lightweight** — ~200 lines of Python, no heavy dependencies

---

## 🖥️ Requirements

- Python **3.8+**
- Works on **Windows**, **macOS**, and **Linux**
- Internet connection (for dictionary lookups)

---

## 🚀 Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/WordLens.git
cd WordLens
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Linux users:** You may also need `xclip` or `xsel` for clipboard access:
> ```bash
> sudo apt install xclip
> ```

### 4. Run WordLens

```bash
python main.py
```

You'll see:
```
📖 WordLens is running...
   Highlight any word in any app to see its meaning.
   Press Ctrl+C to quit.
```

Now just **copy/highlight any word** — the definition card will appear! 🎉

---

## 📁 Project Structure

```
WordLens/
├── main.py          # Entry point — starts listener + overlay
├── listener.py      # Clipboard watcher — detects single-word selections
├── dictionary.py    # Fetches definitions from DictionaryAPI.dev
├── overlay.py       # Floating card UI built with tkinter
├── requirements.txt # Python dependencies
└── README.md        # You're reading this!
```

---

## 🔧 How It Works

```
You highlight a word (any app)
        ↓
listener.py detects clipboard change
        ↓
Validates it's a single word (not a sentence)
        ↓
dictionary.py fetches from DictionaryAPI.dev
        ↓
overlay.py shows a floating card near your cursor
        ↓
Click ✕ or wait 8s → card disappears
```

---

## 💡 Tips

- Works best when you **copy** the word (Ctrl+C / Cmd+C)
- Only triggers for **single words** — copying a sentence won't show anything
- Hyphenated words like `well-being` are supported

---

## 🛣️ Roadmap / Future Ideas

- [ ] Hotkey to toggle WordLens on/off
- [ ] History panel — all words you've looked up
- [ ] Add synonyms / antonyms
- [ ] Support multiple languages
- [ ] System tray icon
- [ ] Offline dictionary fallback

---

## 📜 License

MIT — free to use, modify, and share.