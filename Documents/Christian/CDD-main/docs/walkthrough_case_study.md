# User Walkthrough - Case Study: QT_real_sample.pdf

## Table of Contents
1. [Case Study Overview](#case-study-overview)
2. [Step-by-Step Walkthrough](#step-by-step-walkthrough)
3. [Expected Results](#expected-results)
4. [Validation Checklist](#validation-checklist)
5. [Lessons Learned](#lessons-learned)

## Case Study Overview

This walkthrough demonstrates the complete workflow of extracting and structuring data from a real-world PDF document: **QT_real_sample.pdf**. This case study will guide you through:

- PDF upload and configuration
- Table extraction process
- AI-powered data structuring
- Grouped tree transformation
- Result validation and export

### About QT_real_sample.pdf

This sample PDF contains:
- Multiple tables with infrastructure configuration data
- Various services and systems
- Hardware specifications
- Storage configurations
- Tier information (PROD/nonPROD)

**Learning Objectives:**
- Understand the complete extraction workflow
- Learn how to configure extraction settings
- See how AI maps data to 29-column structure
- Validate output quality
- Export results in multiple formats

## Step-by-Step Walkthrough

### Step 1: Preparation and Setup

**Before Starting:**

1. **Verify Credentials**
   - Ensure `.env` file contains SAP Cloud SDK for AI credentials
   - Test connection using sidebar "Test Connection" button
   - Verify you see: ✅ Connection successful!

2. **Locate Sample File**
   - File: `QT_real_sample.pdf`
   - Location: Project root directory
   - Size: Check file size (should be reasonable for processing)

3. **Prepare Your Workspace**
   - Open the application in your browser
   - Ensure sidebar is expanded
   - Clear any previous session data if needed

**Expected Setup Time:** 2-3 minutes

---

### Step 2: Upload QT_real_sample.pdf

**Action Steps:**

1. **Locate Upload Area**
   - Find the file uploader in the main area
   - Look for: "Upload a PDF file" with dashed border

2. **Upload the File**
   - Click the upload area
   - Navigate to project directory
   - Select `QT_real_sample.pdf`
   - Wait for upload confirmation

3. **Verify Upload**
   - Check for success message: ✅ File uploaded
   - Verify file name appears: `QT_real_sample.pdf`
   - Check file size is displayed

**What You Should See:**
```
📎 File uploaded: QT_real_sample.pdf (XXX bytes)
```

**Troubleshooting:**
- If upload fails, check file permissions
- Verify file is not corrupted
- Ensure file is actual PDF format

---

### Step 3: Configure Extraction Settings

**Action Steps:**

1. **Review Sidebar Settings**
   - Locate "📄 PDF Extraction" section in sidebar
   - Check current settings

2. **Configure Page Selection**
   - **Recommended**: Start with `all` pages
   - **Alternative**: If PDF is large, try `1-5` first
   - Enter in "Pages to extract" field: `all`

3. **Select Table Flavor**
   - **For QT_real_sample.pdf**: Start with `lattice`
   - This PDF likely has tables with borders
   - Select "lattice" from dropdown

**Configuration Summary:**
```
Pages to extract: all
Camelot Flavor: lattice
```

**Why These Settings?**
- `all` pages: Ensures we capture all data
- `lattice`: Best for tables with clear borders (typical in quote documents)

---

### Step 4: Extract Tables (Step 1/3)

**Action Steps:**

1. **Initiate Extraction**
   - Click **"🔄 Extract & Structure Data"** button
   - Wait for Step 1 to complete

2. **Monitor Progress**
   - Watch for: "📊 Step 1/2: Extracting tables from PDF using Camelot..."
   - Progress spinner will appear
   - Wait for completion (typically 10-30 seconds)

3. **Review Extraction Summary**
   - Look for success message: ✅ Extracted X table(s) from PDF
   - Expand "📋 Table Extraction Summary"
   - Review each table found

**Expected Results for QT_real_sample.pdf:**

```
✅ Extracted 3-5 table(s) from PDF (exact count depends on PDF structure)

Table Extraction Summary:
- Table 1 (Page 1): XX rows × YY columns
- Table 2 (Page 2): XX rows × YY columns
- Table 3 (Page 3): XX rows × YY columns
...
```

**What to Check:**
- ✅ Tables were found (count > 0)
- ✅ Row/column counts seem reasonable
- ✅ Pages match where tables should be
- ✅ No error messages

**Common Issues:**
- **No tables found**: Try switching to "stream" flavor
- **Wrong pages**: Adjust page selection
- **Missing tables**: Check if PDF has actual tables (not images)

---

### Step 5: Structure Data with AI (Step 2/3)

**Action Steps:**

1. **AI Processing Begins Automatically**
   - After table extraction, AI processing starts
   - Watch for: "🤖 Step 2/3: Structuring data to 29-column format using SAP Cloud SDK for AI..."

2. **Wait for Processing**
   - Processing typically takes 30-60 seconds
   - Progress spinner shows activity
   - Do not close browser during this step

3. **Review Results**
   - Look for success message: ✅ Structured X row(s) into 29-column format
   - Check for any warnings

**Expected Results:**

```
✅ Structured XX row(s) into 29-column format

AI Provider: SAP Cloud SDK for AI
Model: gpt-4o (or other available model)
Deployment ID: [shown in connection details]
```

**What Happens Behind the Scenes:**
1. Extracted tables are sent to AI model
2. AI analyzes table structure and content
3. Data is mapped to 29-column format
4. Related data is grouped intelligently
5. Structured JSON is returned

**What to Check:**
- ✅ Processing completed without errors
- ✅ Row count matches expectations
- ✅ Success message appears
- ✅ Data appears in main area

**Common Issues:**
- **Timeout**: Try processing fewer pages
- **Mapping errors**: Check source table structure
- **Connection issues**: Verify SAP Cloud SDK for AI connection

---

### Step 6: Generate Grouped Tree (Step 3/3)

**Action Steps:**

1. **Tree Generation**
   - Happens automatically after structuring
   - Watch for: "🌳 Step 3/3: Generating grouped tree structure..."
   - Processing is quick (few seconds)

2. **Review Tree Summary**
   - Look for success message with counts:
   ```
   ✅ Generated grouped tree: X Solution(s), Y Tier(s), Z Server(s)
   ```

**Expected Results for QT_real_sample.pdf:**

```
✅ Generated grouped tree: 
- 2-4 Solution(s) (depending on services in PDF)
- 4-8 Tier(s) (PROD and nonPROD tiers)
- 10-20 Server(s) (individual server instances)
```

**What Happens:**
- Flat 29-column data is transformed
- Data is grouped by Service (Solution)
- Then by Tier Type (PROD/nonPROD)
- Finally by Server with all 29 columns

---

### Step 7: Explore the 29-Column Table

**Action Steps:**

1. **Navigate to Main Table**
   - Default view is "📊 29-Column Table" tab
   - Table should be visible automatically

2. **Review Data Structure**
   - Scroll through the table
   - Check all 29 columns are present
   - Verify data types are correct

3. **Validate Data Quality**
   - Check system names are populated
   - Verify hardware specs (RAM, CPU, SAPs)
   - Check storage information
   - Review tier types (PROD/nonPROD)

**Expected Columns (29 total):**
```
amount, system_name, service, database, tiername, tier_type,
system_id, ram_gib, cpus_physvirt, saps,
no_of_add_hana_nodes, no_of_standby_nodes, tenant__user_data_size,
amount_storage_1_gb, iops1, through_put1,
amount_storage_2_gb, iops2, through_put2,
storage_information_1, backup_class, os, sla, dr,
add_hw_for_dr, pacemaker_included, add_requirements, phase, server
```

**What to Look For:**
- ✅ All rows have data (not all empty)
- ✅ System names match source PDF
- ✅ Hardware specs are numeric values
- ✅ Tier types are PROD or nonPROD
- ✅ Services are correctly identified

**Data Quality Checks:**
- Compare with source PDF
- Verify row count matches expectations
- Check for any obvious mapping errors
- Ensure connectivity services are filtered out

---

### Step 8: Explore Raw XML (Step 1 Output)

**Action Steps:**

1. **Navigate to Raw XML Tab**
   - Click "📄 Raw XML (Step 1)" tab
   - Review XML structure

2. **Understand Structure**
   - Notice flat structure (all rows at same level)
   - Each `<row>` contains all 29 columns
   - Rows are numbered sequentially

**Expected Structure:**
```xml
<document>
  <row id="1">
    <amount>...</amount>
    <system_name>...</system_name>
    <service>...</service>
    <!-- ... all 29 columns ... -->
  </row>
  <row id="2">
    <!-- ... -->
  </row>
</document>
```

**What to Check:**
- ✅ XML is well-formed
- ✅ All rows have all 29 columns
- ✅ Data matches 29-column table view
- ✅ No missing or corrupted data

**Use Cases:**
- Flat data export
- Programmatic processing
- Comparison with other versions
- Validation workflows

---

### Step 9: Explore Grouped Tree Structure (Step 2 Output)

**Action Steps:**

1. **Navigate to Grouped Tree Tab**
   - Click "🌳 Grouped Tree (Step 2)" tab
   - Review tree summary metrics

2. **Explore Hierarchy**
   - Expand Solutions to see structure
   - Expand Tiers within Solutions
   - Expand Servers within Tiers

3. **Drill Down to Server Details**
   - Click on a Server expander
   - Review all 29 columns displayed
   - Check table view for easy comparison

**Expected Structure:**
```
Configuration
└── Solutions
    └── Solution: "Service Name 1"
        └── Tiers
            └── Tier (PROD)
                └── Servers
                    └── Server (all 29 columns)
            └── Tier (nonPROD)
                └── Servers
                    └── Server (all 29 columns)
    └── Solution: "Service Name 2"
        └── ...
```

**What to Check:**
- ✅ Solutions are correctly grouped
- ✅ Tiers are properly organized (PROD/nonPROD)
- ✅ Servers contain all 29 columns
- ✅ Hierarchy matches source PDF structure

**Filtering Features:**
- Filter by Solution
- Filter by Tier Type
- Search by Server Name
- Download filtered results

---

### Step 10: Validate Data Completeness

**Action Steps:**

1. **Compare with Source PDF**
   - Open QT_real_sample.pdf in PDF viewer
   - Compare extracted data with source
   - Verify all important data is captured

2. **Check Summary Metrics**
   - Review Summary expander
   - Check Total Rows metric
   - Verify Rows with Data count
   - Ensure Total Columns = 29

3. **Validate Filtering**
   - Verify connectivity services are excluded
   - Check migration services are filtered
   - Ensure only relevant infrastructure data remains

**Validation Checklist:**
- [ ] Row count matches source PDF tables
- [ ] All systems from PDF are present
- [ ] Hardware specs match source
- [ ] Services are correctly identified
- [ ] Tier types are correct (PROD/nonPROD)
- [ ] Storage information is complete
- [ ] No critical data is missing
- [ ] Filtered services are excluded appropriately

---

### Step 11: Export Results

**Action Steps:**

1. **Export CSV**
   - Go to "📊 29-Column Table" tab
   - Click "⬇️ Download CSV" button
   - Save file: `QT_real_sample_29_column_output.csv`
   - Open in Excel to verify

2. **Export JSON**
   - Go to "📋 JSON View" tab
   - Review JSON structure
   - Download if download button available
   - Use for programmatic access

3. **Export Raw XML**
   - Go to "📄 Raw XML (Step 1)" tab
   - Click "⬇️ Download Raw XML" button
   - Save file: `QT_real_sample_raw.xml`

4. **Export Grouped Tree XML**
   - Go to "🌳 Grouped Tree (Step 2)" tab
   - Scroll to bottom
   - Click "⬇️ Download Grouped Tree XML" button
   - Save file: `QT_real_sample_grouped_tree.xml`

**Export Verification:**
- ✅ All files download successfully
- ✅ Files are not empty (check file size)
- ✅ CSV opens correctly in Excel
- ✅ XML files are well-formed
- ✅ Data matches UI display

---

## Expected Results

### Quantitative Results

Based on typical quote documents, you should expect:

- **Tables Extracted**: 3-5 tables
- **Rows Structured**: 15-30 rows (varies by PDF)
- **Solutions**: 2-4 unique services
- **Tiers**: 4-8 tiers (PROD + nonPROD)
- **Servers**: 10-20 server instances

### Qualitative Results

- **Data Quality**: High - all critical fields populated
- **Grouping Accuracy**: Correct - services and tiers properly organized
- **Completeness**: Complete - all relevant data extracted
- **Format Consistency**: Consistent - standardized 29-column format

### Output Files

1. **CSV File**: Ready for spreadsheet analysis
2. **JSON File**: Ready for programmatic processing
3. **Raw XML**: Flat structure for comparison
4. **Grouped Tree XML**: Hierarchical structure for validation

---

## Validation Checklist

Use this checklist to validate your results:

### Extraction Validation
- [ ] All expected tables were extracted
- [ ] Row counts match source PDF
- [ ] Column counts are reasonable
- [ ] No tables were missed

### Data Quality Validation
- [ ] All 29 columns are present
- [ ] System names are correct
- [ ] Hardware specs are numeric
- [ ] Tier types are PROD or nonPROD
- [ ] Services are correctly identified
- [ ] Storage information is complete

### Structure Validation
- [ ] Solutions are correctly grouped
- [ ] Tiers are properly organized
- [ ] Servers contain all 29 columns
- [ ] Hierarchy matches expectations
- [ ] Filtering works correctly

### Export Validation
- [ ] CSV file downloads and opens correctly
- [ ] JSON structure is valid
- [ ] XML files are well-formed
- [ ] All exports contain expected data
- [ ] File names are correct

---

## Lessons Learned

### Key Takeaways

1. **Start with Default Settings**
   - `all` pages and `lattice` flavor work for most documents
   - Adjust only if needed

2. **Validate Incrementally**
   - Check extraction first
   - Then verify AI structuring
   - Finally validate tree structure

3. **Use Multiple Views**
   - 29-column table for data review
   - Raw XML for flat structure
   - Grouped tree for hierarchy
   - Each view serves different purposes

4. **Export Everything**
   - Download all formats
   - Keep for comparison
   - Version your outputs

### Common Patterns Observed

- **Service Grouping**: Services are typically grouped correctly
- **Tier Organization**: PROD and nonPROD tiers are well-separated
- **Data Completeness**: Most fields are populated accurately
- **Filtering**: Connectivity services are properly excluded

### Best Practices Applied

- ✅ Verified connection before processing
- ✅ Used appropriate extraction settings
- ✅ Validated at each step
- ✅ Exported multiple formats
- ✅ Compared with source PDF

---

## Troubleshooting This Case Study

### If Tables Aren't Found

**Problem**: No tables extracted from QT_real_sample.pdf

**Solutions**:
1. Try "stream" flavor instead of "lattice"
2. Check if PDF has actual tables (not images)
3. Verify page selection includes correct pages
4. Check PDF file is not corrupted

### If AI Structuring Fails

**Problem**: Step 2 fails or returns incomplete data

**Solutions**:
1. Verify SAP Cloud SDK for AI connection
2. Check model deployment availability
3. Try processing fewer pages
4. Retry the operation

### If Data Doesn't Match Source

**Problem**: Extracted data doesn't match PDF content

**Solutions**:
1. Review extraction summary
2. Check if correct pages were processed
3. Verify table structure in source PDF
4. Try different flavor setting

### If Grouped Tree is Incorrect

**Problem**: Hierarchy doesn't match expectations

**Solutions**:
1. Review 29-column table first
2. Check service and system_name columns
3. Verify tier_type values
4. Check source PDF grouping logic

---

## Next Steps

After completing this walkthrough:

1. **Try Your Own PDFs**
   - Apply learned techniques
   - Experiment with different settings
   - Build confidence with the tool

2. **Explore Advanced Features**
   - Use filtering in grouped tree
   - Compare different contract versions
   - Export filtered datasets

3. **Review Documentation**
   - Read User Guide for details
   - Check Training Manual for exercises
   - Consult FAQ for common questions

4. **Practice Regularly**
   - Process different PDF types
   - Learn from each extraction
   - Build your expertise

---

## Summary

This walkthrough demonstrated:

✅ Complete workflow from PDF to grouped tree
✅ Proper configuration and settings
✅ Validation at each step
✅ Multiple export formats
✅ Best practices for data quality

**Key Success Factors:**
- Proper preparation and setup
- Appropriate configuration
- Incremental validation
- Multiple format exports
- Comparison with source

**You're now ready to:**
- Process your own PDFs
- Handle different document types
- Troubleshoot common issues
- Export and use results effectively

For more help, consult:
- **User Guide**: Comprehensive feature documentation
- **Training Manual**: Additional exercises
- **FAQ**: Common questions
- **Troubleshooting Guide**: Solutions to issues

