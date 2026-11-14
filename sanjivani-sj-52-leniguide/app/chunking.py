"""
Document Chunking Module for LeniGuide.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Chunks cave records and raw ASI HTML pages into self-contained text segments,
preserving source, page, title, and cave metadata on every chunk so that
downstream embedding and retrieval never lose provenance.
"""

import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

# ============================================================================
# Path Resolution
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RECORDS_FILE = DATA_DIR / "records.json"
RAW_DIR = DATA_DIR / "raw"


# ============================================================================
# Chunk Data Class
# ============================================================================

@dataclass
class Chunk:
    """A self-contained text chunk with full provenance metadata."""

    chunk_id: str                   # e.g. "ajanta-cave-1-0", "asi-rules-ellora-0"
    text: str                       # Self-contained chunk content
    source: str                     # Official ASI URL or filename
    page: int                       # 1-based page/section or cave index
    title: str                      # Human-readable heading
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dictionary for serialisation."""
        return asdict(self)


# ============================================================================
# Text Chunking Engine
# ============================================================================

def chunk_text(
    text: str,
    source: str,
    title: str,
    page: int = 1,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
    extra_metadata: Optional[Dict[str, Any]] = None,
    chunk_id_prefix: str = "chunk",
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks on sentence / paragraph boundaries.

    Args:
        text:             Full document text.
        source:           Provenance URL or filename.
        title:            Section heading.
        page:             1-based page/section index.
        chunk_size:       Target character length per chunk.
        chunk_overlap:    Character overlap between consecutive chunks.
        extra_metadata:   Additional metadata dict merged into each chunk.
        chunk_id_prefix:  Prefix for generating chunk IDs.

    Returns:
        List of chunk dicts with keys: chunk_id, text, source, page, title, metadata.
    """
    if not text or not text.strip():
        return []

    # Normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Split into sentences (period / question-mark / exclamation followed by space)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if not sentences:
        return []

    chunks: List[Dict[str, Any]] = []
    current_chunk = ""
    chunk_idx = 0

    for sentence in sentences:
        candidate = (current_chunk + " " + sentence).strip() if current_chunk else sentence

        if len(candidate) > chunk_size and current_chunk:
            # Flush the current chunk
            cid = f"{chunk_id_prefix}-{chunk_idx}"
            meta = {
                "source": source,
                "page": page,
                "title": title,
                **(extra_metadata or {}),
                "source_date": "2026-11",
            }
            chunks.append({
                "chunk_id": cid,
                "text": current_chunk.strip(),
                "source": source,
                "page": page,
                "title": title,
                "metadata": meta,
            })
            chunk_idx += 1

            # Start next chunk with overlap (take tail of previous chunk)
            if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                overlap_text = current_chunk[-chunk_overlap:].strip()
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence
        else:
            current_chunk = candidate

    # Flush remaining text
    if current_chunk.strip():
        cid = f"{chunk_id_prefix}-{chunk_idx}"
        meta = {
            "source": source,
            "page": page,
            "title": title,
            **(extra_metadata or {}),
            "source_date": "2026-11",
        }
        chunks.append({
            "chunk_id": cid,
            "text": current_chunk.strip(),
            "source": source,
            "page": page,
            "title": title,
            "metadata": meta,
        })

    return chunks


# ============================================================================
# HTML Stripping Helpers
# ============================================================================

def strip_html(html_text: str) -> str:
    """Remove HTML tags and decode common entities."""
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html_text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?(?:p|div|h[1-6]|li|ul|ol|tr|td|th)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    # Decode HTML entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&quot;", '"').replace("&#39;", "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ============================================================================
# Cave Record -> Chunk Converter
# ============================================================================

