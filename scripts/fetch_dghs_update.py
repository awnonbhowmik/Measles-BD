"""
scripts/fetch_dghs_update.py
Fetch the latest DGHS measles briefing from BSS News (Bangladesh Sangbad Sangstha,
the official state wire), extract cumulative outbreak figures, and append a new row
to data/raw/dghs_daily_updates.csv if the data is newer than the last entry.

Strategy:
  1. Scrape the BSS News /news/health-news category page for recent article IDs
  2. Try each article (most recent first) until one passes the daily-briefing check
  3. Extract cumulative numbers with regex, validate, and append to CSV

Exit codes:
  0 — new row appended
  1 — no new data found (CSV already up to date, or source unavailable)

Usage:
  venv/bin/python scripts/fetch_dghs_update.py
"""

import os, re, sys, time, datetime, csv
import requests
from bs4 import BeautifulSoup

# ── Paths ─────────────────────────────────────────────────────────
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, 'data', 'raw', 'dghs_daily_updates.csv')
LOG_FILE = os.path.join(ROOT, 'data', 'processed', 'update_log.txt')

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64; rv:124.0) '
        'Gecko/20100101 Firefox/124.0'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
}
TIMEOUT = 20
SLEEP   = 1.5   # polite delay between article fetches

# Pages that list recent health articles, tried in order
CATEGORY_PAGES = [
    'https://www.bssnews.net/news/health-news',
    'https://www.bssnews.net/news/national',
]

# ── Regex patterns ─────────────────────────────────────────────────
PATTERNS = {
    # BSS News primary phrasing:
    # "number of suspected measles patients from March 15 to [date] is 27,164"
    'Suspected_Cases': [
        r'suspected\s+measles\s+patients?\s+from\s+March\s+15\s+to\s+\S+\s+\S+\s+is\s+([\d,]+)',
        r'suspected\s+measles\s+patients?\s+from\s+March\s+15[^.]+?is\s+([\d,]+)',
        r'([\d,]+)\s+suspected\s+measles\s+(?:cases?|patients?|infections?)',
        r'suspected\s+(?:measles\s+)?cases?\s*[:\-–—]\s*([\d,]+)',
        r'([\d,]+)\s+(?:total\s+)?(?:people\s+)?suspected\s+(?:measles\s+)?(?:cases?|infected)',
    ],
    # "number of confirmed measles patients from March 15 to till now is 3,934"
    'Confirmed_Cases': [
        r'confirmed\s+measles\s+patients?\s+from\s+March\s+15[^.]+?is\s+([\d,]+)',
        r'([\d,]+)\s+(?:lab[-\s]?)?confirmed\s+(?:measles\s+)?(?:cases?|infections?|patients?)',
        r'confirmed\s+(?:measles\s+)?cases?\s*[:\-–—]\s*([\d,]+)',
    ],
    # "190 people have died from suspected measles from March 15 to April 22"
    'Suspected_Deaths': [
        r'([\d,]+)\s+people\s+have\s+died\s+from\s+suspected\s+measles\s+from\s+March',
        r'([\d,]+)\s+(?:people\s+)?(?:have\s+)?died\s+(?:of|from)\s+suspected\s+measles',
        r'([\d,]+)\s+suspected\s+(?:measles\s+)?deaths?',
    ],
    # "38 people have died from confirmed measles from March 15 to April 22"
    'Confirmed_Deaths': [
        r'([\d,]+)\s+people\s+have\s+died\s+from\s+confirmed\s+measles\s+from\s+March',
        r'([\d,]+)\s+(?:people\s+)?(?:have\s+)?died\s+(?:of|from)\s+confirmed\s+measles',
        r'([\d,]+)\s+confirmed\s+(?:measles\s+)?deaths?',
    ],
    # "17,998 people have been admitted to hospitals with suspected measles"
    'Hospitalised': [
        r'([\d,]+)\s+people\s+have\s+been\s+admitted\s+to\s+hospitals',
        r'([\d,]+)\s+(?:patients?\s+)?(?:have been\s+|were\s+)?admitted',
        r'([\d,]+)\s+(?:people\s+)?(?:were\s+|have been\s+)?hospitalised',
        r'([\d,]+)\s+(?:people\s+)?(?:were\s+|have been\s+)?hospitali[sz]ed',
    ],
    'Districts_Affected': [
        r'([\d]+)\s+(?:out\s+of\s+64\s+)?districts?\s+(?:affected|reported)',
        r'(?:across|from|in)\s+([\d]+)\s+(?:out\s+of\s+64\s+)?districts?',
    ],
}

MONTHS = {
    'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
    'july':7,'august':8,'september':9,'october':10,'november':11,'december':12,
}


def _parse_int(s: str) -> int:
    return int(s.replace(',', '').strip())


def _extract(field: str, text: str):
    for pat in PATTERNS[field]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                return _parse_int(m.group(1))
            except ValueError:
                continue
    return None


def _last_csv_row() -> tuple[datetime.date | None, dict]:
    if not os.path.exists(CSV_PATH):
        return None, {}
    with open(CSV_PATH) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None, {}
    last = rows[-1]
    try:
        return datetime.date.fromisoformat(last['Date'].strip()), last
    except (ValueError, KeyError):
        return None, last


