# Moroccan Justice Portal PDF Downloader

This script downloads **all PDF files** from the Moroccan Ministry of Justice portal
All of the data aquired from tis was used to make https://9anonai.com

It mirrors the **exact folder/category structure** from the website and saves everything locally.

---

## What This Script Does

* Recursively crawls justice portal resources
* Starts from **resource IDs 12 and 569**
* Recreates the same category/subcategory structure locally
* Downloads **PDF files only**
* Preserves original filenames (Arabic supported)
* Skips files that already exist
* Retries failed requests automatically

Output goes into a `laws/` directory.

---

## Folder Structure Example

```
laws/
├── القوانين/
│   ├── القانون_الجنائي.pdf
│   └── ...
└── المراسيم/
    ├── 2023/
    │   └── decree_2023.pdf
```

Same structure as the website. No flattening.

---

## Requirements

* Python **3.10+**
* Internet connection

Python packages:

```bash
pip install requests
```

(Standard library handles the rest.)

---

## Usage

Run the script directly:

```bash
python download_laws.py
```

That’s it.
No arguments. No config files.

---

## Configuration (Optional)

You can edit these in the script if needed:

```python
ROOT_FOLDER_IDS = [12, 569]   # Starting categories
OUTPUT_DIR = Path("laws")    # Output directory
DOWNLOAD_DELAY = 0.5         # Delay between downloads
MAX_RETRIES = 3              # Retry attempts
```

---

## Notes / Warnings

* The script uses **polite delays** to avoid hammering the server.
* If the API structure changes, the script will break.
* This relies on undocumented endpoints (`/api/folders`).
* Use responsibly. You’re hitting a government website.

---

## Legal Disclaimer

This script is for **educational and research purposes**.
You are responsible for how you use the downloaded material and for complying with local laws and website terms.

---

## Author

Built for scraping and archiving Moroccan legal documents efficiently.
No fluff. Just works.


