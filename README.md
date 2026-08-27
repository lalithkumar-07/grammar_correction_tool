# 📝 GrammarAI — Grammar Correction Tool

A beautiful, dark-themed grammar correction web app built with **Python Flask** and **LanguageTool**.

---

## 📁 Project Structure

```
grammar_tool/
│
├── app.py                  ← Flask backend (the server)
├── requirements.txt        ← Python packages to install
├── README.md               ← This guide
│
└── templates/
    └── index.html          ← Frontend (HTML + CSS + JS)
```

---

## ⚙️ Installation — Step by Step

### Step 1: Install Python
- Go to https://python.org and download Python 3.10+
- During install, CHECK "Add Python to PATH"
- Verify: open terminal and type:
  ```
  python --version
  ```

### Step 2: Create Project Folder
```bash
mkdir grammar_tool
cd grammar_tool
```

### Step 3: Create a Virtual Environment
A virtual environment keeps your project's packages separate from other Python projects.
```bash
python -m venv venv
```

Activate it:
- **Windows:**  `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

You'll see `(venv)` in your terminal when it's active.

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ Note: `language-tool-python` will download a Java-based language model (~200MB) on first run. This is normal and happens automatically.

### Step 5: Run the App
```bash
python app.py
```

You should see:
```
==================================================
  Grammar Correction Tool is starting...
  Open your browser and go to:
  http://127.0.0.1:5000
==================================================
```

### Step 6: Open in Browser
Visit: **http://127.0.0.1:5000**

---

## 🚀 How It Works

1. You type/paste text into the editor
2. Click **"Check Grammar"** (or press Ctrl+Enter)
3. JavaScript sends your text to Flask via a **POST /check** API call
4. Flask passes text to **LanguageTool** (the grammar engine)
5. LanguageTool returns all errors + suggestions
6. Flask sends JSON back to JavaScript
7. JavaScript displays corrected text, stats, and issue list

---

## 🛑 Stopping the App
Press `Ctrl + C` in the terminal.

---

## 🔧 Troubleshooting

| Problem | Solution |
|--------|----------|
| `python not found` | Reinstall Python and check "Add to PATH" |
| `pip not found` | Use `python -m pip install -r requirements.txt` |
| First run is slow | LanguageTool is downloading (200MB) — wait for it |
| Port 5000 in use | Change `port=5000` to `port=5001` in app.py |
| Java error | Install Java JDK 8+: https://adoptium.net |