def _article_links_from_category() -> list[str]:
    """Scrape category pages and return numeric-ID article URLs, most-recent first."""
    links = []
    for page in CATEGORY_PAGES:
        try:
            r = requests.get(page, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
        except Exception as e:
            print(f'  [WARN] Category fetch failed ({page}): {e}')
            continue
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if re.search(r'bssnews\.net/(?:news(?:/health-news)?)/\d+', href):
                if href not in links:
                    links.append(href)
        if links:
            break
    # Sort by ID descending (highest = most recent)
    def _id(url):
        m = re.search(r'/(\d+)$', url)
        return int(m.group(1)) if m else 0
    return sorted(links, key=_id, reverse=True)


def _fetch_text(url: str) -> str | None:
    time.sleep(SLEEP)
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
    except Exception as e:
        print(f'    [WARN] Fetch failed: {e}')
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    # Use full page text — BSS News article body is reliably present in full text
    return soup.get_text(separator=' ', strip=True) if soup.body else None


def _is_briefing(text: str) -> bool:
    t = text.lower()
    return (
        bool(re.search(r'suspected.*case|case.*suspected', t)) and
        bool(re.search(r'died.*measles|measles.*died|measles.*death', t)) and
        bool(re.search(r'march 15|since march|from march', t))
    )


def _article_date(text: str) -> datetime.date | None:
    for pat in [
        r'(\d{1,2})\s+([A-Za-z]+)\s+(20\d{2})',
        r'([A-Za-z]+)\s+(\d{1,2}),?\s+(20\d{2})',
    ]:
        for m in re.finditer(pat, text[:3000]):
            try:
                g = m.groups()
                if re.match(r'[A-Za-z]', g[0]):
                    month_str, day, year = g[0].lower(), int(g[1]), int(g[2])
                else:
                    day, month_str, year = int(g[0]), g[1].lower(), int(g[2])
                month = MONTHS.get(month_str)
                if month and 2026 <= year <= 2030:
                    return datetime.date(year, month, day)
            except (ValueError, TypeError):
                continue
    return None


def run() -> bool:
    last_date, last_row = _last_csv_row()
    today = datetime.date.today()
    print(f'Last CSV entry : {last_date}')
    print(f'Today          : {today}')

    if last_date and last_date >= today:
        print('CSV already up to date for today.')
        return False

    links = _article_links_from_category()
    if not links:
        print('[ERROR] No article links found from BSS News.')
        return False
    print(f'Found {len(links)} candidate article(s) on category page.')

    best: dict | None = None

    for url in links[:15]:   # check up to 15 most-recent articles
        print(f'  → {url}')
        text = _fetch_text(url)
        if not text:
            continue

        if not _is_briefing(text):
            # Quick title check to avoid slow text parsing on non-measles stories
            if 'measles' not in text[:500].lower():
                continue
            print('    Not a daily briefing, skipping.')
            continue

        art_date = _article_date(text) or today
        print(f'    Article date: {art_date}')

        if last_date and art_date <= last_date:
            # This article is same age or older than our last entry
            # If we've already seen a newer article above, we can stop
            if best is not None:
                break
            print(f'    Not newer than last entry ({last_date}), skipping.')
            continue

        row = {
            'Date':               str(art_date),
            'Suspected_Cases':    _extract('Suspected_Cases',  text),
            'Confirmed_Cases':    _extract('Confirmed_Cases',  text),
            'Hospitalised':       _extract('Hospitalised',     text),
            'Suspected_Deaths':   _extract('Suspected_Deaths', text),
            'Confirmed_Deaths':   _extract('Confirmed_Deaths', text),
            'Districts_Affected': _extract('Districts_Affected', text),
            'Source':             f'BSS News {art_date} (auto)',
        }

        if row['Suspected_Cases'] is None:
            print('    Could not extract suspected cases, skipping.')
            continue

        print(f'    Extracted: susp={row["Suspected_Cases"]}, conf={row["Confirmed_Cases"]}, '
              f'hosp={row["Hospitalised"]}, s_dth={row["Suspected_Deaths"]}, c_dth={row["Confirmed_Deaths"]}')

        if best is None or (row['Suspected_Cases'] or 0) > (best['Suspected_Cases'] or 0):
            best = row

    if best is None:
        print('[WARN] No valid briefing data extracted.')
        return False

    # ── Sanity check: totals must not decrease ────────────────────
    for col in ('Suspected_Cases', 'Confirmed_Cases'):
        prev = int(last_row.get(col) or 0)
        new  = best.get(col) or 0
        if new < prev:
            print(f'[WARN] {col} decreased ({prev} → {new}); aborting append.')
            return False

    # ── Append ────────────────────────────────────────────────────
    fieldnames = [
        'Date','Suspected_Cases','Confirmed_Cases','Hospitalised',
        'Suspected_Deaths','Confirmed_Deaths','Districts_Affected','Source',
    ]
    write_header = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()
        w.writerow({k: ('' if best.get(k) is None else best[k]) for k in fieldnames})

    with open(LOG_FILE, 'a') as f:
        ts = datetime.datetime.now().isoformat(timespec='seconds')
        f.write(f"{ts} — DGHS fetch OK: {best['Date']} "
                f"({best['Suspected_Cases']} suspected, "
                f"{best['Confirmed_Deaths']} confirmed deaths)\n")

    print(f'\n✓ Appended row for {best["Date"]}')
    return True


if __name__ == '__main__':
    sys.exit(0 if run() else 1)
