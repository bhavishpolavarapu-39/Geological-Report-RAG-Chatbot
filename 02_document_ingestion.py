"""
GeoMind AI - Document Ingestion Pipeline
Production-grade document parsing, OCR, metadata extraction, and chunking.

Features:
- PDF text extraction
- OCR for scanned documents
- Table extraction
- Coordinate detection
- Assay data parsing
- Geological metadata extraction
"""

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import asyncio
import logging
import json
from datetime import datetime
from abc import ABC, abstractmethod

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import numpy as np
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class DocumentFormat(Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    IMAGE = "image"
    CSV = "csv"


@dataclass
class ExtractedTable:
    """Represents an extracted table."""
    data: List[List[str]]
    title: Optional[str] = None
    location_in_document: Optional[str] = None
    table_hash: Optional[str] = None


@dataclass
class GeoCoordinate:
    """Represents a geological coordinate with metadata."""
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    location_name: Optional[str] = None
    confidence: float = 0.95


@dataclass
class AssayResult:
    """Represents a geochemical assay result."""
    sample_id: str
    elements: Dict[str, float]  # Element -> value (ppm or %)
    sample_type: str  # "rock", "soil", "sediment", "drill"
    depth: Optional[float] = None
    location: Optional[GeoCoordinate] = None
    date_analyzed: Optional[str] = None


# ============================================================================
# DOCUMENT PARSER INTERFACE
# ============================================================================

class DocumentParser(ABC):
    """Abstract base for document parsers."""
    
    @abstractmethod
    async def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse document and return text, metadata, tables, images."""
        pass
    
    @abstractmethod
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract document metadata."""
        pass


# ============================================================================
# PDF PARSER
# ============================================================================

class PDFParser(DocumentParser):
    """Parse PDF documents."""
    
    async def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF and extract content."""
        try:
            doc = fitz.open(file_path)
            
            full_text = []
            metadata = await self.extract_metadata(file_path)
            tables = []
            coordinates = []
            images = []
            
            for page_num, page in enumerate(doc):
                # Extract text
                text = page.get_text()
                full_text.append({
                    "page": page_num + 1,
                    "text": text,
                })
                
                # Extract tables (advanced table detection)
                page_tables = await self._extract_tables(page, page_num + 1)
                tables.extend(page_tables)
                
                # Extract images
                for img_index, img in enumerate(page.get_images()):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    img_path = f"/tmp/page_{page_num}_img_{img_index}.png"
                    pix.save(img_path)
                    
                    images.append({
                        "page": page_num + 1,
                        "image_path": img_path,
                        "image_index": img_index,
                    })
                
                # Extract coordinates from text
                page_coords = await self._extract_coordinates(text, page_num + 1)
                coordinates.extend(page_coords)
            
            doc.close()
            
            return {
                "format": DocumentFormat.PDF,
                "full_text": "\n".join([chunk["text"] for chunk in full_text]),
                "text_by_page": full_text,
                "metadata": metadata,
                "tables": tables,
                "coordinates": coordinates,
                "images": images,
                "page_count": len(doc),
            }
        
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            raise
    
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract PDF metadata."""
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            doc.close()
            
            return {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
            }
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {}
    
    async def _extract_tables(self, page, page_num: int) -> List[ExtractedTable]:
        """Extract tables from page using pymupdf-tables."""
        try:
            # For production, use pymupdf-tables or camelot
            # This is a simplified extraction
            tables = []
            
            # Simple approach: find table-like structures
            # In production, use proper table detection library
            text = page.get_text()
            lines = text.split("\n")
            
            potential_tables = []
            current_table = []
            
            for line in lines:
                if "|" in line or "\t" in line:
                    # Potential table row
                    if "|" in line:
                        row = [cell.strip() for cell in line.split("|")]
                    else:
                        row = [cell.strip() for cell in line.split("\t")]
                    
                    current_table.append(row)
                else:
                    if current_table and len(current_table) > 2:
                        potential_tables.append(current_table)
                    current_table = []
            
            for table_data in potential_tables:
                tables.append(ExtractedTable(
                    data=table_data,
                    location_in_document=f"Page {page_num}",
                ))
            
            return tables
        
        except Exception as e:
            logger.warning(f"Table extraction failed: {e}")
            return []
    
    async def _extract_coordinates(self, text: str, page_num: int) -> List[GeoCoordinate]:
        """Extract geographic coordinates from text."""
        import re
        
        coordinates = []
        
        # Regex patterns for coordinates
        # Format: 5.2345°N, 118.1234°E or 5°14'00.5"N, 118°07'24.3"E
        patterns = [
            r"(\d+\.?\d*)[°º]([NSEWnsew])\s*[,/]?\s*(\d+\.?\d*)[°º]([NSEWnsew])",  # Decimal degrees
            r"(\d+)[°º](\d+)['\'](\d+\.?\d*)[\"\'\']\s*([NSEWnsew])",  # DMS format
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    if len(match.groups()) == 4 and all(c in "NSEWnsew" for c in [match.group(2), match.group(4)]):
                        # Decimal format
                        lat = float(match.group(1))
                        lon = float(match.group(3))
                        
                        if match.group(2).upper() == "S":
                            lat = -lat
                        if match.group(4).upper() == "W":
                            lon = -lon
                        
                        coordinates.append(GeoCoordinate(
                            latitude=lat,
                            longitude=lon,
                            confidence=0.95,
                        ))
                except (ValueError, IndexError):
                    continue
        
        return coordinates


# ============================================================================
# OCR PARSER FOR SCANNED DOCUMENTS
# ============================================================================

class OCRParser(DocumentParser):
    """Parse scanned documents with OCR."""
    
    def __init__(self, languages: str = "eng"):
        self.languages = languages
    
    async def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse scanned document using OCR."""
        try:
            # Handle PDF with OCR
            if file_path.lower().endswith(".pdf"):
                return await self._ocr_pdf(file_path)
            
            # Handle image files
            else:
                return await self._ocr_image(file_path)
        
        except Exception as e:
            logger.error(f"OCR parsing failed: {e}")
            raise
    
    async def _ocr_pdf(self, file_path: str) -> Dict[str, Any]:
        """OCR a PDF document."""
        doc = fitz.open(file_path)
        
        full_text = []
        confidence_scores = []
        
        for page_num, page in enumerate(doc):
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_path = f"/tmp/ocr_page_{page_num}.png"
            pix.save(img_path)
            
            # Run OCR
            text, confidence = await self._ocr_image_file(img_path)
            
            full_text.append({
                "page": page_num + 1,
                "text": text,
                "confidence": confidence,
            })
            confidence_scores.append(confidence)
        
        doc.close()
        
        return {
            "format": DocumentFormat.PDF,
            "full_text": "\n".join([chunk["text"] for chunk in full_text]),
            "text_by_page": full_text,
            "metadata": await self.extract_metadata(file_path),
            "ocr_confidence": float(np.mean(confidence_scores)),
            "page_count": len(doc),
        }
    
    async def _ocr_image(self, file_path: str) -> Dict[str, Any]:
        """OCR an image file."""
        text, confidence = await self._ocr_image_file(file_path)
        
        return {
            "format": DocumentFormat.IMAGE,
            "full_text": text,
            "metadata": await self.extract_metadata(file_path),
            "ocr_confidence": confidence,
        }
    
    async def _ocr_image_file(self, image_path: str) -> Tuple[str, float]:
        """Run Tesseract OCR on image file."""
        try:
            # Run in thread pool
            loop = asyncio.get_event_loop()
            
            # Extract text
            text = await loop.run_in_executor(
                None,
                pytesseract.image_to_string,
                Image.open(image_path)
            )
            
            # Estimate confidence (simplified - in production use custom Tesseract config)
            # Extract confidence from Tesseract data
            data = await loop.run_in_executor(
                None,
                pytesseract.image_to_data,
                Image.open(image_path)
            )
            
            lines = data.split('\n')
            confidences = []
            for line in lines[1:]:
                parts = line.split('\t')
                if len(parts) >= 12:
                    try:
                        conf = float(parts[10])
                        if conf > 0:
                            confidences.append(conf)
                    except ValueError:
                        pass
            
            avg_confidence = float(np.mean(confidences)) if confidences else 0.0
            
            return text, avg_confidence / 100  # Convert to 0-1 scale
        
        except Exception as e:
            logger.error(f"OCR image processing failed: {e}")
            return "", 0.0
    
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract image metadata."""
        try:
            img = Image.open(file_path)
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
            }
        except Exception:
            return {}


# ============================================================================
# GEOLOGICAL METADATA EXTRACTOR
# ============================================================================

class GeologicalMetadataExtractor:
    """Extract geological-specific metadata from documents."""
    
    def __init__(self):
        # Mineral types reference
        self.mineral_types = {
            "ni", "cu", "au", "ag", "pb", "zn", "fe", "mo", "co", "as",
            "nickel", "copper", "gold", "silver", "lead", "zinc", "iron",
            "molybdenum", "cobalt", "arsenic", "sulfide", "oxide", "laterite"
        }
    
    async def extract_minerals(self, text: str) -> List[str]:
        """Extract mineral types mentioned in text."""
        found_minerals = set()
        text_lower = text.lower()
        
        for mineral in self.mineral_types:
            if mineral in text_lower:
                found_minerals.add(mineral)
        
        return list(found_minerals)
    
    async def extract_assay_data(self, text: str) -> List[AssayResult]:
        """Extract assay/geochemical data from text."""
        import re
        
        assays = []
        
        # Pattern: "Sample ID: XXX, Cu: 4.5%, Ni: 1.2%"
        sample_pattern = r"sample[_\s]?id[:\s]+([A-Z0-9\-_]+)"
        
        matches = re.finditer(sample_pattern, text, re.IGNORECASE)
        
        for match in matches:
            sample_id = match.group(1)
            
            # Extract elements after sample ID
            section_start = match.start()
            section_end = min(section_start + 500, len(text))
            section = text[section_start:section_end]
            
            elements = {}
            
            # Look for element values (Cu: 4.5%, Ni: 1.2%, etc.)
            element_pattern = r"([A-Z][a-z]?)[\s:]+(\d+\.?\d*)\s*(%|ppm)"
            element_matches = re.finditer(element_pattern, section)
            
            for elem_match in element_matches:
                element = elem_match.group(1)
                value = float(elem_match.group(2))
                unit = elem_match.group(3)
                
                # Normalize to percentage
                if unit == "ppm":
                    value = value / 10000  # 10000 ppm = 1%
                
                elements[element] = value
            
            if elements:
                assays.append(AssayResult(
                    sample_id=sample_id,
                    elements=elements,
                    sample_type="unknown",
                ))
        
        return assays
    
    async def extract_depth_range(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract depth range from text."""
        import re
        
        # Pattern: "0-50m", "50 to 100 metres", "from 0m to 200m"
        patterns = [
            r"(\d+\.?\d*)\s*[m](?:eters?)?\s*[-–to]\s*(\d+\.?\d*)\s*[m](?:eters?)?",
            r"from\s+(\d+\.?\d*)\s*[m](?:eters?)?\s+to\s+(\d+\.?\d*)\s*[m](?:eters?)?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    min_depth = float(match.group(1))
                    max_depth = float(match.group(2))
                    return (min_depth, max_depth)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    async def extract_location(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract location information."""
        import re
        
        location_data = {}
        
        # Extract coordinates
        coord_pattern = r"(\d+\.?\d*)[°º]\s*([NSEWnsew])\s*[,/]?\s*(\d+\.?\d*)[°º]\s*([NSEWnsew])"
        match = re.search(coord_pattern, text)
        
        if match:
            lat = float(match.group(1))
            lon = float(match.group(3))
            
            if match.group(2).upper() == "S":
                lat = -lat
            if match.group(4).upper() == "W":
                lon = -lon
            
            location_data["latitude"] = lat
            location_data["longitude"] = lon
        
        # Extract location name
        location_names = {
            "sumayau", "daling", "lundus", "bubu", "sabah", "malayisa",
            "kalimantan", "sulawesi", "borneo"
        }
        text_lower = text.lower()
        for loc_name in location_names:
            if loc_name in text_lower:
                location_data["location_name"] = loc_name
                break
        
        return location_data if location_data else None


# ============================================================================
# DOCUMENT PROCESSOR PIPELINE
# ============================================================================

class DocumentProcessor:
    """Main document processing pipeline."""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.ocr_parser = OCRParser()
        self.geo_extractor = GeologicalMetadataExtractor()
    
    async def process_document(
        self,
        file_path: str,
        document_id: str,
        document_name: str,
        use_ocr: bool = False,
    ) -> Dict[str, Any]:
        """Process a document end-to-end."""
        
        logger.info(f"Processing document: {document_name}")
        
        # Determine format
        file_ext = Path(file_path).suffix.lower()
        
        # Parse document
        if use_ocr or file_ext in [".png", ".jpg", ".jpeg"]:
            parsed = await self.ocr_parser.parse(file_path)
        elif file_ext == ".pdf":
            parsed = await self.pdf_parser.parse(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
        
        full_text = parsed.get("full_text", "")
        
        # Extract geological metadata
        minerals = await self.geo_extractor.extract_minerals(full_text)
        assays = await self.geo_extractor.extract_assay_data(full_text)
        depth_range = await self.geo_extractor.extract_depth_range(full_text)
        location = await self.geo_extractor.extract_location(full_text)
        
        # Infer document type
        document_type = self._infer_document_type(full_text, file_ext)
        
        return {
            "document_id": document_id,
            "document_name": document_name,
            "full_text": full_text,
            "document_type": document_type,
            "metadata": {
                "file_format": file_ext,
                "minerals": minerals,
                "depth_range": depth_range,
                "location": location,
                "assay_count": len(assays),
                "table_count": len(parsed.get("tables", [])),
                "image_count": len(parsed.get("images", [])),
                "ocr_confidence": parsed.get("ocr_confidence"),
            },
            "parsed_content": parsed,
            "assay_data": assays,
        }
    
    @staticmethod
    def _infer_document_type(text: str, file_ext: str) -> str:
        """Infer document type from content."""
        text_lower = text.lower()
        
        if "drill" in text_lower or "borehole" in text_lower or "hole" in text_lower:
            return "drill_log"
        elif "survey" in text_lower or "geological" in text_lower:
            return "survey"
        elif "map" in text_lower or "geology map" in text_lower:
            return "map"
        elif "assay" in text_lower or "geochemical" in text_lower:
            return "assay"
        elif "report" in text_lower or "exploration" in text_lower:
            return "report"
        else:
            return "document"


# ============================================================================
# BATCH DOCUMENT PROCESSOR
# ============================================================================

class BatchDocumentProcessor:
    """Process multiple documents in parallel."""
    
    def __init__(self, max_concurrent: int = 5):
        self.processor = DocumentProcessor()
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(
        self,
        documents: List[Tuple[str, str, str]],  # (file_path, doc_id, doc_name)
        use_ocr: bool = False,
    ) -> List[Dict[str, Any]]:
        """Process multiple documents concurrently."""
        
        async def process_with_semaphore(file_path, doc_id, doc_name):
            async with self.semaphore:
                try:
                    return await self.processor.process_document(
                        file_path,
                        doc_id,
                        doc_name,
                        use_ocr=use_ocr,
                    )
                except Exception as e:
                    logger.error(f"Failed to process {doc_name}: {e}")
                    return None
        
        tasks = [
            process_with_semaphore(file_path, doc_id, doc_name)
            for file_path, doc_id, doc_name in documents
        ]
        
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage."""
    processor = DocumentProcessor()
    
    # Example: Process a sample geological report
    sample_pdf_path = "/tmp/sample_drill_log.pdf"
    
    # Create a dummy PDF for testing (in production, use real documents)
    # For now, just show the structure
    
    result = {
        "document_id": "SYD25-0001",
        "document_name": "Sumayau Drill Log SYD25-0001",
        "full_text": """
        SUMAYAU PROJECT - DRILL LOG SYD25-0001
        Location: 5.2345°N, 118.1234°E
        
        0-50m: Laterite, brown-red, high nickel (2.1% Ni)
        50-100m: Transition zone, copper mineralization (1.8% Cu, 0.8% Ni)
        100-150m: Primary massive sulfide, black (54.0% Cu, 2.3% Ni)
        150-200m: Disseminated mineralization (1.2% Cu, 0.3% Ni)
        """,
        "document_type": "drill_log",
        "metadata": {
            "minerals": ["ni", "cu", "nickel", "copper"],
            "depth_range": (0.0, 200.0),
            "location": {"latitude": 5.2345, "longitude": 118.1234},
        }
    }
    
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
