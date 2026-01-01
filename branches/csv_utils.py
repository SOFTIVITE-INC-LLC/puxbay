import csv
import io
import logging

logger = logging.getLogger(__name__)

class CSVParser:
    """
    Parses a .csv file and yields rows.
    Designed to allow drop-in replacement for XLSXParser in InventoryService.
    """
    
    def __init__(self, file_content):
        # file_content is bytes, we need to decode it
        self.file_content = file_content

    def parse(self):
        """Yields rows as lists of values."""
        try:
            # Decode bytes to string
            # Try utf-8 first, fallback to latin-1 (common in Excel CSVs)
            try:
                decoded_content = self.file_content.decode('utf-8')
            except UnicodeDecodeError:
                decoded_content = self.file_content.decode('latin-1')

            # Use StringIO to create a file-like object for the csv reader
            csv_file = io.StringIO(decoded_content)
            
            # Detect dialect (optional, but robust)
            try:
                dialect = csv.Sniffer().sniff(decoded_content[:1024])
            except csv.Error:
                # Fallback to excel dialect if sniffing fails (e.g. single column)
                dialect = 'excel'

            reader = csv.reader(csv_file, dialect=dialect)
            
            for row in reader:
                # Filter out empty strings from ends but keep internal structure consistent with XLSX parser
                # XLSXParser returns strings, so we ensure all are strings
                yield [str(cell).strip() for cell in row]
                
        except Exception as e:
            logger.error(f"CSV Parsing Error: {e}")
            raise e
