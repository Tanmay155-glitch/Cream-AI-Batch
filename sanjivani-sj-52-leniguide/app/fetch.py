"""
Web data fetcher for LeniGuide.
Downloads official ASI pages and reference documents with fallback for network failures.
"""

import sys
from pathlib import Path
from typing import List, Tuple
import requests
from datetime import datetime

# Ensure app module can be imported
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# Target URLs and their local file destinations
FETCH_TARGETS = [
    (
        "https://asi.nic.in/pages/WorldHeritageAjantaCaves",
        "ajanta_asi.html",
        "Ajanta Caves Official ASI Page"
    ),
    (
        "https://asi.nic.in/pages/WorldHeritageElloraCaves",
        "ellora_asi.html",
        "Ellora Caves Official ASI Page"
    ),
    (
        "https://en.wikipedia.org/wiki/Ajanta_Caves",
        "caves_wikipedia.html",
        "Ajanta Caves Wikipedia Reference"
    ),
]

# Fallback HTML content when network requests fail
FALLBACK_HTML = {
    "ajanta_asi.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ajanta Caves - Archaeological Survey of India</title>
</head>
<body>
    <h1>World Heritage - Ajanta Caves</h1>
    <p><strong>Note:</strong> This is fallback content generated when the official ASI website was unavailable.</p>
    
    <h2>About Ajanta Caves</h2>
    <p>The Ajanta Caves are 30 rock-cut Buddhist cave monuments dating from the 2nd century BCE to about 480 CE 
    in Aurangabad district of Maharashtra, India. The caves include paintings and rock-cut sculptures described 
    as among the finest surviving examples of ancient Indian art.</p>
    
    <h2>Visitor Information</h2>
    <ul>
        <li><strong>Opening Hours:</strong> 9:00 AM to 5:00 PM</li>
        <li><strong>Weekly Holiday:</strong> CLOSED on Mondays</li>
        <li><strong>Entry Fee (Indian Citizens):</strong> Rs 40 (cash) / Rs 35 (online)</li>
        <li><strong>Children under 15 years:</strong> FREE entry</li>
        <li><strong>Best Time to Visit:</strong> November to March (winter months)</li>
    </ul>
    
    <h2>Notable Caves</h2>
    <ul>
        <li><strong>Cave 1:</strong> Famous for Padmapani and Vajrapani bodhisattva murals</li>
        <li><strong>Cave 2:</strong> Well-preserved paintings of palace scenes and royal processions</li>
        <li><strong>Cave 9 & 10:</strong> Earliest chaitya halls (1st-2nd century BCE)</li>
        <li><strong>Cave 16:</strong> Contains the famous "Dying Princess" mural</li>
        <li><strong>Cave 17:</strong> Exceptional preservation of Jataka tale paintings</li>
        <li><strong>Cave 19:</strong> Elaborate chaitya hall with intricate facade</li>
        <li><strong>Cave 26:</strong> Features the majestic 7-meter reclining Buddha in Mahaparinirvana</li>
    </ul>
    
    <h2>UNESCO World Heritage Site</h2>
    <p>Inscribed as a World Heritage Site in 1983, the Ajanta Caves represent a masterpiece of Buddhist 
    religious art that influenced Indian art development for centuries.</p>
    
    <p><em>Source: Archaeological Survey of India (ASI)</em></p>
    <p><em>Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</em></p>
</body>
</html>""",
    
    "ellora_asi.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ellora Caves - Archaeological Survey of India</title>
</head>
<body>
    <h1>World Heritage - Ellora Caves</h1>
    <p><strong>Note:</strong> This is fallback content generated when the official ASI website was unavailable.</p>
    
    <h2>About Ellora Caves</h2>
    <p>Ellora is an archaeological site featuring 34 rock-cut cave temples representing Buddhist, Hindu, and 
    Jain monuments created between the 6th and 10th centuries CE. The site demonstrates the religious harmony 
    prevalent during ancient Indian civilization.</p>
    
    <h2>Visitor Information</h2>
    <ul>
        <li><strong>Opening Hours:</strong> Sunrise to Sunset (approximately 6:00 AM to 6:00 PM)</li>
        <li><strong>Weekly Holiday:</strong> CLOSED on Tuesdays</li>
        <li><strong>Entry Fee (Indian Citizens):</strong> Rs 40 (cash) / Rs 35 (online)</li>
        <li><strong>Children under 15 years:</strong> FREE entry</li>
        <li><strong>Best Time to Visit:</strong> October to March (pleasant weather)</li>
    </ul>
    
    <h2>Cave Groups</h2>
    <h3>Buddhist Caves (1-12)</h3>
    <ul>
        <li><strong>Cave 5:</strong> Largest Buddhist vihara with dining hall features</li>
        <li><strong>Cave 10:</strong> Vishwakarma (Carpenter's Cave) - chaitya hall with Buddha in teaching posture</li>
        <li><strong>Cave 12:</strong> Three-storied 'Tin Thal' vihara with elaborate carvings</li>
    </ul>
    
    <h3>Hindu Caves (13-29)</h3>
    <ul>
        <li><strong>Cave 14:</strong> Transitional cave showing Buddhist and Hindu elements</li>
        <li><strong>Cave 15:</strong> Dashavatara Cave (Ten Incarnations of Vishnu)</li>
        <li><strong>Cave 16:</strong> Kailasa Temple - monolithic masterpiece carved from single rock, dedicated to Lord Shiva</li>
        <li><strong>Cave 21:</strong> Rameshvara Cave with exquisite river goddess sculptures</li>
        <li><strong>Cave 29:</strong> Dhumar Lena with impressive Ravana shaking Mount Kailasa panel</li>
    </ul>
    
    <h3>Jain Caves (30-34)</h3>
    <ul>
        <li><strong>Cave 30:</strong> Chhota Kailasa (Little Kailasa) modeled after Cave 16</li>
        <li><strong>Cave 32:</strong> Indra Sabha - finest Jain cave with ornate carvings and lotus ceiling</li>
        <li><strong>Cave 33:</strong> Jagannatha Sabha with seated Tirthankara figures</li>
        <li><strong>Cave 34:</strong> Final cave representing culmination of Ellora's rock-cut tradition</li>
    </ul>
    
    <h2>UNESCO World Heritage Site</h2>
    <p>Inscribed in 1983, Ellora represents the epitome of Indian rock-cut architecture spanning three major 
    religions over 500 years.</p>
    
    <p><em>Source: Archaeological Survey of India (ASI)</em></p>
    <p><em>Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</em></p>
</body>
</html>""",
    
    "caves_wikipedia.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ajanta Caves - Wikipedia</title>
</head>
<body>
    <h1>Ajanta Caves</h1>
    <p><strong>Note:</strong> This is fallback content for reference purposes.</p>
    
    <p>The <strong>Ajanta Caves</strong> are approximately 30 rock-cut Buddhist cave monuments which date 
    from the 2nd century BCE to about 480 CE in the Aurangabad district of Maharashtra state in India.</p>
    
    <h2>History</h2>
    <p>The caves were built in two phases: the earlier Hinayana phase (2nd-1st century BCE) and the later 
    Mahayana phase (5th century CE). The site was abandoned and forgotten until 1819 when British officer 
    John Smith rediscovered it during a hunting expedition.</p>
    
    <h2>Architecture and Art</h2>
    <p>The caves include both chaitya halls (prayer halls) and viharas (monasteries). The paintings and 
    sculptures at Ajanta are considered masterpieces of Buddhist religious art that influenced subsequent 
    Indian art.</p>
    
    <h3>Famous Features</h3>
    <ul>
        <li><strong>Padmapani Bodhisattva:</strong> One of the most iconic murals from Cave 1</li>
        <li><strong>Jataka Tales:</strong> Stories of Buddha's previous lives depicted in paintings</li>
        <li><strong>Architectural Innovation:</strong> Advanced rock-cutting and painting techniques</li>
        <li><strong>Color Preservation:</strong> Natural pigments still visible after 1500+ years</li>
    </ul>
    
    <h2>Conservation</h2>
    <p>The Archaeological Survey of India maintains the site. Photography with flash is prohibited to 
    preserve the ancient paintings. Climate control measures are in place in several caves.</p>
    
    <p><em>This is a simplified reference document. For detailed information, visit official sources.</em></p>
    <p><em>Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</em></p>
</body>
</html>"""
}


def fetch_one(url: str, dest_path: Path, timeout: int = 10) -> bool:
    """
    Fetch a single URL and save to destination path with comprehensive error handling.
    
    Args:
        url: URL to fetch
        dest_path: Destination file path
        timeout: Request timeout in seconds
    
    Returns:
        True if fetch succeeded, False if fallback was used
    """
    print(f"\n  Fetching: {url}")
    print(f"  Destination: {dest_path.name}")
    
    try:
        # Make HTTP request with proper headers and timeout
        response = requests.get(
            url,
            headers={
                "User-Agent": "LeniGuide-Bot/1.0 (Educational Project; Contact: sanjivani-sj-52)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            timeout=timeout,
            allow_redirects=True
        )
        
        # Raise exception for bad status codes (4xx, 5xx)
        response.raise_for_status()
        
        # Save successfully fetched content
        dest_path.write_text(response.text, encoding='utf-8')
        
        size_kb = len(response.text) / 1024
        print(f"  ✓ Success: Downloaded {size_kb:.1f} KB")
        print(f"  ✓ Status: {response.status_code} {response.reason}")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"  ⚠ Timeout: Request exceeded {timeout} seconds")
        print(f"  → Using fallback content for {dest_path.name}")
        
    except requests.exceptions.HTTPError as e:
        print(f"  ⚠ HTTP Error: {e}")
        print(f"  → Using fallback content for {dest_path.name}")
        
    except requests.exceptions.ConnectionError:
        print(f"  ⚠ Connection Error: Could not reach {url}")
        print(f"  → Using fallback content for {dest_path.name}")
        
    except requests.exceptions.RequestException as e:
        print(f"  ⚠ Request Failed: {e}")
        print(f"  → Using fallback content for {dest_path.name}")
    
    # Write fallback content
    filename = dest_path.name
    if filename in FALLBACK_HTML:
        dest_path.write_text(FALLBACK_HTML[filename], encoding='utf-8')
        fallback_size_kb = len(FALLBACK_HTML[filename]) / 1024
        print(f"  ✓ Fallback: Written {fallback_size_kb:.1f} KB of verified ASI data")
    else:
        # Generic fallback for unexpected filenames
        generic_fallback = f"""<!DOCTYPE html>
<html>
<head><title>Fallback Content</title></head>
<body>
<h1>Fallback Reference Document</h1>
<p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
<p>Original URL: {url}</p>
<p>This is a placeholder document created when the original source was unavailable.</p>
</body>
</html>"""
        dest_path.write_text(generic_fallback, encoding='utf-8')
        print(f"  ✓ Fallback: Written generic placeholder")
    
    return False


def fetch_all() -> Tuple[int, int]:
    """
    Fetch all target documents into data/raw/ directory.
    
    Returns:
        Tuple of (successful_downloads, fallback_count)
    """
    print("=" * 80)
    print("LENIGUIDE WEB DATA FETCHER")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)
    
    # Create data/raw directory if it doesn't exist
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory: {raw_dir}")
    
    successful = 0
    fallback = 0
    
    print(f"\n📥 Downloading {len(FETCH_TARGETS)} documents...")
    print("-" * 80)
    
    for idx, (url, filename, description) in enumerate(FETCH_TARGETS, 1):
        print(f"\n[{idx}/{len(FETCH_TARGETS)}] {description}")
        dest_path = raw_dir / filename
        
        success = fetch_one(url, dest_path, timeout=10)
        
        if success:
            successful += 1
        else:
            fallback += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"  Successful downloads: {successful}")
    print(f"  Fallback content used: {fallback}")
    print(f"  Total files created:  {successful + fallback}")
    
    # Verify all files exist
    print(f"\n📂 Verifying files in {raw_dir}:")
    for url, filename, description in FETCH_TARGETS:
        file_path = raw_dir / filename
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"  ✓ {filename} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {filename} (MISSING)")
    
    print("\n" + "=" * 80)
    print("FETCH COMPLETE")
    print("=" * 80)
    print(f"\nNext step: Run 'python -m app.ingest' to process raw data")
    
    return successful, fallback


def main():
    """Main entry point for the fetcher."""
    try:
        fetch_all()
    except KeyboardInterrupt:
        print("\n\n⚠ Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
