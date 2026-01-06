# Frequently Asked Questions (FAQ)

## Table of Contents
1. [General Questions](#general-questions)
2. [Setup and Configuration](#setup-and-configuration)
3. [PDF Extraction](#pdf-extraction)
4. [AI Processing](#ai-processing)
5. [Data Output](#data-output)
6. [Troubleshooting](#troubleshooting)

## General Questions

### Q1: What is this application used for?

**A:** This application extracts structured data from PDF documents containing tables and transforms it into a standardized 29-column format, then organizes it into a hierarchical grouped tree structure. It's particularly useful for processing contract documents, quotes, and other structured PDFs.

### Q2: What file formats does it support?

**A:** Currently, the application only supports PDF files. The PDF should contain tables with structured data.

### Q3: Is there a file size limit?

**A:** There's no hard-coded limit, but very large PDFs may take longer to process. For best performance, consider extracting specific pages rather than processing entire large documents.

### Q4: Do I need an internet connection?

**A:** Yes, an internet connection is required because the application uses SAP Cloud SDK for AI (generative) which requires cloud connectivity to access AI models.

### Q5: Is my data secure?

**A:** Yes. Your PDF files are processed locally, and only the extracted table data is sent to the AI service for structuring. The application doesn't store your files permanently. However, ensure your SAP credentials are kept secure and not shared.

## Setup and Configuration

### Q6: How do I set up SAP Cloud SDK for AI credentials?

**A:** Create a `.env` file in the project root directory with the following variables:
```
AICORE_CLIENT_ID=your_client_id
AICORE_CLIENT_SECRET=your_client_secret
AICORE_AUTH_URL=your_auth_url
AICORE_BASE_URL=your_base_url
AICORE_RESOURCE_GROUP=default
```

### Q7: What if I don't have SAP Cloud SDK for AI credentials?

**A:** The application requires SAP Cloud SDK for AI credentials to function. Contact your SAP administrator or refer to SAP documentation for obtaining these credentials.

### Q8: How do I test if my credentials are working?

**A:** Click the "Test Connection" button in the sidebar. You should see a success message with connection details including the deployment ID and model name.

### Q9: Can I use OpenAI directly instead of SAP Cloud SDK for AI?

**A:** The current version is configured to use SAP Cloud SDK for AI. The code structure supports OpenAI as a fallback, but it's not currently enabled in the UI.

### Q10: What is the difference between SAP_* and AICORE_* environment variables?

**A:** Both naming conventions are supported. The application checks for both:
- `SAP_CLIENT_ID` or `AICORE_CLIENT_ID`
- `SAP_CLIENT_SECRET` or `AICORE_CLIENT_SECRET`
- `SAP_AUTH_URL` or `AICORE_AUTH_URL`

Use whichever convention your organization prefers.

## PDF Extraction

### Q11: What is the difference between "Lattice" and "Stream" flavors?

**A:** 
- **Lattice**: Best for tables with clear borders/lines. Uses line detection to identify table boundaries.
- **Stream**: Best for tables without visible borders. Uses text alignment and spacing to detect tables.

**Recommendation**: Start with Lattice. If no tables are found, try Stream.

### Q12: How do I specify which pages to extract?

**A:** In the sidebar, use the "Pages to extract" field:
- `all` - Extract from all pages
- `1-5` - Extract from pages 1 through 5
- `1,3,5` - Extract from specific pages (1, 3, and 5)
- `1-3,5,7-10` - Mix of ranges and individual pages

### Q13: What if no tables are found in my PDF?

**A:** Try these solutions:
1. Switch from Lattice to Stream (or vice versa)
2. Check if the PDF contains actual tables (not just images)
3. Verify page selection includes pages with tables
4. Ensure tables are not scanned images (text should be selectable)

### Q14: Can I extract tables from scanned PDFs?

**A:** The application works best with PDFs containing actual text and tables. Scanned PDFs (images) may not work well unless they've been OCR'd. For best results, use PDFs with selectable text.

### Q15: How many tables can be extracted at once?

**A:** There's no hard limit, but processing time increases with more tables. The application will extract all tables found in the specified pages.

## AI Processing

### Q16: Which AI model is used?

**A:** The application uses models available through SAP Cloud SDK for AI. It prefers models in this order:
1. gpt-4o
2. gpt-4
3. gpt-4.1
4. anthropic--claude-3.5-sonnet
5. anthropic--claude-4.5-sonnet
6. gpt-5

It automatically selects the first available model from your deployments.

### Q17: How long does AI processing take?

**A:** Processing time depends on:
- Number of tables extracted
- Amount of data in tables
- Model response time
- Network latency

Typically, processing takes 30-60 seconds for moderate-sized documents.

### Q18: What if AI processing fails?

**A:** Common causes and solutions:
- **Connection error**: Check SAP Cloud SDK for AI connection
- **Timeout**: Try processing fewer pages or smaller tables
- **Invalid response**: Check if model deployment is available
- **Mapping errors**: Review source table structure

### Q19: Can I customize the AI prompt?

**A:** The AI prompt is built into the application to ensure consistent 29-column mapping. Customization would require code changes.

### Q20: What happens if the AI model returns incomplete data?

**A:** The application attempts to handle incomplete JSON responses by:
- Detecting incomplete structures
- Adding missing closing brackets/braces
- Providing error messages with context

If data is still incomplete, try reprocessing or check the source PDF quality.

## Data Output

### Q21: What are the 29 columns?

**A:** The standardized columns are:
1. amount, system_name, service, database, tiername, tier_type
2. system_id, ram_gib, cpus_physvirt, saps
3. no_of_add_hana_nodes, no_of_standby_nodes, tenant__user_data_size
4. amount_storage_1_gb, iops1, through_put1
5. amount_storage_2_gb, iops2, through_put2
6. storage_information_1, backup_class, os, sla, dr
7. add_hw_for_dr, pacemaker_included, add_requirements, phase, server

### Q22: What is the difference between Raw XML and Grouped Tree XML?

**A:**
- **Raw XML (Step 1)**: Flat structure with all rows at the same level. Each `<row>` contains all 29 columns.
- **Grouped Tree XML (Step 2)**: Hierarchical structure organized by Solution → Tier → Server. Groups related data together.

### Q23: Why are some rows filtered out?

**A:** The application automatically filters out:
- Connectivity services (VPN, Direct Connect, VPC Peering, etc.)
- Migration services
- Supplementary services

These are excluded to focus on core infrastructure data.

### Q24: Can I export filtered data?

**A:** Yes! In the Grouped Tree tab, you can:
1. Use filters (Solution, Tier Type, Server Name)
2. View filtered results in the comparison table
3. Download the filtered data as CSV

### Q25: What file formats can I export?

**A:** You can export in three formats:
- **CSV**: For spreadsheet applications (Excel, Google Sheets)
- **JSON**: For programmatic access and APIs
- **XML**: For validation workflows and comparison

### Q26: How are exported files named?

**A:** Files are automatically named based on the source PDF filename:
- `{pdf_filename}_raw.xml`
- `{pdf_filename}_grouped_tree.xml`
- `{pdf_filename}_servers_comparison.csv`

## Troubleshooting

### Q27: I get "Missing required SAP credentials" error

**A:** 
1. Check if `.env` file exists in project root
2. Verify all required variables are set:
   - AICORE_CLIENT_ID
   - AICORE_CLIENT_SECRET
   - AICORE_AUTH_URL
3. Restart the application after updating `.env`

### Q28: Connection test fails

**A:**
1. Verify credentials in `.env` file
2. Check network connectivity
3. Ensure SAP Cloud SDK for AI service is accessible
4. Verify resource group is correct
5. Check if model deployments are available

### Q29: Tables are extracted but AI structuring fails

**A:**
1. Check SAP Cloud SDK for AI connection
2. Verify model deployment is available
3. Try processing smaller dataset
4. Check error message for specific issue
5. Review source table structure

### Q30: Data in output doesn't match source PDF

**A:**
1. Review extracted tables summary
2. Check if correct pages were processed
3. Verify table structure in source PDF
4. Try different flavor (Lattice/Stream)
5. Check AI mapping in 29-column table

### Q31: Application is slow or unresponsive

**A:**
1. Process fewer pages at a time
2. Check network connectivity
3. Verify SAP Cloud SDK for AI service status
4. Close other browser tabs/applications
5. Try again after a few moments

### Q32: Downloaded files are empty or corrupted

**A:**
1. Ensure processing completed successfully
2. Check browser download settings
3. Try downloading again
4. Verify file wasn't blocked by security software
5. Check file size (should not be 0 bytes)

### Q33: Can't see all columns in the table view

**A:**
1. Use horizontal scroll in the table
2. Expand browser window width
3. Use "Grouped Tree" tab to see all columns at Server level
4. Export CSV to view in spreadsheet application

### Q34: Grouped tree shows incorrect hierarchy

**A:**
1. Review source PDF table structure
2. Check how data is grouped by service/system
3. Verify AI mapping in 29-column table
4. Check if system_name and service columns are correct

### Q35: How do I report bugs or request features?

**A:** Contact your system administrator or development team. Include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- PDF sample (if relevant)

## Additional Resources

- **User Guide**: Comprehensive documentation
- **Training Manual**: Step-by-step tutorials
- **Troubleshooting Guide**: Detailed solutions
- **API Reference**: Technical documentation

For more help, consult these resources or contact support.

