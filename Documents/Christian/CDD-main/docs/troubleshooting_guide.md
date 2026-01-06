# Troubleshooting Guide - PDF to Grouped Tree Structure Extractor

## Table of Contents
1. [Connection Issues](#connection-issues)
2. [PDF Extraction Problems](#pdf-extraction-problems)
3. [AI Processing Errors](#ai-processing-errors)
4. [Data Quality Issues](#data-quality-issues)
5. [Performance Problems](#performance-problems)
6. [Export Issues](#export-issues)

## Connection Issues

### Problem: "Missing required SAP credentials" Error

**Symptoms:**
- Error message: "Missing required SAP credentials: SAP_CLIENT_ID, SAP_CLIENT_SECRET, SAP_AUTH_URL"
- Red warning in sidebar

**Diagnosis:**
1. Check if `.env` file exists in project root
2. Verify file contains required variables
3. Check for typos in variable names

**Solutions:**

**Solution 1: Create/Update .env File**
```bash
# Create .env file in project root with:
AICORE_CLIENT_ID=your_client_id
AICORE_CLIENT_SECRET=your_client_secret
AICORE_AUTH_URL=your_auth_url
AICORE_BASE_URL=your_base_url
AICORE_RESOURCE_GROUP=default
```

**Solution 2: Verify File Encoding**
- Ensure `.env` file is UTF-8 encoded (no BOM)
- Check for special characters in values
- Use quotes around values with special characters if needed

**Solution 3: Restart Application**
- After updating `.env`, restart Streamlit
- Credentials are loaded at startup

**Prevention:**
- Keep `.env` file in project root
- Never commit `.env` to version control
- Use `.env.example` as template

---

### Problem: Connection Test Fails

**Symptoms:**
- "Test Connection" button shows error
- Red error message in sidebar
- No deployment information shown

**Diagnosis:**
1. Test connection manually
2. Check network connectivity
3. Verify credentials are correct
4. Check SAP Cloud SDK for AI service status

**Solutions:**

**Solution 1: Verify Credentials**
```python
# Test credentials manually
from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv('AICORE_CLIENT_ID'))
print(os.getenv('AICORE_CLIENT_SECRET'))
print(os.getenv('AICORE_AUTH_URL'))
```

**Solution 2: Check Network Connectivity**
- Verify internet connection
- Check firewall settings
- Test SAP Cloud SDK for AI endpoint accessibility
- Verify VPN connection if required

**Solution 3: Validate Resource Group**
- Ensure `AICORE_RESOURCE_GROUP` matches your setup
- Default is "default"
- Check with SAP administrator if unsure

**Solution 4: Check Model Deployments**
- Verify deployments exist in your resource group
- Check if preferred models (gpt-4o, etc.) are available
- Contact SAP administrator if no deployments found

**Error Messages:**

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Authentication failed" | Invalid credentials | Verify CLIENT_ID and CLIENT_SECRET |
| "Connection timeout" | Network issue | Check connectivity, try again |
| "No deployments found" | No models deployed | Contact administrator |
| "Resource group not found" | Wrong resource group | Verify AICORE_RESOURCE_GROUP |

---

## PDF Extraction Problems

### Problem: No Tables Found

**Symptoms:**
- Error: "No tables found in the PDF"
- Extraction summary shows 0 tables
- Processing stops after Step 1

**Diagnosis:**
1. Check if PDF actually contains tables
2. Verify table structure (with/without borders)
3. Check page selection
4. Verify PDF is not just images

**Solutions:**

**Solution 1: Try Different Flavor**
- Switch from Lattice to Stream (or vice versa)
- Lattice: For tables with clear borders
- Stream: For tables without borders

**Solution 2: Check Page Selection**
- Verify pages contain tables
- Try `all` pages first
- Then narrow down to specific pages

**Solution 3: Verify PDF Quality**
- Ensure PDF contains actual text (not scanned images)
- Check if text is selectable
- Verify tables are properly formatted
- Try OCR if PDF is scanned

**Solution 4: Check PDF Structure**
- Open PDF in PDF viewer
- Verify tables are actual tables (not text boxes)
- Check for merged cells (may cause issues)
- Ensure consistent column structure

**Debug Steps:**
1. Open PDF in PDF viewer
2. Try selecting table text
3. Check table borders/formatting
4. Note page numbers with tables
5. Try extraction with noted pages

---

### Problem: Incorrect Table Extraction

**Symptoms:**
- Tables extracted but data is wrong
- Missing rows or columns
- Merged cells not handled correctly
- Extra data included

**Diagnosis:**
1. Compare extracted tables with source PDF
2. Check table structure complexity
3. Verify extraction settings

**Solutions:**

**Solution 1: Adjust Flavor**
- Complex tables: Try Stream mode
- Simple tables: Use Lattice mode
- Mixed structure: Process in sections

**Solution 2: Process Pages Separately**
- Extract problematic pages separately
- Combine results manually if needed
- Use page ranges for better control

**Solution 3: Pre-process PDF**
- Clean up PDF before processing
- Remove unnecessary elements
- Ensure consistent formatting
- Split complex tables if possible

**Solution 4: Manual Review**
- Review extraction summary
- Check each table individually
- Verify row/column counts match
- Re-extract if needed

---

### Problem: Extraction is Slow

**Symptoms:**
- Long wait times during extraction
- Progress spinner runs for minutes
- Application appears frozen

**Diagnosis:**
1. Check PDF size and complexity
2. Verify number of pages being processed
3. Check system resources

**Solutions:**

**Solution 1: Reduce Page Count**
- Process specific pages instead of `all`
- Use page ranges: `1-5` instead of entire document
- Process in batches

**Solution 2: Optimize PDF**
- Remove unnecessary pages
- Reduce PDF file size if possible
- Ensure tables are on relevant pages only

**Solution 3: Check System Resources**
- Close other applications
- Ensure sufficient memory available
- Check CPU usage
- Wait for current process to complete

---

## AI Processing Errors

### Problem: AI Structuring Fails

**Symptoms:**
- Error: "Failed to parse JSON response"
- Error: "SAP Cloud SDK for AI error"
- Processing stops at Step 2

**Diagnosis:**
1. Check SAP Cloud SDK for AI connection
2. Verify model deployment availability
3. Review error message details
4. Check data size being processed

**Solutions:**

**Solution 1: Check Connection**
- Test SAP Cloud SDK for AI connection
- Verify credentials are correct
- Ensure service is accessible
- Check for service outages

**Solution 2: Verify Model Availability**
- Check if preferred models are deployed
- Verify deployment IDs are correct
- Contact administrator if models unavailable
- Try with different model if available

**Solution 3: Reduce Data Size**
- Process fewer tables at once
- Extract from fewer pages
- Split large tables if possible
- Process in smaller batches

**Solution 4: Check Error Details**
- Expand error message in UI
- Review traceback information
- Check JSON parsing errors
- Look for timeout messages

**Common Error Messages:**

| Error | Cause | Solution |
|-------|-------|----------|
| "No suitable model found" | No deployments available | Check deployments, contact admin |
| "JSON decode error" | Invalid AI response | Retry, check data quality |
| "Timeout" | Processing too slow | Reduce data size, retry |
| "Authentication failed" | Credential issue | Verify credentials |

---

### Problem: Incomplete AI Mapping

**Symptoms:**
- Some columns are empty
- Data not mapped correctly
- Missing rows in output
- Incorrect data types

**Diagnosis:**
1. Review source table structure
2. Check AI response quality
3. Verify 29-column mapping
4. Compare with source PDF

**Solutions:**

**Solution 1: Review Source Data**
- Check if source tables have all required data
- Verify column headers are clear
- Ensure consistent data format
- Check for missing values in source

**Solution 2: Improve Table Quality**
- Ensure clear table structure
- Use consistent formatting
- Include column headers
- Avoid merged cells

**Solution 3: Retry Processing**
- Sometimes AI needs retry
- Process again with same settings
- Check if results improve
- Try different pages if issue persists

**Solution 4: Manual Correction**
- Export to CSV
- Manually fill missing data
- Use spreadsheet application
- Re-import if needed

---

### Problem: AI Timeout

**Symptoms:**
- Processing stops mid-way
- Error: "Request timeout"
- No response from AI service

**Diagnosis:**
1. Check network connectivity
2. Verify service status
3. Check data size
4. Review timeout settings

**Solutions:**

**Solution 1: Reduce Data Size**
- Process fewer pages
- Extract smaller tables
- Split large datasets
- Process incrementally

**Solution 2: Check Network**
- Verify stable internet connection
- Check for network interruptions
- Try again after network stabilizes
- Use wired connection if possible

**Solution 3: Retry**
- Wait a few minutes
- Try processing again
- Service may have been temporarily unavailable
- Check service status page

---

## Data Quality Issues

### Problem: Missing Data in Output

**Symptoms:**
- Empty columns in 29-column table
- Missing rows compared to source
- Incomplete grouped tree

**Diagnosis:**
1. Compare output with source PDF
2. Check extraction summary
3. Verify AI mapping
4. Review filtering logic

**Solutions:**

**Solution 1: Check Source PDF**
- Verify source has complete data
- Check if data is in tables (not text)
- Ensure all pages were processed
- Verify page selection

**Solution 2: Review Extraction**
- Check extraction summary
- Verify all tables were extracted
- Check row/column counts
- Re-extract if counts don't match

**Solution 3: Check Filtering**
- Some rows may be filtered out
- Connectivity services are excluded
- Migration services are excluded
- Check if your data matches filter criteria

**Solution 4: Verify AI Mapping**
- Review 29-column table
- Check if data mapped to wrong columns
- Verify column names match
- Check for data type issues

---

### Problem: Incorrect Data Grouping

**Symptoms:**
- Solutions grouped incorrectly
- Tiers in wrong solutions
- Servers under wrong tiers
- Hierarchy doesn't match expectations

**Diagnosis:**
1. Review source PDF structure
2. Check service/system names
3. Verify grouping logic
4. Compare with expected structure

**Solutions:**

**Solution 1: Check Source Data**
- Verify service names are consistent
- Check system_name values
- Ensure tier_type is correct
- Review database values

**Solution 2: Review Grouping Logic**
- Grouping is by: Service → Tier → Server
- Check service column values
- Verify tier_type values (PROD/nonPROD)
- Review system_name grouping

**Solution 3: Manual Correction**
- Export to CSV
- Manually adjust grouping
- Use spreadsheet for reorganization
- Re-process if source can be fixed

---

### Problem: Data Type Issues

**Symptoms:**
- Numbers stored as text
- Dates in wrong format
- Boolean values incorrect
- Decimal precision lost

**Diagnosis:**
1. Check source PDF data types
2. Review AI mapping
3. Verify column definitions
4. Check export formats

**Solutions:**

**Solution 1: Source Data Format**
- Ensure source PDF has correct formats
- Numbers should be numeric
- Dates should be consistent
- Verify source formatting

**Solution 2: Post-Processing**
- Export to CSV
- Use spreadsheet to fix types
- Apply data type conversions
- Re-export in correct format

**Solution 3: Review Column Definitions**
- Check 29-column structure
- Verify expected data types
- Update source if needed
- Document type requirements

---

## Performance Problems

### Problem: Slow Processing

**Symptoms:**
- Long wait times
- Application appears frozen
- Timeout errors
- Browser becomes unresponsive

**Diagnosis:**
1. Check PDF size and complexity
2. Verify number of pages
3. Check network speed
4. Review system resources

**Solutions:**

**Solution 1: Optimize PDF Processing**
- Process specific pages only
- Use page ranges instead of `all`
- Split large documents
- Process in batches

**Solution 2: Improve Network**
- Use stable connection
- Avoid peak usage times
- Check bandwidth availability
- Use wired connection

**Solution 3: System Optimization**
- Close other applications
- Free up memory
- Check CPU usage
- Restart browser if needed

**Solution 4: Reduce Data Size**
- Extract fewer tables
- Process smaller sections
- Simplify table structure
- Remove unnecessary data

---

### Problem: Browser Crashes

**Symptoms:**
- Browser becomes unresponsive
- Tab crashes
- Memory errors
- Application freezes

**Diagnosis:**
1. Check browser memory usage
2. Verify PDF size
3. Check number of tabs open
4. Review browser version

**Solutions:**

**Solution 1: Browser Optimization**
- Close other tabs
- Clear browser cache
- Update browser
- Use Chrome/Firefox (recommended)

**Solution 2: Reduce Load**
- Process smaller PDFs
- Use page selection
- Process incrementally
- Avoid multiple simultaneous operations

**Solution 3: System Resources**
- Close other applications
- Free up RAM
- Check available disk space
- Restart computer if needed

---

## Export Issues

### Problem: Download Fails

**Symptoms:**
- Download button doesn't work
- File not downloaded
- Empty file downloaded
- Browser blocks download

**Diagnosis:**
1. Check browser download settings
2. Verify file generation
3. Check security settings
4. Review file permissions

**Solutions:**

**Solution 1: Browser Settings**
- Check download permissions
- Allow downloads from site
- Disable pop-up blocker
- Check download folder permissions

**Solution 2: Verify Processing**
- Ensure processing completed
- Check for errors
- Verify data exists
- Try processing again

**Solution 3: Alternative Export**
- Try different format (CSV/JSON/XML)
- Use browser's "Save As"
- Copy data manually if needed
- Check file size (should not be 0)

---

### Problem: Exported File is Empty

**Symptoms:**
- File downloads but is empty
- 0 bytes file size
- No data in exported file
- File opens but shows nothing

**Diagnosis:**
1. Check if processing completed
2. Verify data exists in UI
3. Check file generation
4. Review export logic

**Solutions:**

**Solution 1: Verify Data**
- Check 29-column table has data
- Verify processing completed successfully
- Check for errors during processing
- Ensure data is not filtered out

**Solution 2: Retry Export**
- Process PDF again
- Wait for complete processing
- Try exporting again
- Check different format

**Solution 3: Check Processing**
- Review extraction summary
- Verify AI structuring completed
- Check for warnings/errors
- Ensure all steps completed

---

### Problem: Wrong File Format

**Symptoms:**
- File extension doesn't match content
- File won't open in expected application
- Format appears corrupted
- Encoding issues

**Diagnosis:**
1. Check file extension
2. Verify content format
3. Check encoding
4. Review export code

**Solutions:**

**Solution 1: File Extension**
- CSV files should have `.csv` extension
- JSON files should have `.json` extension
- XML files should have `.xml` extension
- Rename if extension is wrong

**Solution 2: Content Verification**
- Open file in text editor
- Check file content format
- Verify encoding (UTF-8)
- Check for corruption

**Solution 3: Application Compatibility**
- Use appropriate application
- CSV: Excel, Google Sheets
- JSON: Text editor, JSON viewer
- XML: Text editor, XML viewer
- Verify application supports format

---

## Getting Additional Help

If you've tried the solutions above and still have issues:

1. **Document the Problem**
   - Note exact error messages
   - Screenshot the issue
   - Record steps to reproduce
   - Note what you've tried

2. **Check Logs**
   - Review browser console (F12)
   - Check application logs
   - Look for error messages
   - Note timestamps

3. **Contact Support**
   - Provide problem description
   - Include error messages
   - Attach screenshots
   - Share PDF sample (if possible)

4. **Review Documentation**
   - Check User Guide
   - Review FAQ
   - Consult Training Manual
   - Look for similar issues

---

## Prevention Tips

1. **Regular Testing**
   - Test with sample PDFs regularly
   - Verify connection before processing
   - Check output quality

2. **Data Preparation**
   - Prepare PDFs properly
   - Ensure consistent formatting
   - Verify table structure

3. **Backup and Version Control**
   - Keep original PDFs
   - Save exported outputs
   - Version your data

4. **Stay Updated**
   - Keep application updated
   - Check for new versions
   - Review release notes

