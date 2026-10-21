
# Python Paginated Web Scraper

## Project Overview
A Python web scraper that collects book information from a practice website, navigates multiple pages, removes duplicate titles, handles request failures, and exports structured data to CSV and JSON.

## Objectives
- Fetch website pages using Requests.
- Parse HTML using BeautifulSoup.
- Navigate paginated book listings.
- Extract book titles, prices, ratings, and page numbers.
- Handle request errors and retry failed requests.
- Export data to CSV and JSON.
- Validate record counts and required fields.

## Website
https://books.toscrape.com/

This project uses a practice website intended for web scraping education.

## Technologies
- Python 3
- Requests
- BeautifulSoup4
- CSV and JSON
- pathlib

## Project Structure
```text
.
├── main.py
├── validate_data.py
├── requirements.txt
├── README.md
├── .gitignore
├── task1/
├── task2/
├── task3/
├── task4/
└── data/
    ├── books.csv
    └── books.json
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Datheon_Python_for_Data_Engineering_Automation_Internship
```

### 2. Create a virtual environment
```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 5. Run the scraper
```bash
python main.py
```

### 6. Validate the output
```bash
python validate_data.py
```

## Output Files
- `data/books.csv` — spreadsheet-friendly records.
- `data/books.json` — structured JSON records.

## Error Handling
The scraper retries failed requests, checks HTTP response status, skips incomplete records, and stops when pagination ends or a page cannot be fetched.

## Data Validation
The validation script checks required fields, duplicate titles, CSV/JSON record counts, and the 100-record threshold.

## Limitations
The current version is configured to scrape up to five pages. The actual record count depends on successful requests and valid records returned by the source website.

## Author
Yash Vikas Gayake
