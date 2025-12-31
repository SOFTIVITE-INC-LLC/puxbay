import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
import datetime
import re
import logging

logger = logging.getLogger(__name__)

class XLSXGenerator:
    """Generates a simple .xlsx file without external dependencies."""
    
    def __init__(self):
        self.rows = []
        self.headers = []

    def writerow(self, row_data):
        """Add a row of data (list or tuple)."""
        self.rows.append(row_data)

    def generate(self):
        """Returns the bytes of the .xlsx file."""
        output = BytesIO()
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
            # [Content_Types].xml
            zf.writestr('[Content_Types].xml', self._content_types_xml())
            # _rels/.rels
            zf.writestr('_rels/.rels', self._rels_xml())
            # xl/workbook.xml
            zf.writestr('xl/workbook.xml', self._workbook_xml())
            # xl/_rels/workbook.xml.rels
            zf.writestr('xl/_rels/workbook.xml.rels', self._workbook_rels_xml())
            # xl/styles.xml (Minimal styles)
            zf.writestr('xl/styles.xml', self._styles_xml())
            # xl/worksheets/sheet1.xml
            zf.writestr('xl/worksheets/sheet1.xml', self._worksheet_xml())

        return output.getvalue()

    def _content_types_xml(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>"""

    def _rels_xml(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

    def _workbook_xml(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>
<sheet name="Sheet1" sheetId="1" r:id="rId1"/>
</sheets>
</workbook>"""

    def _workbook_rels_xml(self):
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    def _styles_xml(self):
         return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="1"><font><name val="Calibri"/><sz val="11"/><color theme="1"/><family val="2"/><scheme val="minor"/></font></fonts>
<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
</styleSheet>"""

    def _worksheet_xml(self):
        xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
        xml.append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">')
        xml.append('<sheetData>')
        
        for i, row in enumerate(self.rows):
            xml.append(f'<row r="{i+1}">')
            for j, val in enumerate(row):
                col_letter = self._get_col_letter(j + 1)
                cell_ref = f"{col_letter}{i+1}"
                
                if val is None:
                    continue
                    
                val_str = str(val)
                # Escape XML special characters
                val_str = val_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
                
                # Inline String (simplest way to write strings without sharedStrings table)
                xml.append(f'<c r="{cell_ref}" t="inlineStr"><is><t>{val_str}</t></is></c>')
            xml.append('</row>')
            
        xml.append('</sheetData>')
        xml.append('</worksheet>')
        return "".join(xml)

    def _get_col_letter(self, col_idx):
        """1 -> A, 2 -> B, ..., 26 -> Z, 27 -> AA"""
        string = ""
        while col_idx > 0:
            col_idx, remainder = divmod(col_idx - 1, 26)
            string = chr(65 + remainder) + string
        return string


class XLSXParser:
    """Parses a .xlsx file and yields rows."""
    
    def __init__(self, file_content):
        self.file_content = file_content
        self.shared_strings = []

    def parse(self):
        """Yields rows as lists of values."""
        zf = zipfile.ZipFile(BytesIO(self.file_content))
        
        # 1. Shared Strings
        if 'xl/sharedStrings.xml' in zf.namelist():
            self.shared_strings = self._parse_shared_strings(zf.read('xl/sharedStrings.xml'))
        
        # 2. Find any worksheet (robust to different names/cases)
        worksheet_path = None
        for name in zf.namelist():
            if name.lower().startswith('xl/worksheets/sheet') and name.lower().endswith('.xml'):
                worksheet_path = name
                break
        
        if not worksheet_path:
            # Fallback to any xml in worksheets
            worksheets = [f for f in zf.namelist() if f.lower().startswith('xl/worksheets/') and f.lower().endswith('.xml')]
            if worksheets: worksheet_path = worksheets[0]

        if worksheet_path:
            yield from self._parse_sheet(zf.read(worksheet_path))

    def _find_tag(self, element, tag_name, ns=None):
        """Finds a tag regardless of namespace prefix."""
        # 1. Try with provided namespace
        if ns:
            res = element.find(f'ns:{tag_name}', ns)
            if res is not None: return res
        
        # 2. Try absolute match (no namespace)
        res = element.find(tag_name)
        if res is not None: return res
        
        # 3. Try searching all children for tag name matching the end
        suffix = f"}}{tag_name}"
        for child in element:
            if child.tag == tag_name or child.tag.endswith(suffix):
                return child
        
        # 4. Deep search as last resort
        for child in element.iter():
            if child.tag == tag_name or child.tag.endswith(suffix):
                return child
        return None

    def _findall_tags(self, element, tag_name, ns=None):
        """Finds all tags regardless of namespace prefix."""
        results = []
        if ns:
            results = element.findall(f'ns:{tag_name}', ns)
            if results: return results
            
        results = element.findall(tag_name)
        if results: return results
        
        suffix = f"}}{tag_name}"
        return [child for child in element.iter() if child.tag == tag_name or child.tag.endswith(suffix)]

    def _parse_shared_strings(self, xml_content):
        strings = []
        try:
            root = ET.fromstring(xml_content)
        except: return []

        ns_url = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        if root.tag.startswith('{'):
            ns_url = root.tag.split('}')[0].strip('{')
        ns = {'ns': ns_url}

        for si in self._findall_tags(root, 'si', ns):
            t_tags = self._findall_tags(si, 't', ns)
            text = "".join([t.text for t in t_tags if t.text is not None])
            strings.append(text)
        return strings

    def _parse_sheet(self, xml_content):
        try:
            root = ET.fromstring(xml_content)
        except: return

        ns_url = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        if root.tag.startswith('{'):
            ns_url = root.tag.split('}')[0].strip('{')
        ns = {'ns': ns_url}

        sheet_data = self._find_tag(root, 'sheetData', ns)
        if sheet_data is None: return

        for row in self._findall_tags(sheet_data, 'row', ns):
            parsed_row_data = {}
            max_col = 0
            cells = self._findall_tags(row, 'c', ns)

            for cell in cells:
                r_attr = cell.get('r')
                if r_attr:
                    col_str = "".join([c for c in r_attr if c.isalpha()])
                    col_idx = self._col_str_to_index(col_str)
                    max_col = max(max_col, col_idx)
                else:
                    col_idx = len(parsed_row_data) + 1
                    max_col = max(max_col, col_idx)

                t_attr = cell.get('t')
                v_tag = self._find_tag(cell, 'v', ns)
                val = v_tag.text if v_tag is not None else ""
                
                final_val = ""
                if t_attr == 's' and val != "":
                    try:
                        idx = int(val)
                        if 0 <= idx < len(self.shared_strings):
                            final_val = self.shared_strings[idx]
                    except: pass
                elif t_attr == 'inlineStr' or self._find_tag(cell, 'is', ns) is not None:
                    is_tag = self._find_tag(cell, 'is', ns)
                    t_tag = self._find_tag(is_tag, 't', ns) if is_tag is not None else None
                    if t_tag is not None:
                        final_val = t_tag.text or ""
                else:
                    final_val = val
                
                parsed_row_data[col_idx] = final_val

            row_list = []
            for i in range(1, max(max_col, 20) + 1):
                row_list.append(str(parsed_row_data.get(i, "")).strip())
            
            yield row_list

    def _col_str_to_index(self, col_str):
        """Convert column string (A, B, AA) to 1-based index."""
        num = 0
        for c in col_str:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        return num
