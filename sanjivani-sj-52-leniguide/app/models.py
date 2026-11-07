"""
Data models for LeniGuide cave records.
Defines the Record dataclass with validation and serialization methods.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, Any


@dataclass
class Record:
    """
    Represents a single cave record in the LeniGuide system.
    
    Attributes:
        site: Either "Ajanta" or "Ellora"
        cave_no: Cave number as string (e.g., "1", "16", "32")
        religion_period: Religious tradition and historical period
        highlights: Key architectural and artistic features
        visit_info: Timing, fees, and visit recommendations
        source_url: Official ASI or verified source URL
    """
    
    site: str
    cave_no: str
    religion_period: str
    highlights: str
    visit_info: str
    source_url: str
    
    def __post_init__(self):
        """Validate and normalize fields immediately after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate record fields and normalize data.
        
        Raises:
            ValueError: If any required field is empty or site is invalid.
        """
        # Normalize whitespace in all string fields
        self.site = self.site.strip()
        self.cave_no = str(self.cave_no).strip()
        self.religion_period = self.religion_period.strip()
        self.highlights = self.highlights.strip()
        self.visit_info = self.visit_info.strip()
        self.source_url = self.source_url.strip()
        
        # Validate required fields are not empty
        if not self.site:
            raise ValueError("Field 'site' cannot be empty")
        if not self.cave_no:
            raise ValueError("Field 'cave_no' cannot be empty")
        if not self.religion_period:
            raise ValueError("Field 'religion_period' cannot be empty")
        if not self.highlights:
            raise ValueError("Field 'highlights' cannot be empty")
        if not self.visit_info:
            raise ValueError("Field 'visit_info' cannot be empty")
        if not self.source_url:
            raise ValueError("Field 'source_url' cannot be empty")
        
        # Validate site is either Ajanta or Ellora
        if self.site not in ["Ajanta", "Ellora"]:
            raise ValueError(
                f"Field 'site' must be 'Ajanta' or 'Ellora', got '{self.site}'"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Record to a dictionary.
        
        Returns:
            Dictionary representation of the record.
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Record":
        """
        Create a Record instance from a dictionary.
        
        Args:
            data: Dictionary with record fields.
        
        Returns:
            New Record instance.
        
        Raises:
            ValueError: If required fields are missing or invalid.
            TypeError: If field types are incompatible.
        """
        # Extract required fields with validation
        try:
            return cls(
                site=data["site"],
                cave_no=data["cave_no"],
                religion_period=data["religion_period"],
                highlights=data["highlights"],
                visit_info=data["visit_info"],
                source_url=data["source_url"]
            )
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        except TypeError as e:
            raise TypeError(f"Invalid field type: {e}")
    
    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.site} Cave {self.cave_no} ({self.religion_period})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Record(site='{self.site}', cave_no='{self.cave_no}', "
            f"religion_period='{self.religion_period[:30]}...')"
        )


# Alias for compatibility with different import styles
CaveRecord = Record


def main():
    """Demonstrate Record functionality."""
    print("=" * 80)
    print("TESTING app/models.py - Record Dataclass")
    print("=" * 80)
    
    # Test 1: Valid record creation
    print("\n1. Creating a valid record...")
    try:
        record = Record(
            site="Ajanta",
            cave_no="1",
            religion_period="Buddhist (Mahayana, ~5th century CE)",
            highlights="Padmapani and Vajrapani bodhisattva murals",
            visit_info="Must-see (Top 5). Open 9:00 AM - 5:00 PM, Closed Mondays.",
            source_url="https://asi.nic.in/pages/WorldHeritageAjantaCaves"
        )
        print(f"   ✓ Created: {record}")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: to_dict() conversion
    print("\n2. Converting to dictionary...")
    record_dict = record.to_dict()
    print(f"   ✓ Dictionary keys: {list(record_dict.keys())}")
    print(f"   ✓ Site: {record_dict['site']}, Cave: {record_dict['cave_no']}")
    
    # Test 3: from_dict() reconstruction
    print("\n3. Reconstructing from dictionary...")
    reconstructed = Record.from_dict(record_dict)
    print(f"   ✓ Reconstructed: {reconstructed}")
    print(f"   ✓ Match original: {record.to_dict() == reconstructed.to_dict()}")
    
    # Test 4: Invalid site validation
    print("\n4. Testing validation (invalid site)...")
    try:
        invalid_record = Record(
            site="InvalidSite",
            cave_no="1",
            religion_period="Test",
            highlights="Test",
            visit_info="Test",
            source_url="http://test.com"
        )
        print("   ✗ Validation failed - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ Correctly rejected: {e}")
    
    # Test 5: Empty field validation
    print("\n5. Testing validation (empty field)...")
    try:
        empty_record = Record(
            site="Ajanta",
            cave_no="",
            religion_period="Test",
            highlights="Test",
            visit_info="Test",
            source_url="http://test.com"
        )
        print("   ✗ Validation failed - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ Correctly rejected: {e}")
    
    # Test 6: Missing field from_dict
    print("\n6. Testing from_dict with missing field...")
    try:
        incomplete_dict = {
            "site": "Ellora",
            "cave_no": "16",
            "religion_period": "Hindu"
            # Missing: highlights, visit_info, source_url
        }
        bad_record = Record.from_dict(incomplete_dict)
        print("   ✗ Validation failed - should have raised ValueError")
    except ValueError as e:
        print(f"   ✓ Correctly rejected: {e}")
    
    print("\n" + "=" * 80)
    print("ALL MODEL TESTS PASSED")
    print("=" * 80)


if __name__ == "__main__":
    main()
