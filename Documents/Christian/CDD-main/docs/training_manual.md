# Training Manual - PDF to Grouped Tree Structure Extractor

## Table of Contents
1. [Training Overview](#training-overview)
2. [Module 1: Introduction and Setup](#module-1-introduction-and-setup)
3. [Module 2: Basic Workflow](#module-2-basic-workflow)
4. [Module 3: Advanced Features](#module-3-advanced-features)
5. [Module 4: Data Validation](#module-4-data-validation)
6. [Module 5: Best Practices](#module-5-best-practices)
7. [Hands-On Exercises](#hands-on-exercises)

## Training Overview

This training manual provides step-by-step instructions for using the PDF to Grouped Tree Structure Extractor. Each module builds upon the previous one, taking you from basic usage to advanced techniques.

### Training Objectives

By the end of this training, you will be able to:
- ✅ Set up and configure the application
- ✅ Extract tables from PDF documents
- ✅ Structure data using AI-powered mapping
- ✅ Navigate and understand the grouped tree structure
- ✅ Export data in multiple formats
- ✅ Validate and troubleshoot data extraction

### Prerequisites

- Basic understanding of PDF documents
- Familiarity with data structures (tables, columns)
- Access to SAP Cloud SDK for AI credentials
- Sample PDF documents for practice

## Module 1: Introduction and Setup

### Lesson 1.1: Understanding the Application

**What is this tool?**
- A web-based application for extracting structured data from PDFs
- Uses AI to map data to standardized formats
- Creates hierarchical tree structures for validation

**Key Components:**
1. **PDF Upload**: Interface for selecting PDF files
2. **Table Extraction**: Camelot library for table detection
3. **AI Structuring**: SAP Cloud SDK for AI for data mapping
4. **Tree Transformation**: Converts flat data to hierarchical structure
5. **Export Options**: Multiple format downloads

### Lesson 1.2: Initial Setup

**Step 1: Verify Credentials**

1. Open the application sidebar
2. Locate "SAP Cloud SDK for AI" section
3. Click "Test Connection" button
4. Verify you see: ✅ Connection successful!

**Expected Result:**
- Green success message
- Connection details showing deployment ID and model name

**Troubleshooting:**
- If connection fails, check `.env` file credentials
- Verify `AICORE_CLIENT_ID`, `AICORE_CLIENT_SECRET`, `AICORE_AUTH_URL` are set
- Check network connectivity

**Step 2: Prepare Your PDF**

1. Locate your PDF document
2. Verify it contains tables with data
3. Note which pages contain relevant tables
4. Check table structure (with/without borders)

### Lesson 1.3: Understanding the Interface

**Main Components:**

1. **Header**: Application title and description
2. **Sidebar**: Configuration and settings
   - SAP Connection Test
   - Credential Status
   - PDF Extraction Settings
3. **Main Area**: File upload and results display
4. **Tabs**: Different views of extracted data

**Navigation:**
- Use sidebar for configuration
- Main area for file operations
- Tabs for viewing different data formats

## Module 2: Basic Workflow

### Lesson 2.1: Uploading a PDF

**Exercise 2.1.1: Upload Your First PDF**

1. Click the upload area (dashed box)
2. Select a PDF file from your computer
3. Wait for file validation
4. Verify file info appears: ✅ File uploaded

**What to Look For:**
- File name displayed
- File size shown
- Upload confirmation message

**Common Issues:**
- File too large: Check file size limits
- Wrong format: Ensure file is PDF format
- Upload fails: Check file permissions

### Lesson 2.2: Configuring Extraction Settings

**Exercise 2.2.1: Configure Page Selection**

1. In sidebar, find "PDF Extraction" section
2. Locate "Pages to extract" field
3. Enter page selection:
   - `all` for entire document
   - `1-5` for pages 1 through 5
   - `1,3,5` for specific pages
4. Click outside field to save

**Exercise 2.2.2: Select Table Flavor**

1. Find "Camelot Flavor" dropdown
2. Select appropriate option:
   - **Lattice**: For tables with clear borders/lines
   - **Stream**: For tables without visible borders
3. If unsure, start with "Lattice"

**Decision Guide:**
- Tables with lines → Lattice
- Tables without lines → Stream
- Mixed document → Try Lattice first

### Lesson 2.3: Extracting Tables

**Exercise 2.3.1: Run Table Extraction**

1. Verify PDF is uploaded
2. Check extraction settings
3. Click **"🔄 Extract & Structure Data"** button
4. Wait for Step 1 to complete

**What Happens:**
- Step 1/2: Extracting tables from PDF using Camelot...
- Progress spinner appears
- Success message: ✅ Extracted X table(s) from PDF

**Exercise 2.3.2: Review Extraction Summary**

1. Expand "📋 Table Extraction Summary"
2. Review each table:
   - Table number
   - Page number
   - Row and column counts
3. Verify tables match expectations

**Expected Output:**
```
Table 1 (Page 1): 25 rows × 8 columns
Table 2 (Page 2): 15 rows × 6 columns
```

### Lesson 2.4: Structuring Data with AI

**Exercise 2.4.1: AI Processing**

1. After table extraction, AI processing starts automatically
2. Watch for: "Step 2/3: Structuring data..."
3. Wait for completion (may take 30-60 seconds)

**What Happens:**
- AI model analyzes extracted tables
- Maps data to 29-column structure
- Groups related data
- Returns structured JSON

**Exercise 2.4.2: Review Structured Output**

1. Check success message: ✅ Structured X row(s)
2. Verify data appears in main area
3. Check for any warnings or errors

**Common Issues:**
- AI timeout: Check model availability
- Mapping errors: Review source table structure
- Missing data: Verify PDF table completeness

## Module 3: Advanced Features

### Lesson 3.1: Navigating the 29-Column Table

**Exercise 3.1.1: Explore the Main Table**

1. Go to "📊 29-Column Table" tab (default)
2. Scroll through the table
3. Use column headers to understand structure
4. Check row count matches expectations

**Table Features:**
- Sortable columns
- Scrollable rows
- Full-width display
- Row highlighting on hover

**Exercise 3.1.2: Filter and Search**

1. Use browser search (Ctrl+F) to find specific values
2. Scroll to locate specific systems or servers
3. Note column order and data types

### Lesson 3.2: Understanding Raw XML (Step 1)

**Exercise 3.2.1: View Raw XML**

1. Click "📄 Raw XML (Step 1)" tab
2. Review XML structure
3. Notice flat structure (all rows at same level)
4. Each `<row>` contains all 29 columns

**XML Structure:**
```xml
<document>
  <row id="1">
    <amount>...</amount>
    <system_name>...</system_name>
    ...
  </row>
  <row id="2">...</row>
</document>
```

**Exercise 3.2.2: Download Raw XML**

1. Scroll to bottom of Raw XML tab
2. Click "⬇️ Download Raw XML" button
3. Save file to your computer
4. Open in text editor to inspect

### Lesson 3.3: Exploring Grouped Tree Structure (Step 2)

**Exercise 3.3.1: Navigate the Tree**

1. Click "🌳 Grouped Tree (Step 2)" tab
2. Review tree summary:
   - Number of Solutions
   - Number of Tiers
   - Number of Servers
3. Expand Solutions to see hierarchy

**Tree Structure:**
```
Configuration
└── Solutions
    └── Solution: "Service Name"
        └── Tiers
            └── Tier (PROD/nonPROD)
                └── Servers
                    └── Server (all 29 columns)
```

**Exercise 3.3.2: Drill Down to Server Details**

1. Expand a Solution
2. Expand a Tier within that Solution
3. Expand a Server within that Tier
4. Review all 29 columns displayed

**What You'll See:**
- Solution name
- Tier type (PROD/nonPROD)
- Database type
- All 29 columns with values
- Table view for easy comparison

**Exercise 3.3.3: Use Filtering**

1. Scroll to "Complete Server Comparison Table"
2. Use "Filter by Solution" dropdown
3. Use "Filter by Tier Type" dropdown
4. Use "Search Server Name" field
5. Observe filtered results update

### Lesson 3.4: Export Options

**Exercise 3.4.1: Export CSV**

1. Go to "📊 29-Column Table" tab
2. Click "⬇️ Download CSV" button
3. Open in Excel or spreadsheet application
4. Verify all columns and data present

**Exercise 3.4.2: Export JSON**

1. Go to "📋 JSON View" tab
2. Review JSON structure
3. Click download button (if available)
4. Use for programmatic access

**Exercise 3.4.3: Export XML**

1. Go to "🌳 Grouped Tree" tab
2. Scroll to bottom
3. Click "⬇️ Download Grouped Tree XML"
4. Use for validation workflows

## Module 4: Data Validation

### Lesson 4.1: Validating Extraction Quality

**Exercise 4.1.1: Compare Source and Output**

1. Open source PDF
2. Open extracted table view
3. Compare row counts
4. Verify data matches

**Checklist:**
- ✅ Row count matches
- ✅ Column data matches
- ✅ No missing critical fields
- ✅ Data types are correct

**Exercise 4.1.2: Verify AI Mapping**

1. Review 29-column table
2. Check if data is in correct columns
3. Verify system names are grouped correctly
4. Check for any mis-mapped data

### Lesson 4.2: Validating Tree Structure

**Exercise 4.2.1: Verify Grouping**

1. Navigate grouped tree
2. Verify Solutions are correctly grouped
3. Check Tiers are properly organized
4. Confirm Servers are under correct Tiers

**Exercise 4.2.2: Check Data Completeness**

1. Expand a Server in grouped tree
2. Verify all 29 columns are present
3. Check for empty/null values
4. Verify data matches source

### Lesson 4.3: Handling Errors

**Exercise 4.3.1: Identify Common Errors**

**Error Type 1: No Tables Found**
- Symptom: "No tables found in PDF"
- Cause: PDF doesn't contain tables or wrong flavor
- Solution: Try different flavor or check PDF

**Error Type 2: AI Mapping Failure**
- Symptom: "Failed to parse JSON response"
- Cause: AI model timeout or invalid response
- Solution: Check connection, retry with smaller dataset

**Error Type 3: Missing Data**
- Symptom: Empty columns in output
- Cause: Source table missing data or AI couldn't map
- Solution: Review source PDF, check table structure

## Module 5: Best Practices

### Lesson 5.1: PDF Preparation

**Best Practice 1: Table Quality**
- Use clear, well-defined tables
- Avoid merged cells when possible
- Ensure text is selectable (not scanned images)

**Best Practice 2: Page Selection**
- Extract only relevant pages
- Use page ranges for efficiency
- Test with small subset first

**Best Practice 3: Table Structure**
- Prefer tables with borders (Lattice mode)
- Ensure consistent column structure
- Include headers when possible

### Lesson 5.2: Processing Workflow

**Best Practice 1: Test First**
- Start with single page
- Verify extraction quality
- Then process full document

**Best Practice 2: Validate Incrementally**
- Check table extraction first
- Verify AI structuring
- Validate tree structure last

**Best Practice 3: Save Outputs**
- Download all formats
- Keep original PDFs
- Version your outputs

### Lesson 5.3: Data Quality

**Best Practice 1: Review Before Export**
- Always review 29-column table
- Check grouped tree structure
- Verify data completeness

**Best Practice 2: Compare Versions**
- Use grouped tree XML for comparison
- Compare different contract versions
- Track changes over time

## Hands-On Exercises

### Exercise 1: Basic Extraction

**Objective**: Extract tables from a simple PDF

**Steps**:
1. Upload a PDF with 1-2 tables
2. Use default settings (all pages, Lattice)
3. Extract and structure data
4. Review 29-column table
5. Export CSV

**Success Criteria**:
- ✅ Tables extracted successfully
- ✅ Data appears in 29-column format
- ✅ CSV export works

### Exercise 2: Advanced Navigation

**Objective**: Navigate and filter grouped tree

**Steps**:
1. Process a PDF with multiple solutions
2. Navigate to grouped tree tab
3. Expand all Solutions
4. Filter by Tier Type
5. Drill down to Server details
6. Export filtered data

**Success Criteria**:
- ✅ Can navigate tree structure
- ✅ Filters work correctly
- ✅ All 29 columns visible at Server level

### Exercise 3: Troubleshooting

**Objective**: Handle common issues

**Steps**:
1. Try extracting from PDF with no tables (should show error)
2. Try wrong flavor for table type
3. Test with invalid credentials
4. Practice resolving each issue

**Success Criteria**:
- ✅ Can identify errors
- ✅ Know how to resolve issues
- ✅ Can recover from failures

## Assessment

### Knowledge Check

1. What are the two Camelot flavors and when to use each?
2. What is the difference between Raw XML and Grouped Tree XML?
3. How many columns are in the standardized output?
4. What information is shown at the Server level in the grouped tree?

### Practical Assessment

Complete these tasks:
1. Extract tables from a provided PDF
2. Navigate the grouped tree structure
3. Export data in all three formats
4. Identify and resolve a common error

## Next Steps

After completing this training:
1. Practice with your own PDFs
2. Explore advanced filtering features
3. Review the User Guide for detailed information
4. Consult FAQ for common questions
5. Check Troubleshooting Guide when issues arise

## Additional Resources

- **User Guide**: Comprehensive feature documentation
- **FAQ**: Answers to common questions
- **Troubleshooting Guide**: Solutions to common issues
- **API Reference**: Technical implementation details

