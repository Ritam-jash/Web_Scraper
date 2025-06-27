# 🗺️ Google Maps Business Scraper

A robust, modular Python scraper for extracting business data from Google Maps using Selenium. Designed for reliability, anti-detection, and clean output in CSV, Excel, and JSON formats.

---

## 🚀 Features
- Extracts 12–15+ data points per business (name, address, phone, website, rating, reviews, coordinates, etc.)
- Handles Google Maps scrolling, pagination, and dynamic loading
- Advanced website filtering (removes aggregator/chain links)
- Anti-detection: proxy support, user-agent rotation, smart delays
- Output to CSV, Excel, and JSON (with post-processing and cleaning)
- Modular, extensible codebase
- Logging and error handling

---

## 📦 Requirements
- Python 3.8+
- Google Chrome browser
- ChromeDriver (path configurable in `src/scraper/browser_manager.py`)
- See `requirements.txt` for Python dependencies

---

## ⚡ Setup
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd gmaps-scraper-python
   ```
2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Mac/Linux
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure ChromeDriver path:**
   - Edit `src/scraper/browser_manager.py` and set the `chromedriver_path` variable to your local ChromeDriver executable.

---

## 🛠️ Usage
Run the scraper from the project root with your desired options:

### **Headed (browser visible):**
```bash
python main.py --search "restaurants in Kolkata" --max-results 50 --output-format csv
```

### **Headless (browser hidden):**
```bash
python main.py --search "restaurants in Kolkata" --max-results 50 --output-format csv --headless
```

#### **Arguments:**
- `--search` / `-s` : Search query (required)
- `--max-results` / `-m` : Max businesses to scrape (default: 100)
- `--output-format` / `-f` : Output format (`csv`, `json`, `excel`, or `all`)
- `--headless` : Run browser in headless mode

---

## 📂 Output
- Results are saved in `data/output/` as CSV, Excel, and/or JSON files.
- Filtered Excel files are automatically generated with only real business websites.
- Logs are saved in `data/logs/`.

---

## 🧩 Project Structure
```
gmaps-scraper-python/
  main.py                # Entry point
  config/                # Settings & selectors
  src/
    scraper/             # Scraper logic
    models/              # Data models
    utils/               # Utilities (file, logger, etc.)
  data/
    output/              # Scraped data (csv, excel, json)
    logs/                # Log files
    screenshots/         # (Disabled by default)
  requirements.txt
  README.md
```

---

## 📝 Troubleshooting
- **Slow scraping?**
  - Screenshots are disabled by default for speed.
  - Smart waits are used instead of fixed sleeps.
  - For large queries, Google Maps may throttle or block—use proxies and moderate delays.
- **Missing data?**
  - Some businesses may hide info or load slowly. The scraper uses robust waits and retries.
- **ChromeDriver errors?**
  - Ensure your ChromeDriver version matches your Chrome browser.
  - Update the path in `src/scraper/browser_manager.py`.

---

## 🙏 Credits
- Developed by Ritam Jash
- Powered by Selenium, pandas, rapidfuzz, and open-source libraries

---

## 📬 Feedback & Contributions
Pull requests and issues are welcome! For feature requests or bug reports, please open an issue on GitHub.

---

**Happy scraping!** 🥳 