# User Guide - PDF to Grouped Tree Structure Extractor

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Features Overview](#features-overview)
4. [Workflow](#workflow)
5. [Understanding the Output](#understanding-the-output)
6. [Best Practices](#best-practices)

## Introduction

The PDF to Grouped Tree Structure Extractor is a powerful tool designed to extract structured data from PDF documents containing tables and transform it into a standardized 29-column format, then organize it into a hierarchical grouped tree structure (Solution/Tier/Server).

### What This Tool Does

- **Extracts tables** from PDF documents using advanced table detection algorithms
- **Structures data** into a standardized 29-column format using AI-powered data mapping
- **Transforms data** into a grouped tree structure for validation and comparison
- **Exports** data in multiple formats (CSV, JSON, XML)

### Key Benefits

- ✅ Automated data extraction from PDFs
- ✅ AI-powered intelligent data mapping
- ✅ Standardized output format for consistency
- ✅ Multiple export formats for flexibility
- ✅ Visual tree structure for easy navigation

## Getting Started

### Prerequisites

Before using the application, ensure you have:

1. **SAP Cloud SDK for AI Credentials** configured in your `.env` file:
   - `AICORE_CLIENT_ID`
   - `AICORE_CLIENT_SECRET`
   - `AICORE_AUTH_URL`
   - `AICORE_BASE_URL`
   - `AICORE_RESOURCE_GROUP`

2. **PDF Document** containing tables with the data you want to extract

3. **Internet Connection** (required for AI model access)

### First Steps

1. **Access the Application**: Open the application in your web browser
2. **Verify Connection**: Click "Test Connection" in the sidebar to verify SAP Cloud SDK for AI connectivity
3. **Upload PDF**: Click the upload area and select your PDF file
4. **Configure Settings**: Adjust extraction settings in the sidebar if needed
5. **Process Document**: Click "Extract & Structure Data" to begin processing

## Features Overview

### 1. PDF Table Extraction

The application uses **Camelot** library to extract tables from PDF documents:

- **Lattice Mode**: Best for tables with clear lines/borders
- **Stream Mode**: Best for tables without visible borders
- **Page Selection**: Extract from specific pages or all pages
- **Multiple Tables**: Automatically detects and extracts all tables

### 2. AI-Powered Data Structuring

Uses **SAP Cloud SDK for AI (generative)** with models like GPT-4o to:

- Map extracted table data to 29-column structure
- Handle variations in source data format
- Group related data intelligently
- Fill missing values appropriately

### 3. Grouped Tree Structure

Transforms flat data into hierarchical structure:

```
Configuration
└── Solutions
    └── Solution (Service Name)
        └── Tiers
            └── Tier (System/Tier Type)
                └── Servers
                    └── Server (Complete 29-column data)
```

### 4. Multiple Export Formats

Export your data in:
- **CSV**: For spreadsheet applications
- **JSON**: For programmatic access
- **XML**: For validation and comparison

## Workflow

### Step 1: Upload and Configure

1. **Upload PDF File**
   - Click the upload area
   - Select your PDF file
   - Wait for file validation

2. **Configure Extraction Settings** (Sidebar)
   - **Pages**: Specify pages to extract (`all`, `1-5`, `1,3,5`)
   - **Flavor**: Choose `lattice` or `stream` based on table structure

### Step 2: Extract Tables

1. Click **"Extract & Structure Data"** button
2. The application will:
   - Extract tables using Camelot
   - Display extraction summary
   - Show number of tables found

### Step 3: Structure Data

1. AI processing begins automatically after table extraction
2. Data is mapped to 29-column format
3. Progress is shown with spinner
4. Results are displayed when complete

### Step 4: View and Export

1. **View Results** in different tabs:
   - 29-Column Table: Main structured data view
   - Raw XML: Step 1 output (flat structure)
   - Grouped Tree: Step 2 output (hierarchical structure)
   - JSON View: Data in JSON format
   - CSV View: Data in CSV format

2. **Download Results**:
   - Use download buttons in each tab
   - Files are named based on source PDF filename

## Understanding the Output

### 29-Column Structure

The standardized output includes these columns:

**System Information:**
- `amount`, `system_name`, `service`, `database`, `tiername`, `tier_type`
- `system_id`

**Hardware Specifications:**
- `ram_gib`, `cpus_physvirt`, `saps`
- `no_of_add_hana_nodes`, `no_of_standby_nodes`

**Storage:**
- `tenant__user_data_size`
- `amount_storage_1_gb`, `iops1`, `through_put1`
- `amount_storage_2_gb`, `iops2`, `through_put2`
- `storage_information_1`

**Configuration:**
- `backup_class`, `os`, `sla`, `dr`
- `add_hw_for_dr`, `pacemaker_included`
- `add_requirements`, `phase`, `server`

### Grouped Tree Structure

The grouped tree organizes data by:

1. **Solution** (Service Name): Top-level grouping
2. **Tier**: Groups systems by tier type (PROD/nonPROD)
3. **Server**: Individual server instances with complete data

### Data Filtering

The application automatically filters out:
- Connectivity services (VPN, Direct Connect, etc.)
- Migration services
- Supplementary services

## Best Practices

### PDF Preparation

1. **Ensure Table Quality**:
   - Use clear, well-defined tables
   - Avoid merged cells when possible
   - Ensure text is readable (not scanned images)

2. **Page Selection**:
   - Extract only relevant pages to improve speed
   - Use page ranges for large documents

3. **Table Structure**:
   - Prefer tables with clear borders (use Lattice mode)
   - For tables without borders, use Stream mode

### Data Validation

1. **Review Extracted Tables**:
   - Check the extraction summary
   - Verify table count matches expectations

2. **Validate Structured Data**:
   - Review the 29-column table
   - Check for missing or incorrect mappings
   - Verify data types are correct

3. **Inspect Grouped Tree**:
   - Navigate through Solutions → Tiers → Servers
   - Verify hierarchical grouping is correct
   - Check all 29 columns are present at Server level

### Export and Usage

1. **Choose Appropriate Format**:
   - CSV for spreadsheet analysis
   - JSON for programmatic processing
   - XML for validation workflows

2. **File Naming**:
   - Files are automatically named based on source PDF
   - Keep original PDFs for reference

3. **Version Control**:
   - Download outputs for different contract versions
   - Compare grouped tree XMLs for validation

## Troubleshooting

### Common Issues

**Issue**: No tables found in PDF
- **Solution**: Check if PDF contains actual tables (not images)
- Try different flavor (lattice vs stream)
- Verify page selection includes correct pages

**Issue**: AI structuring fails
- **Solution**: Check SAP Cloud SDK for AI connection
- Verify credentials in `.env` file
- Check if model deployment is available

**Issue**: Missing data in output
- **Solution**: Review source PDF table structure
- Check if data is in expected format
- Verify AI model has sufficient context

For more detailed troubleshooting, see the Troubleshooting Guide.

## Support

For additional help:
- Review the Training Manual for step-by-step tutorials
- Check the FAQ for common questions
- Consult the API Reference for technical details