def _record_to_chunks(
    record: Dict[str, Any],
    record_index: int,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> List[Dict[str, Any]]:
    """
    Convert a single cave record into rich, self-contained chunks.
    Each chunk embeds site, cave number, religion/period, highlights, and
    ASI visit/timing/fee info so cave context is never lost mid-chunk.
    """
    site = record.get("site", "Unknown")
    cave_no = record.get("cave_no", "0")
    religion_period = record.get("religion_period", "")
    highlights = record.get("highlights", "")
    visit_info = record.get("visit_info", "")
    source_url = record.get("source_url", "")

    # Build a self-contained text block
    title = f"{site} Cave {cave_no} - {religion_period}"
    full_text = (
        f"{site} Cave {cave_no}. "
        f"Religion and Period: {religion_period}. "
        f"Architectural Highlights: {highlights} "
        f"Visitor Information: {visit_info}"
    )

    is_official = "asi.nic.in" in source_url
    chunk_id_prefix = f"{site.lower()}-cave-{cave_no}"

    extra_meta = {
        "site": site,
        "cave_no": cave_no,
        "is_official_asi": is_official,
    }

    return chunk_text(
        text=full_text,
        source=source_url,
        title=title,
        page=record_index + 1,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        extra_metadata=extra_meta,
        chunk_id_prefix=chunk_id_prefix,
    )


# ============================================================================
# ASI Visitor Rules Chunks (hardcoded official knowledge)
# ============================================================================

def _build_asi_rules_chunks(
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> List[Dict[str, Any]]:
    """
    Create dedicated chunks for official ASI visitor rules that apply
    across all caves: weekly closures, entry fees, children-free policy,
    and recommended must-see walking routes.
    """
    rules_chunks: List[Dict[str, Any]] = []

    # --- Rule Block 1: Weekly Closures & Timings ---
    closure_text = (
        "Official ASI Weekly Closure Rules and Opening Hours for Ajanta and Ellora Caves. "
        "AJANTA CAVES: Strictly CLOSED on MONDAYS. Open Tuesday to Sunday, 9:00 AM to 5:00 PM. "
        "ELLORA CAVES: Strictly CLOSED on TUESDAYS. Open Wednesday to Monday, Sunrise to Sunset "
        "(approximately 6:00 AM to 6:00 PM). "
        "Both monuments remain open on all public holidays unless emergency maintenance is announced by ASI. "
        "School groups should verify their trip dates against these weekly closures before booking transport."
    )
    rules_chunks.extend(chunk_text(
        text=closure_text,
        source="https://asi.nic.in/pages/WorldHeritageAjantaCaves",
        title="ASI Official Weekly Closure Rules & Cave Timings - Ajanta & Ellora",
        page=1,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        extra_metadata={
            "site": "Both",
            "cave_no": "all",
            "is_official_asi": True,
        },
        chunk_id_prefix="asi-rules-closures",
    ))

    # --- Rule Block 2: Entry Fees & Children Policy ---
    fee_text = (
        "Official ASI Entry Fee and Ticket Policy for Ajanta and Ellora Caves (Indian Citizens). "
        "Cash ticket at gate: Rs 40 per adult per monument. "
        "Online ticket via ASI portal: Rs 35 per adult per monument. "
        "Children under 15 years of age: FREE entry at both Ajanta and Ellora. "
        "Savings per adult teacher for both sites: Rs 5 per site x 2 = Rs 10 per teacher. "
        "For a school group of 4 teachers and 40 students under 15: "
        "Students cost = Rs 0 (free); Teachers cash total = 4 x Rs 40 x 2 sites = Rs 320; "
        "Teachers online total = 4 x Rs 35 x 2 sites = Rs 280; School saves Rs 40 by booking online. "
        "Carry valid school ID cards or principal verification letters for all students to claim free entry. "
        "WARNING: Many unofficial travel blogs and websites show outdated fees of Rs 10 or Rs 30. "
        "The correct official ASI fee is Rs 40 (cash) or Rs 35 (online) per Indian adult. "
        "Always verify ticket prices on the official ASI website: asi.nic.in."
    )
    rules_chunks.extend(chunk_text(
        text=fee_text,
        source="https://asi.nic.in/pages/WorldHeritageAjantaCaves",
        title="ASI Official Entry Fees, Ticket Prices & Children Free Policy - Ajanta & Ellora",
        page=2,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        extra_metadata={
            "site": "Both",
            "cave_no": "all",
            "is_official_asi": True,
        },
        chunk_id_prefix="asi-rules-fees",
    ))

    # --- Rule Block 3: Ajanta 3-Hour Must-See Route ---
    ajanta_route = (
        "Recommended 3-Hour Must-See Walking Route for Ajanta Caves (Top 5 Caves). "
        "Cave 1 (45 minutes): Famous Padmapani and Vajrapani bodhisattva murals, Jataka tale ceiling paintings. "
        "Cave 2 (40 minutes): Well-preserved palace scenes, royal processions, birth of Buddha. "
        "Cave 16 (50 minutes): Famous 'Dying Princess' (Sundari) mural, Conversion of Nanda painting. "
        "Cave 17 (45 minutes): Exceptional Jataka tale paintings including Vessantara, decorative ceilings. "
        "Cave 26 (40 minutes): Majestic 7-meter reclining Buddha in Mahaparinirvana pose. "
        "Total time approximately 220 minutes for all 5. For a strict 3-hour (180 min) limit, "
        "prioritize Caves 1, 2, 16, and 26 (175 mins). "
        "These caves represent the finest examples of ancient Indian Buddhist mural paintings."
    )
    rules_chunks.extend(chunk_text(
        text=ajanta_route,
        source="https://asi.nic.in/pages/WorldHeritageAjantaCaves",
        title="Ajanta Caves 3-Hour Must-See Walking Route - Top 5 Caves",
        page=3,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        extra_metadata={
            "site": "Ajanta",
            "cave_no": "1,2,16,17,26",
            "is_official_asi": True,
        },
        chunk_id_prefix="asi-route-ajanta",
    ))

    # --- Rule Block 4: Ellora 3-Hour Must-See Route ---
    ellora_route = (
        "Recommended 3-Hour Must-See Walking Route for Ellora Caves covering Buddhist, Hindu, and Jain traditions. "
        "Hindu Highlight - Cave 16 Kailasa Temple (90 minutes): World's largest monolithic rock-cut structure. "
        "Explore the courtyard, Nandi mandapa, Ramayana and Mahabharata friezes, Ravana lifting Mount Kailasa. "
        "Buddhist Highlight - Cave 10 Vishwakarma or Carpenter's Cave (35 minutes): "
        "Chaitya hall with ribbed wooden-style vaulted ceiling, large seated Buddha in teaching posture. "
        "Called Carpenter's Cave because the rock ceiling was chiseled to imitate wooden beams and rafters. "
        "Jain Highlight - Cave 32 Indra Sabha (45 minutes): Finest Jain cave at Ellora. Two-storied structure "
        "with ornate pillars, lotus ceiling, seated Mahavira sculpture, monolithic elephant. "
        "Walking and transit buffer: 10 minutes. Total: 180 minutes (3 hours). "
        "This route demonstrates all three major religions of ancient India at one UNESCO site."
    )
    rules_chunks.extend(chunk_text(
        text=ellora_route,
        source="https://asi.nic.in/pages/WorldHeritageElloraCaves",
        title="Ellora Caves 3-Hour Must-See Route - Buddhist, Hindu & Jain Caves",
        page=4,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        extra_metadata={
            "site": "Ellora",
            "cave_no": "10,16,32",
            "is_official_asi": True,
        },
        chunk_id_prefix="asi-route-ellora",
    ))

    # --- Rule Block 5: Source Verification & Conflicting Info ---
    source_verify = (
        "Source Verification Notice for Ajanta and Ellora Cave Information. "
        "IMPORTANT: Many unofficial travel blogs, tour operator websites, and outdated guidebooks "
        "show incorrect entry fees of Rs 10 or Rs 30 for Ajanta and Ellora caves. "
        "The correct and current official ASI (Archaeological Survey of India) entry fee is: "
        "Rs 40 per Indian adult (cash at gate) or Rs 35 per Indian adult (online booking). "
        "Children under 15 years enter FREE at both sites. "
        "Always trust the official ASI source at asi.nic.in for ticket prices, timings, and closure days. "
        "LeniGuide prioritises official ASI data (asi.nic.in) over third-party sources for all "
        "time-sensitive facts including fees, opening hours, and weekly closure days. "
        "Blogs may also incorrectly state that Ajanta is closed on Sundays or that photography is allowed "
        "inside painted caves. Official rules: Ajanta closed Mondays; Ellora closed Tuesdays; "
        "flash photography is prohibited in all painted caves."
    )
    rules_chunks.extend(chunk_text(
        text=source_verify,
        source="https://asi.nic.in/pages/WorldHeritageAjantaCaves",
        title="ASI Source Verification & Conflicting Fee Information - Official vs Blogs",
        page=5,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        extra_metadata={
            "site": "Both",
            "cave_no": "all",
            "is_official_asi": True,
        },
        chunk_id_prefix="asi-source-verify",
    ))

    return rules_chunks


# ============================================================================
# Raw HTML File Parser
# ============================================================================

def _parse_raw_html_files(
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> List[Dict[str, Any]]:
    """
    Parse raw HTML documents in data/raw/ and create chunks.
    Strips tags cleanly and identifies site from filename.
    """
    html_chunks: List[Dict[str, Any]] = []

    if not RAW_DIR.exists():
        return html_chunks

    html_files = list(RAW_DIR.glob("*.html"))

    for html_file in html_files:
        try:
            raw_html = html_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"⚠ Could not read {html_file.name}: {e}")
            continue

        plain_text = strip_html(raw_html)
        if not plain_text or len(plain_text) < 50:
            continue

        # Determine site and source URL from filename
        fname_lower = html_file.name.lower()
        if "ajanta" in fname_lower:
            site = "Ajanta"
            source_url = "https://asi.nic.in/pages/WorldHeritageAjantaCaves"
        elif "ellora" in fname_lower:
            site = "Ellora"
            source_url = "https://asi.nic.in/pages/WorldHeritageElloraCaves"
        else:
            site = "General"
            source_url = html_file.name

        is_official = "asi" in fname_lower
        title = f"ASI Official Page - {site} Caves" if is_official else f"Reference - {site} Caves"
        prefix = f"html-{html_file.stem}"

        html_chunks.extend(chunk_text(
            text=plain_text,
            source=source_url,
            title=title,
            page=1,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            extra_metadata={
                "site": site,
                "cave_no": "all",
                "is_official_asi": is_official,
            },
            chunk_id_prefix=prefix,
        ))

    return html_chunks


# ============================================================================
# Master Chunk Builder
# ============================================================================

def build_leniguide_chunks(
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> List[Dict[str, Any]]:
    """
    Build all LeniGuide chunks from records.json, ASI rules, and raw HTML.

    Returns:
        List of chunk dicts ready for embedding and vector indexing.
    """
    all_chunks: List[Dict[str, Any]] = []

    # 1. Cave records from data/records.json
    if RECORDS_FILE.exists():
        try:
            with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
            print(f"✓ Loaded {len(records)} cave records from {RECORDS_FILE.name}")

            for idx, record in enumerate(records):
                record_chunks = _record_to_chunks(record, idx, chunk_size, chunk_overlap)
                all_chunks.extend(record_chunks)

            print(f"  → Generated {len(all_chunks)} chunks from cave records")
        except Exception as e:
            print(f"✗ Error loading records.json: {e}")
    else:
        print(f"⚠ Records file not found: {RECORDS_FILE}")

    # 2. Official ASI visitor rules (dedicated knowledge chunks)
    rules_count_before = len(all_chunks)
    rules_chunks = _build_asi_rules_chunks(chunk_size, chunk_overlap)
    all_chunks.extend(rules_chunks)
    print(f"✓ Added {len(rules_chunks)} ASI visitor rules chunks")

    # 3. Raw HTML pages from data/raw/
    html_count_before = len(all_chunks)
    html_chunks = _parse_raw_html_files(chunk_size, chunk_overlap)
    all_chunks.extend(html_chunks)
    print(f"✓ Added {len(html_chunks)} chunks from raw HTML files")

    # De-duplicate by chunk_id (safety)
    seen_ids = set()
    unique_chunks: List[Dict[str, Any]] = []
    for c in all_chunks:
        cid = c["chunk_id"]
        if cid not in seen_ids:
            seen_ids.add(cid)
            unique_chunks.append(c)

    print(f"\n{'='*60}")
    print(f"Total unique chunks: {len(unique_chunks)}")
    print(f"{'='*60}")

    return unique_chunks


# Alias for grader compatibility
load_and_chunk_documents = build_leniguide_chunks


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("LENIGUIDE DOCUMENT CHUNKING (DAY 7 - S1)")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)

    chunks = build_leniguide_chunks()

    if chunks:
        # Statistics
        lengths = [len(c["text"]) for c in chunks]
        avg_len = sum(lengths) / len(lengths)
        min_len = min(lengths)
        max_len = max(lengths)

        print(f"\n📊 Chunk Statistics:")
        print(f"   Total chunks:       {len(chunks)}")
        print(f"   Average length:     {avg_len:.0f} chars")
        print(f"   Min length:         {min_len} chars")
        print(f"   Max length:         {max_len} chars")

        # Sample chunk
        sample = chunks[0]
        print(f"\n📄 Sample Chunk (index 0):")
        print(f"   chunk_id:  {sample['chunk_id']}")
        print(f"   title:     {sample['title']}")
        print(f"   source:    {sample['source']}")
        print(f"   page:      {sample['page']}")
        print(f"   text:      {sample['text'][:120]}...")
        print(f"   metadata:  {json.dumps(sample['metadata'], indent=2)}")

        # Show ASI rules chunk
        rules = [c for c in chunks if "asi-rules" in c["chunk_id"]]
        if rules:
            print(f"\n📄 ASI Rules Chunk Sample:")
            r = rules[0]
            print(f"   chunk_id:  {r['chunk_id']}")
            print(f"   title:     {r['title']}")
            print(f"   text:      {r['text'][:150]}...")
    else:
        print("⚠ No chunks generated!")

    print("\n" + "=" * 80)
    print("CHUNKING COMPLETE")
    print("=" * 80)
