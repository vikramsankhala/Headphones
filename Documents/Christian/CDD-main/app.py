import streamlit as st
import camelot
import pandas as pd
import json
import csv
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from io import BytesIO, StringIO
from html import escape
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
import threading
import tempfile
import os
from dotenv import load_dotenv
import requests
from urllib.parse import urljoin
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Load environment variables from .env file
load_dotenv()  # reads variables from a .env file and sets them in os.environ

# Page configuration
st.set_page_config(
    page_title="PDF → 29-Column Structured Data Extractor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load SAP Service Key credentials from environment variables
# Support both AICORE_* and SAP_* naming conventions
SAP_CLIENT_ID = os.environ.get('SAP_CLIENT_ID') or os.environ.get('AICORE_CLIENT_ID', '')
SAP_CLIENT_SECRET = os.environ.get('SAP_CLIENT_SECRET') or os.environ.get('AICORE_CLIENT_SECRET', '')
SAP_AUTH_URL = os.environ.get('SAP_AUTH_URL') or os.environ.get('AICORE_AUTH_URL', '')
# AICORE_BASE_URL might include the path, so we need to handle it
aicore_base_url = os.environ.get('AICORE_BASE_URL', '')
if aicore_base_url:
    # Strip /v2 or /v1 from base URL (same logic as test_connection.py)
    # We'll add the version path in the endpoint itself
    SAP_AI_API_URL = aicore_base_url.rstrip('/v2').rstrip('/v1').rstrip('/')
else:
    SAP_AI_API_URL = os.environ.get('SAP_AI_API_URL', 'https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com')

# Extract resource group if provided
SAP_RESOURCE_GROUP = os.environ.get('AICORE_RESOURCE_GROUP', 'default')
def get_sap_service_key():
    """
    Get SAP Service Key configuration as a dictionary.
    Returns None if required credentials are missing.
    """
    if not SAP_CLIENT_ID or not SAP_CLIENT_SECRET:
        return None
    
    return {
        "clientid": SAP_CLIENT_ID,
        "clientsecret": SAP_CLIENT_SECRET,
        "url": SAP_AUTH_URL,
        "serviceurls": {
            "AI_API_URL": SAP_AI_API_URL
        }
    }

def validate_sap_credentials():
    """Validate that SAP credentials are properly configured."""
    missing = []
    if not SAP_CLIENT_ID:
        missing.append("SAP_CLIENT_ID")
    if not SAP_CLIENT_SECRET:
        missing.append("SAP_CLIENT_SECRET")
    if not SAP_AUTH_URL:
        missing.append("SAP_AUTH_URL")
    
    if missing:
        return False, f"Missing required SAP credentials: {', '.join(missing)}"
    return True, "SAP credentials configured"

def test_sap_gen_ai_hub_connection():
    """
    Test connection to SAP Cloud SDK for AI (generative) using the SDK's LangChain integration.
    Returns a tuple: (success: bool, message: str, details: dict)
    """
    try:
        # Set environment variables for SDK
        os.environ['AICORE_CLIENT_ID'] = SAP_CLIENT_ID
        os.environ['AICORE_CLIENT_SECRET'] = SAP_CLIENT_SECRET
        os.environ['AICORE_AUTH_URL'] = SAP_AUTH_URL
        os.environ['AICORE_BASE_URL'] = os.environ.get('AICORE_BASE_URL', SAP_AI_API_URL)
        os.environ['AICORE_RESOURCE_GROUP'] = SAP_RESOURCE_GROUP
        
        # Initialize SDK proxy client (required for LangChain integration)
        proxy_client = get_proxy_client('gen-ai-hub')
        
        # Get deployments
        deployments = proxy_client.get_deployments()

        print(f"Found {len(deployments)} deployments.")
        for dep in deployments:
            print(f"Deployment ID: {dep.deployment_id}, Model Name: {dep.model_name}")

        
        # Try to find a suitable model
        preferred_models = ['gpt-4o', 'gpt-4', 'gpt-4.1', 'anthropic--claude-3.5-sonnet', 'anthropic--claude-4.5-sonnet', 'gpt-5']
        selected_model = None
        selected_deployment = None
        
        for model_name in preferred_models:
            for dep in deployments:
                if dep.model_name == model_name:
                    selected_model = model_name
                    selected_deployment = dep
                    break
            if selected_deployment:
                break
        
        if not selected_deployment:
            return False, "❌ No suitable deployment found. Available models: " + ", ".join([d.model_name for d in deployments[:10]]), {
                'auth_status': 'success',
                'deployments_found': len(deployments),
                'available_models': [d.model_name for d in deployments[:15]]
            }
        
        # Test using LangChain ChatOpenAI (the proper SDK way)
        try:
            chat_model = ChatOpenAI(
                model_name=selected_model,
                deployment_id=selected_deployment.deployment_id,
                temperature=0,
                max_tokens=10
            )
            
            # Test with a simple message
            response = chat_model.invoke([HumanMessage(content="test")])
            
            details = {
                'auth_status': 'success',
                'sdk_status': 'initialized',
                'sdk_method': 'LangChain ChatOpenAI',
                'deployment_id': selected_deployment.deployment_id,
                'model_name': selected_deployment.model_name,
                'response_received': True,
                'response_preview': str(response.content)[:200] if hasattr(response, 'content') else str(response)[:200]
            }
            
            return True, f"✅ Connection successful! {selected_model} deployment '{selected_deployment.deployment_id}' is accessible via SDK LangChain integration", details
            
        except Exception as langchain_error:
            # If LangChain fails, provide helpful error message
            error_msg = str(langchain_error)
            details = {
                'auth_status': 'success',
                'sdk_status': 'initialized',
                'deployment_id': selected_deployment.deployment_id,
                'model_name': selected_deployment.model_name,
                'langchain_error': error_msg,
                'available_models': [d.model_name for d in deployments[:10]]
            }
            
            return False, f"❌ Failed to connect via SDK LangChain integration: {error_msg}\n\nModel: {selected_model}\nDeployment ID: {selected_deployment.deployment_id}", details
            
    except Exception as e:
        import traceback
        return False, f"❌ Error testing connection: {str(e)}", {
            'error': str(e),
            'traceback': traceback.format_exc()[:500]
        }

# Define the 29-column structure
COLUMN_STRUCTURE = [
    "amount", "system_name", "service", "database", "tiername", "tier_type",
    "system_id", "ram_gib", "cpus_physvirt", "saps", "no_of_add_hana_nodes",
    "no_of_standby_nodes", "tenant__user_data_size", "amount_storage_1_gb",
    "iops1", "through_put1", "amount_storage_2_gb", "iops2", "through_put2",
    "storage_information_1", "backup_class", "os", "sla", "dr", "add_hw_for_dr",
    "pacemaker_included", "add_requirements", "phase", "server"
]

def get_sap_gen_ai_client():
    """
    Get SAP Cloud SDK for AI (generative) proxy client.
    Returns the proxy client instance, or None if initialization fails.
    """
    try:
        # Set environment variables for SDK
        os.environ['AICORE_CLIENT_ID'] = SAP_CLIENT_ID
        os.environ['AICORE_CLIENT_SECRET'] = SAP_CLIENT_SECRET
        os.environ['AICORE_AUTH_URL'] = SAP_AUTH_URL
        os.environ['AICORE_BASE_URL'] = os.environ.get('AICORE_BASE_URL', SAP_AI_API_URL)
        os.environ['AICORE_RESOURCE_GROUP'] = SAP_RESOURCE_GROUP
        
        # Initialize SDK proxy client
        proxy_client = get_proxy_client('gen-ai-hub')
        
        # Verify a suitable deployment is available
        deployments = proxy_client.get_deployments()
        print(f"Found {len(deployments)} deployments.")
        print("Available models:")
        for dep in deployments:
            print(f"Deployment ID: {dep.deployment_id}, Model Name: {dep.model_name}")

        preferred_models = ['gpt-4o', 'gpt-4', 'gpt-4.1', 'anthropic--claude-3.5-sonnet', 'gpt-5']
        model_available = any(dep.model_name in preferred_models for dep in deployments)
        
        if not model_available:
            st.warning(f"⚠️ No preferred model deployment found. Available models: {', '.join([d.model_name for d in deployments[:10]])}")
            return None
        
        return proxy_client
    except Exception as e:
        st.error(f"Error initializing SAP Cloud SDK for AI (generative) client: {str(e)}")
        return None


def extract_tables_with_camelot(uploaded_file, pages='all', flavor='lattice'):
    """
    Extract tables from PDF using Camelot.
    Returns: list of tables (camelot Table objects)
    """
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        
        try:
            # Extract tables using Camelot
            tables = camelot.read_pdf(tmp_path, pages=pages, flavor=flavor)
            
            if not tables:
                # Try with stream flavor if lattice fails
                st.warning("No tables found with 'lattice' flavor. Trying 'stream' flavor...")
                tables = camelot.read_pdf(tmp_path, pages=pages, flavor='stream')
            
            return tables, tmp_path
        finally:
            # Clean up temp file after a delay (in case Camelot still needs it)
            pass  # We'll clean it up later
            
    except Exception as e:
        raise Exception(f"Failed to extract tables with Camelot: {str(e)}")

def tables_to_dataframe(tables):
    """
    Convert Camelot tables to a single pandas DataFrame.
    """
    if not tables:
        return pd.DataFrame()
    
    all_rows = []
    for i, table in enumerate(tables):
        df = table.df
        # Add metadata columns
        df['table_id'] = i + 1
        df['page'] = table.page
        all_rows.append(df)
    
    if all_rows:
        combined_df = pd.concat(all_rows, ignore_index=True)
        return combined_df
    return pd.DataFrame()

def process_table_chunk(proxy_client, tables_chunk, column_structure, chunk_id, model_info):
    """
    Process a chunk of tables using AI. This function is designed to run in parallel.
    """
    # Convert tables to a readable format
    tables_summary = []
    for i, table in enumerate(tables_chunk):
        df = table.df
        tables_summary.append({
            "table_id": chunk_id * 100 + i + 1,  # Unique ID across chunks
            "page": table.page,
            "rows": df.to_dict('records')[:10] if len(df) > 10 else df.to_dict('records'),
            "total_rows": len(df)
        })
    
    prompt = f"""You are a data extraction expert. I have extracted tables from a PDF document using Camelot.
    
Your task is to map the extracted table data to a standardized 29-column structure. The columns are:
{', '.join(column_structure)}

Extracted Tables Data:
{json.dumps(tables_summary, indent=2, default=str)}

Instructions:
1. Analyze the extracted table data and map each row to the 29-column structure
2. If a column doesn't exist in the source data, leave it empty/null
3. Group data by System name when applicable
4. Return a JSON object with a "data" key containing an array of objects, where each object represents a row with all 29 columns
5. Ensure proper data types (strings for text, numbers for numeric values)
6. Process all rows from the provided tables

Return ONLY valid JSON object with structure: {{"data": [{{...}}, {{...}}]}} without any markdown, code blocks, or explanations:
"""
    
    try:
        selected_model, selected_deployment = model_info
        
        # Create a new chat model instance for this thread
        chat_model = ChatOpenAI(
            model_name=selected_model,
            deployment_id=selected_deployment.deployment_id,
            temperature=0.3,
            max_tokens=16000
        )
        
        # Create messages for LangChain
        messages = [
            SystemMessage(content="You are a data mapping expert. Return ONLY valid JSON objects with a 'data' key containing an array, without any markdown or code blocks."),
            HumanMessage(content=prompt)
        ]
        
        # Invoke the model
        response = chat_model.invoke(messages)
        
        # Extract content from LangChain response
        if hasattr(response, 'content'):
            result = response.content.strip()
        else:
            result = str(response).strip()
        
        # Clean JSON string
        if result.startswith("```json"):
            result = result[7:]
        elif result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()
        
        # Extract JSON
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            result = result[json_start:json_end]
        
        if json_start == -1:
            json_start = result.find('[')
            json_end = result.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                result = result[json_start:json_end]
        
        result = result.strip()
        
        # Fix common JSON issues
        import re
        result = re.sub(r',\s*}', '}', result)
        result = re.sub(r',\s*]', ']', result)
        result = re.sub(r"'(\w+)':", r'"\1":', result)
        
        # Fix incomplete JSON
        open_braces = result.count('{')
        close_braces = result.count('}')
        open_brackets = result.count('[')
        close_brackets = result.count(']')
        
        if open_braces > close_braces or open_brackets > close_brackets:
            missing_braces = open_braces - close_braces
            missing_brackets = open_brackets - close_brackets
            result += ']' * missing_brackets + '}' * missing_braces
        
        # Parse JSON
        json_data = json.loads(result)
        
        # Extract data array
        if isinstance(json_data, dict):
            for key in ['data', 'rows', 'records', 'items']:
                if key in json_data and isinstance(json_data[key], list):
                    return json_data[key]
            return []
        
        if isinstance(json_data, list):
            return json_data
        
        return []
        
    except Exception as e:
        raise Exception(f"Error processing chunk {chunk_id}: {str(e)}")

def structure_data_with_sap_gen_ai(proxy_client, tables_data, column_structure, use_parallel=True, max_workers=3):
    """
    Use SAP Cloud SDK for AI (generative) to map extracted table data to the 29-column structure.
    Supports parallel processing for faster execution.
    """
    if not tables_data:
        return []
    
    try:
        # Get deployments and select a suitable model
        deployments = proxy_client.get_deployments()
        preferred_models = ['gpt-4o', 'gpt-4', 'gpt-4.1', 'anthropic--claude-3.5-sonnet', 'anthropic--claude-4.5-sonnet', 'gpt-5']
        selected_model = None
        selected_deployment = None
        
        for model_name in preferred_models:
            for dep in deployments:
                if dep.model_name == model_name:
                    selected_model = model_name
                    selected_deployment = dep
                    break
            if selected_deployment:
                break
        
        if not selected_deployment:
            raise Exception(f"No suitable model found. Available models: {', '.join([d.model_name for d in deployments[:10]])}")
        
        model_info = (selected_model, selected_deployment)
        
        # Determine if we should use parallel processing
        total_tables = len(tables_data)
        should_parallelize = use_parallel and total_tables > 1
        
        if should_parallelize:
            # Split tables into chunks for parallel processing
            # Each chunk should have 1-2 tables to balance load
            chunk_size = max(1, min(2, total_tables // max_workers + 1))
            table_chunks = []
            
            for i in range(0, total_tables, chunk_size):
                chunk = tables_data[i:i + chunk_size]
                table_chunks.append((chunk, i // chunk_size))
            
            # Process chunks in parallel
            all_results = []
            with ThreadPoolExecutor(max_workers=min(max_workers, len(table_chunks))) as executor:
                # Submit all tasks
                future_to_chunk = {
                    executor.submit(process_table_chunk, proxy_client, chunk, column_structure, chunk_id, model_info): chunk_id
                    for chunk, chunk_id in table_chunks
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_chunk):
                    chunk_id = future_to_chunk[future]
                    try:
                        result = future.result()
                        all_results.extend(result)
                    except Exception as e:
                        st.warning(f"Chunk {chunk_id} processing failed: {str(e)}")
                        # Continue with other chunks
            
            return all_results
        else:
            # Sequential processing (original method for single table or when parallel is disabled)
            # Convert tables to a readable format
            tables_summary = []
            for i, table in enumerate(tables_data):
                df = table.df
                tables_summary.append({
                    "table_id": i + 1,
                    "page": table.page,
                    "rows": df.to_dict('records')[:10] if len(df) > 10 else df.to_dict('records'),
                    "total_rows": len(df)
                })
            
            prompt = f"""You are a data extraction expert. I have extracted tables from a PDF document using Camelot.
    
Your task is to map the extracted table data to a standardized 29-column structure. The columns are:
{', '.join(column_structure)}

Extracted Tables Data:
{json.dumps(tables_summary, indent=2, default=str)}

Instructions:
1. Analyze the extracted table data and map each row to the 29-column structure
2. If a column doesn't exist in the source data, leave it empty/null
3. Group data by System name when applicable
4. Return a JSON object with a "data" key containing an array of objects, where each object represents a row with all 29 columns
5. Ensure proper data types (strings for text, numbers for numeric values)
6. If there are multiple tables, combine them into a single array

Return ONLY valid JSON object with structure: {{"data": [{{...}}, {{...}}]}} without any markdown, code blocks, or explanations:
"""
            
            chat_model = ChatOpenAI(
                model_name=selected_model,
                deployment_id=selected_deployment.deployment_id,
                temperature=0.3,
                max_tokens=16000
            )
            
            messages = [
                SystemMessage(content="You are a data mapping expert. Return ONLY valid JSON objects with a 'data' key containing an array, without any markdown or code blocks."),
                HumanMessage(content=prompt)
            ]
            
            response = chat_model.invoke(messages)
            
            if hasattr(response, 'content'):
                result = response.content.strip()
            else:
                result = str(response).strip()
            
            # Clean and parse JSON (same as before)
            if result.startswith("```json"):
                result = result[7:]
            elif result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                result = result[json_start:json_end]
            
            if json_start == -1:
                json_start = result.find('[')
                json_end = result.rfind(']') + 1
                if json_start != -1 and json_end > json_start:
                    result = result[json_start:json_end]
            
            result = result.strip()
            
            import re
            result = re.sub(r',\s*}', '}', result)
            result = re.sub(r',\s*]', ']', result)
            result = re.sub(r"'(\w+)':", r'"\1":', result)
            
            open_braces = result.count('{')
            close_braces = result.count('}')
            open_brackets = result.count('[')
            close_brackets = result.count(']')
            
            if open_braces > close_braces or open_brackets > close_brackets:
                missing_braces = open_braces - close_braces
                missing_brackets = open_brackets - close_brackets
                result += ']' * missing_brackets + '}' * missing_braces
            
            try:
                json_data = json.loads(result)
            except json.JSONDecodeError as e:
                error_pos = e.pos if hasattr(e, 'pos') else len(result)
                error_msg = f"Failed to parse JSON response.\n"
                error_msg += f"Error: {e.msg} at position {error_pos}\n\n"
                error_msg += f"Response length: {len(result)} characters\n"
                raise Exception(error_msg)
            
            if isinstance(json_data, dict):
                for key in ['data', 'rows', 'records', 'items']:
                    if key in json_data and isinstance(json_data[key], list):
                        return json_data[key]
                return []
            
            if isinstance(json_data, list):
                return json_data
            
            return []
        
    except Exception as e:
        raise Exception(f"SAP Cloud SDK for AI (generative) error while structuring data: {str(e)}")

def is_connectivity_service(row):
    """
    Check if a row represents a connectivity service that should be excluded.
    """
    # Check for sap_connectivity field
    if 'sap_connectivity' in row and row.get('sap_connectivity'):
        return True
    
    # Check service name for connectivity-related keywords
    service = str(row.get('service', '')).lower()
    connectivity_keywords = [
        'vpn', 'direct connect', 'vpc peering', 'transit gateway',
        'loadbalancer', 'load balancer', 'connectivity', 'egress',
        'supplementary service', 'tgw attachment'
    ]
    if any(keyword in service for keyword in connectivity_keywords):
        return True
    
    # Check system_name for connectivity-related keywords
    system_name = str(row.get('system_name', '')).lower()
    if any(keyword in system_name for keyword in connectivity_keywords):
        return True
    
    return False

def is_migration_service(row):
    """
    Check if a row represents a migration service that should be excluded.
    """
    # Check service name for migration-related keywords
    service = str(row.get('service', '')).lower()
    migration_keywords = [
        'migration', 'migration server', 'iaas basic'
    ]
    if any(keyword in service for keyword in migration_keywords):
        return True
    
    # Check system_name for migration-related keywords
    system_name = str(row.get('system_name', '')).lower()
    if any(keyword in system_name for keyword in migration_keywords):
        return True
    
    # Check server name for migration-related keywords
    server = str(row.get('server', '')).lower()
    if any(keyword in server for keyword in migration_keywords):
        return True
    
    return False

def should_exclude_row(row):
    """
    Check if a row should be excluded from display (connectivity or migration services).
    """
    return is_connectivity_service(row) or is_migration_service(row)

def create_29_column_dataframe(structured_data):
    """
    Create a pandas DataFrame with exactly 29 columns matching the structure.
    Filters out connectivity and migration services.
    """
    if not structured_data:
        return pd.DataFrame(columns=COLUMN_STRUCTURE)
    
    # Ensure all rows have all 29 columns and filter out connectivity and migration services
    normalized_rows = []
    for row in structured_data:
        # Skip connectivity and migration services
        if should_exclude_row(row):
            continue
            
        normalized_row = {}
        for col in COLUMN_STRUCTURE:
            normalized_row[col] = row.get(col, "")
        normalized_rows.append(normalized_row)
    
    df = pd.DataFrame(normalized_rows)
    return df

def dataframe_to_csv(df):
    """Convert DataFrame to CSV string."""
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def dataframe_to_json(df):
    """Convert DataFrame to JSON string."""
    return df.to_json(orient='records', indent=2)

def dataframe_to_xml(df):
    """Convert DataFrame to XML string (raw XML - step 1 output)."""
    root = ET.Element("document")
    
    row_id = 1
    for idx, row in df.iterrows():
        # Skip connectivity and migration services
        row_dict = row.to_dict()
        if should_exclude_row(row_dict):
            continue
            
        row_elem = ET.SubElement(root, "row", id=str(row_id))
        row_id += 1
        for col in COLUMN_STRUCTURE:
            cell_elem = ET.SubElement(row_elem, col)
            value = row.get(col, "")
            if pd.notna(value):
                cell_elem.text = str(value)
            else:
                cell_elem.text = ""
    
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    return pretty_xml

def transform_to_grouped_tree(raw_xml_string):
    """
    Transform raw XML (step 1) to grouped tree structure (step 2).
    Groups by Solution > Tier > Server hierarchy.
    """
    try:
        # Parse raw XML
        root = ET.fromstring(raw_xml_string)
        
        # Create output structure with Configuration as root
        configuration_root = ET.Element("Configuration")
        solutions_root = ET.SubElement(configuration_root, "Solutions")
        
        # Dictionary to group rows by service
        services = {}
        
        # Process each row
        for row in root.findall('row'):
            # Check for sap_connectivity field (connectivity services)
            sap_connectivity = row.find('sap_connectivity')
            if sap_connectivity is not None and sap_connectivity.text:
                continue
            
            service = row.find('service')
            server = row.find('server')
            
            # Skip rows without service or server data
            if service is None or not service.text or not service.text.strip():
                continue
            if server is None or not server.text or not server.text.strip():
                continue
            
            # Check if service name indicates connectivity service
            service_name = service.text.strip().lower()
            connectivity_keywords = [
                'vpn', 'direct connect', 'vpc peering', 'transit gateway',
                'loadbalancer', 'load balancer', 'connectivity', 'egress',
                'supplementary service', 'tgw attachment'
            ]
            if any(keyword in service_name for keyword in connectivity_keywords):
                continue
            
            # Check if service name indicates migration service
            migration_keywords = [
                'migration', 'migration server', 'iaas basic'
            ]
            if any(keyword in service_name for keyword in migration_keywords):
                continue
            
            # Check server name for migration keywords
            server_name = server.text.strip().lower()
            if any(keyword in server_name for keyword in migration_keywords):
                continue
            
            # Check system_name for migration keywords
            system_name_elem = row.find('system_name')
            if system_name_elem is not None and system_name_elem.text:
                system_name = system_name_elem.text.strip().lower()
                if any(keyword in system_name for keyword in migration_keywords):
                    continue
            
            service_name = service.text.strip()
            server_name = server.text.strip()
            
            # Get other row data
            system_name = row.find('system_name')
            tier_type = row.find('tier_type')
            database = row.find('database')
            
            # Create tier data
            tier_data = {
                'system_name': system_name.text if system_name is not None and system_name.text else "",
                'tier_type': tier_type.text if tier_type is not None and tier_type.text else "",
                'database': database.text if database is not None and database.text else "",
                'server': server_name,
                'row': row  # Keep reference to full row for all data
            }
            
            # Group by service
            if service_name not in services:
                services[service_name] = []
            services[service_name].append(tier_data)
        
        # Create Solutions structure
        for service_name, tiers in services.items():
            # Create Solution element
            solution = ET.SubElement(solutions_root, "Solution")
            solution_name_elem = ET.SubElement(solution, "SolutionName")
            solution_name_elem.text = service_name
            
            # Create Tiers container
            tiers_container = ET.SubElement(solution, "Tiers")
            
            # Add each tier
            for tier_data in tiers:
                system_name = tier_data['system_name']
                server_name = tier_data['server']
                row = tier_data['row']  # Original row data
                
                # Create Tier element
                tier = ET.SubElement(tiers_container, "Tier")
                
                # Helper function to get row value
                def get_row_value(row_elem, element_name, default=""):
                    elem = row_elem.find(element_name)
                    if elem is not None and elem.text:
                        return elem.text.strip()
                    return default
                
                # Helper function to add tier element
                def add_tier_element(parent, name, value):
                    elem = ET.SubElement(parent, name)
                    elem.text = str(value) if value else ""
                
                # Helper functions for transformations
                def get_gxp_value(add_requirements):
                    if not add_requirements:
                        return "N"
                    elif "GXP" in str(add_requirements).upper():
                        return "Y"
                    else:
                        return "N"
                
                def get_hipaa_value(add_requirements):
                    if not add_requirements:
                        return "N"
                    elif "HIPAA" in str(add_requirements).upper():
                        return "Y"
                    else:
                        return "N"
                
                def get_dr_scenario_value(dr_value):
                    if not dr_value:
                        return ""
                    result = str(dr_value).replace("_", "").replace("m", "").replace("M", "").upper()
                    return result
                
                def format_sla_decimal(sla_text):
                    if not sla_text:
                        return "0.0"
                    if '%' in str(sla_text):
                        try:
                            numeric_part = str(sla_text).replace('%', '').strip()
                            sla_float = float(numeric_part)
                            return f"{sla_float:.1f}"
                        except:
                            return "0.0"
                    else:
                        try:
                            sla_float = float(sla_text)
                            if sla_float <= 1.0:
                                return f"{sla_float * 100:.1f}"
                            else:
                                return f"{sla_float:.1f}"
                        except:
                            return "0.0"
                
                # Add Tier children with data mapping
                tier_type_value = get_row_value(row, 'tier_type')
                tier_type_mapped = "PROD" if tier_type_value == "PROD" else "nonPROD"
                add_tier_element(tier, "TierType", tier_type_mapped)
                
                database_value = get_row_value(row, 'database')
                database_type_mapped = "HANA as DB" if database_value == "HANA as DB" else "NONE"
                add_tier_element(tier, "DatabaseType", database_type_mapped)
                
                add_tier_element(tier, "DBSize", get_row_value(row, 'tenant__user_data_size'))
                
                add_requirements_value = get_row_value(row, 'add_requirements')
                add_tier_element(tier, "GxP", get_gxp_value(add_requirements_value))
                add_tier_element(tier, "HIPAA", get_hipaa_value(add_requirements_value))
                
                dr_value = get_row_value(row, 'dr')
                dr_mapped = "Y" if dr_value else "N"
                add_tier_element(tier, "DR", dr_mapped)
                add_tier_element(tier, "DRScenario", get_dr_scenario_value(dr_value))
                
                add_tier_element(tier, "SLA", format_sla_decimal(get_row_value(row, 'sla')))
                add_tier_element(tier, "AddSchemaCount", get_row_value(row, 'no_of_add_hana_nodes', "0"))
                
                hana_encryption_value = "Y" if database_value == "HANA as DB" else "N"
                add_tier_element(tier, "HanaEncryption", hana_encryption_value)
                add_tier_element(tier, "PhaseNo", get_row_value(row, 'phase', "1"))
                
                # Create Servers container
                servers_container = ET.SubElement(tier, "Servers")
                server_elem = ET.SubElement(servers_container, "Server")
                
                # Add Server children with ALL 29 columns for complete drilldown
                # This ensures all original data is preserved at the Server level
                
                # Column 1: amount
                add_tier_element(server_elem, "amount", get_row_value(row, 'amount'))
                
                # Column 2: system_name
                add_tier_element(server_elem, "system_name", get_row_value(row, 'system_name'))
                
                # Column 3: service (also in SolutionName, but preserved here for completeness)
                add_tier_element(server_elem, "service", get_row_value(row, 'service'))
                
                # Column 4: database (also in DatabaseType, but preserved here)
                add_tier_element(server_elem, "database", get_row_value(row, 'database'))
                
                # Column 5: tiername
                add_tier_element(server_elem, "tiername", get_row_value(row, 'tiername'))
                
                # Column 6: tier_type (also in TierType, but preserved here)
                add_tier_element(server_elem, "tier_type", get_row_value(row, 'tier_type'))
                
                # Column 7: system_id
                add_tier_element(server_elem, "system_id", get_row_value(row, 'system_id'))
                
                # Column 8: ram_gib (also as RAM)
                add_tier_element(server_elem, "ram_gib", get_row_value(row, 'ram_gib'))
                add_tier_element(server_elem, "RAM", get_row_value(row, 'ram_gib'))  # Keep RAM alias
                
                # Column 9: cpus_physvirt (also as CPU)
                add_tier_element(server_elem, "cpus_physvirt", get_row_value(row, 'cpus_physvirt'))
                add_tier_element(server_elem, "CPU", get_row_value(row, 'cpus_physvirt'))  # Keep CPU alias
                
                # Column 10: saps
                add_tier_element(server_elem, "saps", get_row_value(row, 'saps'))
                
                # Column 11: no_of_add_hana_nodes
                add_tier_element(server_elem, "no_of_add_hana_nodes", get_row_value(row, 'no_of_add_hana_nodes'))
                
                # Column 12: no_of_standby_nodes (also as Standby)
                add_tier_element(server_elem, "no_of_standby_nodes", get_row_value(row, 'no_of_standby_nodes'))
                add_tier_element(server_elem, "Standby", get_row_value(row, 'no_of_standby_nodes'))  # Keep Standby alias
                
                # Column 13: tenant__user_data_size (also in DBSize, but preserved here)
                add_tier_element(server_elem, "tenant__user_data_size", get_row_value(row, 'tenant__user_data_size'))
                
                # Column 14: amount_storage_1_gb
                add_tier_element(server_elem, "amount_storage_1_gb", get_row_value(row, 'amount_storage_1_gb'))
                
                # Column 15: iops1
                add_tier_element(server_elem, "iops1", get_row_value(row, 'iops1'))
                
                # Column 16: through_put1
                add_tier_element(server_elem, "through_put1", get_row_value(row, 'through_put1'))
                
                # Column 17: amount_storage_2_gb
                add_tier_element(server_elem, "amount_storage_2_gb", get_row_value(row, 'amount_storage_2_gb'))
                
                # Column 18: iops2
                add_tier_element(server_elem, "iops2", get_row_value(row, 'iops2'))
                
                # Column 19: through_put2
                add_tier_element(server_elem, "through_put2", get_row_value(row, 'through_put2'))
                
                # Column 20: storage_information_1
                add_tier_element(server_elem, "storage_information_1", get_row_value(row, 'storage_information_1'))
                
                # Column 21: backup_class (also as BackupClass)
                add_tier_element(server_elem, "backup_class", get_row_value(row, 'backup_class'))
                add_tier_element(server_elem, "BackupClass", get_row_value(row, 'backup_class'))  # Keep BackupClass alias
                
                # Column 22: os (also as OS)
                add_tier_element(server_elem, "os", get_row_value(row, 'os'))
                add_tier_element(server_elem, "OS", get_row_value(row, 'os'))  # Keep OS alias
                
                # Column 23: sla (also at Tier level, but preserved here)
                add_tier_element(server_elem, "sla", get_row_value(row, 'sla'))
                
                # Column 24: dr (also at Tier level, but preserved here)
                add_tier_element(server_elem, "dr", get_row_value(row, 'dr'))
                
                # Column 25: add_hw_for_dr
                add_tier_element(server_elem, "add_hw_for_dr", get_row_value(row, 'add_hw_for_dr'))
                
                # Column 26: pacemaker_included
                add_tier_element(server_elem, "pacemaker_included", get_row_value(row, 'pacemaker_included'))
                
                # Column 27: add_requirements (also as Additional)
                add_tier_element(server_elem, "add_requirements", get_row_value(row, 'add_requirements'))
                add_tier_element(server_elem, "Additional", get_row_value(row, 'add_requirements'))  # Keep Additional alias
                
                # Column 28: phase (also in PhaseNo, but preserved here)
                add_tier_element(server_elem, "phase", get_row_value(row, 'phase'))
                
                # Column 29: server
                add_tier_element(server_elem, "server", get_row_value(row, 'server'))
        
        # Convert to pretty XML string
        rough_string = ET.tostring(configuration_root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Clean up empty lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        pretty_xml = '\n'.join(lines)
        
        return pretty_xml
        
    except Exception as e:
        raise Exception(f"Error transforming to grouped tree: {str(e)}")

def extract_servers_from_grouped_tree(grouped_tree_xml):
    """
    Extract all servers with their 29 columns from grouped tree XML.
    Returns a DataFrame with all servers and their complete data.
    """
    try:
        root = ET.fromstring(grouped_tree_xml)
        servers_data = []
        
        # Helper function to get element text
        def get_element_text(elem, tag, default=""):
            child = elem.find(tag)
            if child is not None and child.text:
                return child.text.strip()
            return default
        
        # Iterate through all servers
        for solution in root.findall('.//Solution'):
            solution_name = get_element_text(solution, 'SolutionName', 'Unknown')
            
            for tier in solution.findall('.//Tier'):
                tier_type = get_element_text(tier, 'TierType', 'Unknown')
                database_type = get_element_text(tier, 'DatabaseType', 'Unknown')
                
                for server in tier.findall('.//Server'):
                    # Extract all 29 columns from Server element
                    server_row = {
                        'Solution': solution_name,
                        'TierType': tier_type,
                        'DatabaseType': database_type,
                        'amount': get_element_text(server, 'amount'),
                        'system_name': get_element_text(server, 'system_name'),
                        'service': get_element_text(server, 'service'),
                        'database': get_element_text(server, 'database'),
                        'tiername': get_element_text(server, 'tiername'),
                        'tier_type': get_element_text(server, 'tier_type'),
                        'system_id': get_element_text(server, 'system_id'),
                        'ram_gib': get_element_text(server, 'ram_gib'),
                        'cpus_physvirt': get_element_text(server, 'cpus_physvirt'),
                        'saps': get_element_text(server, 'saps'),
                        'no_of_add_hana_nodes': get_element_text(server, 'no_of_add_hana_nodes'),
                        'no_of_standby_nodes': get_element_text(server, 'no_of_standby_nodes'),
                        'tenant__user_data_size': get_element_text(server, 'tenant__user_data_size'),
                        'amount_storage_1_gb': get_element_text(server, 'amount_storage_1_gb'),
                        'iops1': get_element_text(server, 'iops1'),
                        'through_put1': get_element_text(server, 'through_put1'),
                        'amount_storage_2_gb': get_element_text(server, 'amount_storage_2_gb'),
                        'iops2': get_element_text(server, 'iops2'),
                        'through_put2': get_element_text(server, 'through_put2'),
                        'storage_information_1': get_element_text(server, 'storage_information_1'),
                        'backup_class': get_element_text(server, 'backup_class'),
                        'os': get_element_text(server, 'os'),
                        'sla': get_element_text(server, 'sla'),
                        'dr': get_element_text(server, 'dr'),
                        'add_hw_for_dr': get_element_text(server, 'add_hw_for_dr'),
                        'pacemaker_included': get_element_text(server, 'pacemaker_included'),
                        'add_requirements': get_element_text(server, 'add_requirements'),
                        'phase': get_element_text(server, 'phase'),
                        'server': get_element_text(server, 'server'),
                    }
                    servers_data.append(server_row)
        
        if servers_data:
            df = pd.DataFrame(servers_data)
            return df
        else:
            return pd.DataFrame(columns=['Solution', 'TierType', 'DatabaseType'] + COLUMN_STRUCTURE)
            
    except Exception as e:
        st.error(f"Error extracting servers: {str(e)}")
        return pd.DataFrame()

def display_29_column_table(df):
    """Display the 29-column DataFrame as an interactive table."""
    st.markdown("### 📊 29-Column Structured Data Table")
    st.markdown(f"**Total Rows:** {len(df)}")
    
    # Display the table
    st.dataframe(
        df,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # Add download options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = dataframe_to_csv(df)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="29_column_output.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = dataframe_to_json(df)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_data,
            file_name="29_column_output.json",
            mime="application/json"
        )
    
    with col3:
        xml_data = dataframe_to_xml(df)
        st.download_button(
            label="⬇️ Download XML",
            data=xml_data,
            file_name="29_column_output.xml",
            mime="application/xml"
        )

def load_documentation(file_name):
    """Load documentation from docs folder."""
    docs_path = os.path.join(os.path.dirname(__file__), 'docs', file_name)
    if os.path.exists(docs_path):
        with open(docs_path, 'r', encoding='utf-8') as f:
            return f.read()
    return f"Documentation file '{file_name}' not found."

def render_executive_summary():
    """Render the Executive Summary section with key metrics and status."""
    with st.expander("📊 Executive Summary", expanded=True):
        # Initialize session state for statistics if not exists
        if 'processing_stats' not in st.session_state:
            st.session_state.processing_stats = {
                'total_processed': 0,
                'total_tables_extracted': 0,
                'total_rows_structured': 0,
                'last_processed': None,
                'avg_processing_time': 0
            }
        
        # Get current status (lazy-load SAP client - don't block page load)
        # Only check credentials, don't initialize client on every page load
        is_valid, cred_message = validate_sap_credentials()
        # Don't initialize SAP client here - it's slow and blocks page load
        # Will be initialized when actually needed (when processing PDFs)
        sap_client = None
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # System Status
            st.markdown("### 🔌 System Status")
            if is_valid:
                st.success("✅ **Operational**")
                st.caption("AI services connected")
            else:
                st.warning("⚠️ **Limited**")
                st.caption("Check credentials")
        
        with col2:
            # Processing Statistics
            st.markdown("### 📈 Processing Stats")
            total_processed = st.session_state.processing_stats['total_processed']
            st.metric("Documents Processed", total_processed)
            if total_processed > 0:
                st.caption(f"Last: {st.session_state.processing_stats.get('last_processed', 'N/A')}")
        
        with col3:
            # Data Extraction Stats
            st.markdown("### 📊 Data Extraction")
            total_tables = st.session_state.processing_stats['total_tables_extracted']
            total_rows = st.session_state.processing_stats['total_rows_structured']
            st.metric("Tables Extracted", total_tables)
            if total_tables > 0:
                st.caption(f"{total_rows} rows structured")
        
        with col4:
            # Performance Metrics
            st.markdown("### ⚡ Performance")
            use_parallel = st.session_state.get('use_parallel', True)
            max_workers = st.session_state.get('max_workers', 3)
            if use_parallel:
                st.info(f"**Parallel Mode**")
                st.caption(f"{max_workers} workers active")
            else:
                st.info("**Sequential Mode**")
                st.caption("Single-threaded")
        
        st.divider()
        
        # Current Session Summary
        col_summary1, col_summary2 = st.columns(2)
        
        with col_summary1:
            st.markdown("### 🎯 Current Session")
            if st.session_state.get('structured_df') is not None:
                df = st.session_state.structured_df
                st.success("✅ **Active Processing**")
                st.markdown(f"""
                - **File**: {st.session_state.get('processed_filename', 'N/A')}
                - **Rows**: {len(df)}
                - **Columns**: {len(COLUMN_STRUCTURE)}
                - **Status**: Ready for export
                """)
            else:
                st.info("📄 **No active session**")
                st.caption("Upload a PDF to begin")
        
        with col_summary2:
            st.markdown("### 🚀 Quick Actions")
            action_col1, action_col2 = st.columns(2)
            
            with action_col1:
                if st.button("📖 Documentation", use_container_width=True, key="exec_docs"):
                    st.session_state.nav_to_docs = True
                    st.rerun()
            
            with action_col2:
                if st.button("🔌 Test Connection", use_container_width=True, key="exec_test"):
                    st.session_state.test_connection = True
                if st.button("📊 View Stats", use_container_width=True, key="exec_stats"):
                    st.session_state.show_detailed_stats = not st.session_state.get('show_detailed_stats', False)
                    st.rerun()
        
        # Detailed Statistics (if requested)
        if st.session_state.get('show_detailed_stats', False):
            st.divider()
            st.markdown("### 📊 Detailed Statistics")
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                st.markdown("**Processing History**")
                stats = st.session_state.processing_stats
                st.json({
                    "Total Documents": stats['total_processed'],
                    "Total Tables": stats['total_tables_extracted'],
                    "Total Rows": stats['total_rows_structured'],
                    "Last Processed": stats.get('last_processed', 'Never')
                })
            
            with stats_col2:
                st.markdown("**System Configuration**")
                st.json({
                    "Parallel Processing": st.session_state.get('use_parallel', True),
                    "Max Workers": st.session_state.get('max_workers', 3),
                    "Credentials Status": "Valid" if is_valid else "Invalid",
                    "AI Client": "Will connect when processing" if is_valid else "Not Configured"
                })
            
            with stats_col3:
                st.markdown("**Application Info**")
                st.json({
                    "Version": "1.0.0",
                    "AI Provider": "SAP Cloud SDK for AI (generative)",
                    "Table Extraction": "Camelot",
                    "Output Formats": ["CSV", "JSON", "XML"]
                })
            
            if st.button("Close Detailed Stats", key="close_stats"):
                st.session_state.show_detailed_stats = False
                st.rerun()
        
        # Key Capabilities Summary
        st.divider()
        st.markdown("### 💡 Key Capabilities")
        
        cap_col1, cap_col2, cap_col3 = st.columns(3)
        
        with cap_col1:
            st.markdown("""
            **📄 PDF Processing**
            - Multi-table extraction
            - Page selection
            - Lattice & Stream modes
            """)
        
        with cap_col2:
            st.markdown("""
            **🤖 AI-Powered Structuring**
            - 29-column standardization
            - Intelligent data mapping
            - Parallel processing
            """)
        
        with cap_col3:
            st.markdown("""
            **🌳 Tree Transformation**
            - Hierarchical grouping
            - Solution/Tier/Server structure
            - Multiple export formats
            """)

def get_ai_assistant_context():
    """Get context about the application for AI Assistant."""
    try:
        user_guide = load_documentation('user_guide.md')
    except Exception as e:
        print(f"Warning: Could not load user_guide.md: {str(e)}")
        user_guide = "User guide not available."
    
    try:
        faq = load_documentation('faq.md')
    except Exception as e:
        print(f"Warning: Could not load faq.md: {str(e)}")
        faq = "FAQ not available."
    
    try:
        troubleshooting = load_documentation('troubleshooting_guide.md')
    except Exception as e:
        print(f"Warning: Could not load troubleshooting_guide.md: {str(e)}")
        troubleshooting = "Troubleshooting guide not available."
    
    try:
        walkthrough = load_documentation('walkthrough_case_study.md')
    except Exception as e:
        print(f"Warning: Could not load walkthrough_case_study.md: {str(e)}")
        walkthrough = "Walkthrough not available."
    
    context = f"""
    You are an AI Assistant for the PDF to Grouped Tree Structure Extractor application.
    
    Application Overview:
    - This application extracts tables from PDF documents
    - Uses Camelot library for table extraction
    - Uses SAP Cloud SDK for AI (generative) with models like GPT-4o for data structuring
    - Maps extracted data to a standardized 29-column format
    - Transforms data into a hierarchical grouped tree structure (Solution/Tier/Server)
    - Supports multiple export formats: CSV, JSON, XML
    
    Key Features:
    - PDF table extraction with Lattice and Stream flavors
    - AI-powered data mapping to 29-column structure
    - Grouped tree transformation (Configuration → Solutions → Tiers → Servers)
    - Multiple export formats
    - Filtering capabilities
    
    29-Column Structure:
    amount, system_name, service, database, tiername, tier_type,
    system_id, ram_gib, cpus_physvirt, saps,
    no_of_add_hana_nodes, no_of_standby_nodes, tenant__user_data_size,
    amount_storage_1_gb, iops1, through_put1,
    amount_storage_2_gb, iops2, through_put2,
    storage_information_1, backup_class, os, sla, dr,
    add_hw_for_dr, pacemaker_included, add_requirements, phase, server
    
    Documentation Context:
    
    USER GUIDE SUMMARY:
    {user_guide[:2000]}
    
    FAQ SUMMARY:
    {faq[:2000]}
    
    TROUBLESHOOTING SUMMARY:
    {troubleshooting[:2000]}
    
    WALKTHROUGH SUMMARY:
    {walkthrough[:2000]}
    
    Answer questions about the application based on this context. Be helpful, accurate, and concise.
    If you don't know something, say so rather than guessing.
    """
    return context

def render_ai_assistant():
    """Render the AI Assistant interface."""
    try:
        st.markdown("# 🤖 AI Assistant")
        st.markdown("---")
        st.markdown("""
        Ask me anything about the PDF to Grouped Tree Structure Extractor application!
        
        I can help you with:
        - How to use the application
        - Understanding features and workflows
        - Troubleshooting issues
        - Configuration and setup
        - Best practices
        - And more!
        """)
        
        # Check if SAP client is available
        try:
            sap_client = get_sap_gen_ai_client()
        except Exception as e:
            st.error(f"⚠️ Error initializing SAP Cloud SDK for AI client: {str(e)}")
            st.info("💡 Tip: Use the 'Test Connection' button in the sidebar to verify your SAP Cloud SDK for AI setup.")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
            return
        
        if not sap_client:
            st.error("⚠️ AI Assistant requires SAP Cloud SDK for AI connection. Please configure credentials and test connection.")
            st.info("💡 Tip: Use the 'Test Connection' button in the sidebar to verify your SAP Cloud SDK for AI setup.")
            return
        
        # Initialize chat history
        if 'ai_assistant_history' not in st.session_state:
            st.session_state.ai_assistant_history = []
        
        # Check for pending query from example buttons (process immediately before displaying)
        processing_query = False
        print(f"[CP2] CHECKPOINT 2: Checking for pending query. ai_pending_query in session_state: {'ai_pending_query' in st.session_state}")
        if 'ai_pending_query' in st.session_state:
            print(f"[CP2] CHECKPOINT 2: ai_pending_query value: '{st.session_state.ai_pending_query}'")
        if 'ai_pending_query' in st.session_state and st.session_state.ai_pending_query:
            print("[CP2-DETECTED] CHECKPOINT 2: Pending query DETECTED!")
            pending_query = st.session_state.ai_pending_query
            print(f"[CP2-DETECTED] CHECKPOINT 2: Extracted pending_query = '{pending_query}'")
            st.session_state.ai_pending_query = None  # Clear it immediately
            print("[CP2-DETECTED] CHECKPOINT 2: Cleared ai_pending_query from session_state")
            processing_query = True
            print(f"[CP2-DETECTED] CHECKPOINT 2: Set processing_query = {processing_query}")
            
            # Process the pending query
            if pending_query:
                print("[CP3] CHECKPOINT 3: Starting query processing")
                print(f"[CP3] CHECKPOINT 3: Processing query: '{pending_query}'")
                
                # Add user message to history
                st.session_state.ai_assistant_history.append(("user", pending_query))
                print(f"[CP3] CHECKPOINT 3: Added user message to history. History length: {len(st.session_state.ai_assistant_history)}")
                
                # Process query and get response
                try:
                    print("[CP3] CHECKPOINT 3: Getting AI context...")
                    # Get context
                    context = get_ai_assistant_context()
                    print(f"[CP3] CHECKPOINT 3: Context loaded. Length: {len(context)} characters")
                    
                    print("[CP3] CHECKPOINT 3: Getting deployments...")
                    # Get deployments and select model
                    deployments = sap_client.get_deployments()
                    print(f"[CP3] CHECKPOINT 3: Found {len(deployments)} deployments")
                    preferred_models = ['gpt-4o', 'gpt-4', 'gpt-4.1', 'anthropic--claude-3.5-sonnet', 'anthropic--claude-4.5-sonnet', 'gpt-5']
                    selected_model = None
                    selected_deployment = None
                    
                    for model_name in preferred_models:
                        for dep in deployments:
                            if dep.model_name == model_name:
                                selected_model = model_name
                                selected_deployment = dep
                                break
                        if selected_deployment:
                            break
                    
                    print(f"[CP3] CHECKPOINT 3: Selected model: {selected_model}, Deployment ID: {selected_deployment.deployment_id if selected_deployment else 'None'}")
                    
                    if selected_deployment:
                        print("[CP3] CHECKPOINT 3: Creating chat model...")
                        # Create chat model
                        chat_model = ChatOpenAI(
                            model_name=selected_model,
                            deployment_id=selected_deployment.deployment_id,
                            temperature=0.3,
                            max_tokens=2000
                        )
                        print("[CP3] CHECKPOINT 3: Chat model created successfully")
                        
                        print("[CP3] CHECKPOINT 3: Building conversation messages...")
                        # Build conversation history for context
                        conversation_messages = [SystemMessage(content=context)]
                        
                        # Add recent conversation history (excluding the just-added user message)
                        recent_history = st.session_state.ai_assistant_history[:-1] if len(st.session_state.ai_assistant_history) > 1 else []
                        print(f"[CP3] CHECKPOINT 3: Adding {len(recent_history)} recent messages to context")
                        for role, message in recent_history[-10:]:
                            if role == "user":
                                conversation_messages.append(HumanMessage(content=message))
                            elif role == "assistant":
                                conversation_messages.append(AIMessage(content=message))
                        
                        # Add current query
                        conversation_messages.append(HumanMessage(content=pending_query))
                        print(f"[CP3] CHECKPOINT 3: Total messages in conversation: {len(conversation_messages)}")
                        
                        print("[CP3] CHECKPOINT 3: Invoking AI model...")
                        # Get response
                        response = chat_model.invoke(conversation_messages)
                        print("[CP3] CHECKPOINT 3: AI response received!")
                        
                        # Extract content
                        if hasattr(response, 'content'):
                            answer = response.content.strip()
                            print(f"[CP3] CHECKPOINT 3: Extracted answer. Length: {len(answer)} characters")
                            print(f"[CP3] CHECKPOINT 3: Answer preview: {answer[:100]}...")
                        else:
                            answer = str(response).strip()
                            print(f"[CP3] CHECKPOINT 3: Extracted answer (string conversion). Length: {len(answer)} characters")
                        
                        # Add to history
                        st.session_state.ai_assistant_history.append(("assistant", answer))
                        print(f"[CP3] CHECKPOINT 3: Added assistant response to history. History length: {len(st.session_state.ai_assistant_history)}")
                        print(f"[CP3] CHECKPOINT 3: Full history: {st.session_state.ai_assistant_history}")
                    else:
                        error_msg = "No suitable AI model deployment found."
                        print(f"[CP3] CHECKPOINT 3: ERROR - {error_msg}")
                        st.session_state.ai_assistant_history.append(("assistant", f"Error: {error_msg}"))
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    print(f"[CP3] CHECKPOINT 3: EXCEPTION - {error_msg}")
                    import traceback
                    print(f"[CP3] CHECKPOINT 3: Traceback:\n{traceback.format_exc()}")
                    st.session_state.ai_assistant_history.append(("assistant", f"Error: {error_msg}"))
                    st.session_state.ai_error = traceback.format_exc()
                
                print("[CP3] CHECKPOINT 3: Processing complete. History updated.")
                print(f"[CP3] CHECKPOINT 3: History length: {len(st.session_state.ai_assistant_history)} messages")
                # Rerun to display the new messages (display code will run after rerun)
                # Ensure we stay on documentation page and AI Assistant tab
                st.session_state.nav_to_docs = True
                st.session_state.doc_tab = 5  # AI Assistant tab
                st.rerun()
            else:
                print("[CP3] CHECKPOINT 3: WARNING - pending_query is empty!")
        
        # Display chat history (after processing pending queries)
        st.markdown("### 💬 Conversation")
        print(f"[CP4] CHECKPOINT 4: Displaying chat history. History length: {len(st.session_state.ai_assistant_history)}")
        
        if not st.session_state.ai_assistant_history:
            print("[CP4] CHECKPOINT 4: No chat history - showing empty state")
            st.info("👋 Start a conversation by asking a question or clicking an example question below.")
        else:
            print(f"[CP4] CHECKPOINT 4: Rendering {len(st.session_state.ai_assistant_history)} messages")
            print(f"[CP4] CHECKPOINT 4: Full history structure: {st.session_state.ai_assistant_history}")
            # Display all messages in chat history
            for i, (role, message) in enumerate(st.session_state.ai_assistant_history):
                print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Role: '{role}', Type: {type(role)}")
                print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Message type: {type(message)}, Length: {len(str(message)) if message else 0}")
                print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Message preview: {str(message)[:150] if message else 'None'}")
                try:
                    if role == "user":
                        print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Creating user chat message...")
                        with st.chat_message("user"):
                            print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Writing user message content...")
                            st.write(message)
                        print(f"[CP4] CHECKPOINT 4: [Message {i+1}] [OK] User message displayed successfully")
                    else:
                        print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Creating assistant chat message...")
                    with st.chat_message("assistant"):
                        if message and isinstance(message, str) and message.startswith("Error:"):
                            print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Displaying error message")
                            st.error(message)
                            if 'ai_error' in st.session_state:
                                with st.expander("Error Details"):
                                    st.code(st.session_state.ai_error)
                        else:
                            if message:
                                print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Writing assistant message content...")
                                st.write(message)
                                print(f"[CP4] CHECKPOINT 4: [Message {i+1}] [OK] Assistant message displayed successfully")
                            else:
                                print(f"[CP4] CHECKPOINT 4: [Message {i+1}] [WARN] Empty message detected!")
                                st.warning("Empty response received")
                except Exception as e:
                    print(f"[CP4] CHECKPOINT 4: [Message {i+1}] [ERROR] EXCEPTION: {str(e)}")
                    import traceback
                    print(f"[CP4] CHECKPOINT 4: [Message {i+1}] Full traceback:\n{traceback.format_exc()}")
                    st.error(f"Error displaying message {i+1}: {str(e)}")
            print("[CP4] CHECKPOINT 4: [OK] Finished displaying all messages")
        
        # Chat input
        user_query = st.chat_input("Ask a question about the application...")
        
        if user_query:
            # Add user message to history
            st.session_state.ai_assistant_history.append(("user", user_query))
            
            # Show user message immediately
            with st.chat_message("user"):
                st.write(user_query)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Get context
                        context = get_ai_assistant_context()
                        
                        # Get deployments and select model
                        deployments = sap_client.get_deployments()
                        preferred_models = ['gpt-4o', 'gpt-4', 'gpt-4.1', 'anthropic--claude-3.5-sonnet', 'anthropic--claude-4.5-sonnet', 'gpt-5']
                        selected_model = None
                        selected_deployment = None
                        
                        for model_name in preferred_models:
                            for dep in deployments:
                                if dep.model_name == model_name:
                                    selected_model = model_name
                                    selected_deployment = dep
                                    break
                            if selected_deployment:
                                break
                        
                        if not selected_deployment:
                            error_msg = "No suitable AI model deployment found. Please check your SAP Cloud SDK for AI configuration."
                            st.error(error_msg)
                            st.session_state.ai_assistant_history.append(("assistant", f"Error: {error_msg}"))
                            st.rerun()
                            return
                        
                        # Create chat model
                        chat_model = ChatOpenAI(
                            model_name=selected_model,
                            deployment_id=selected_deployment.deployment_id,
                            temperature=0.3,
                            max_tokens=2000
                        )
                        
                        # Build conversation history for context
                        conversation_messages = [SystemMessage(content=context)]
                        
                        # Add recent conversation history (skip the last user message as we'll add it)
                        recent_history = st.session_state.ai_assistant_history[:-1] if len(st.session_state.ai_assistant_history) > 1 else []
                        for role, message in recent_history[-10:]:
                            if role == "user":
                                conversation_messages.append(HumanMessage(content=message))
                            elif role == "assistant":
                                conversation_messages.append(AIMessage(content=message))
                        
                        # Add current query
                        conversation_messages.append(HumanMessage(content=user_query))
                        
                        # Get response
                        response = chat_model.invoke(conversation_messages)
                        
                        # Extract content
                        if hasattr(response, 'content'):
                            answer = response.content.strip()
                        else:
                            answer = str(response).strip()
                        
                        # Display answer
                        st.write(answer)
                        
                        # Add to history
                        st.session_state.ai_assistant_history.append(("assistant", answer))
                        
                        # Rerun to update the display
                        st.rerun()
                        
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.info("Please try again or check your SAP Cloud SDK for AI connection.")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
                        st.session_state.ai_assistant_history.append(("assistant", f"Error: {error_msg}"))
                        st.rerun()
        
        # Clear chat button
        if st.session_state.ai_assistant_history:
            st.divider()
            if st.button("🗑️ Clear Conversation", use_container_width=True):
                st.session_state.ai_assistant_history = []
                st.rerun()
        
        # Example questions
        st.divider()
        st.markdown("### 💡 Example Questions")
        example_cols = st.columns(2)
        
        with example_cols[0]:
            if st.button("❓ How do I extract tables?", use_container_width=True):
                print("[CP1] CHECKPOINT 1: Button clicked - 'How do I extract tables?'")
                st.session_state.ai_pending_query = "How do I extract tables from a PDF?"
                st.session_state.nav_to_docs = True
                st.session_state.doc_tab = 5  # AI Assistant tab
                print(f"[CP1] CHECKPOINT 1: Set ai_pending_query = '{st.session_state.ai_pending_query}'")
                st.rerun()
            if st.button("❓ What are the 29 columns?", use_container_width=True):
                print("[CP1] CHECKPOINT 1: Button clicked - 'What are the 29 columns?'")
                st.session_state.ai_pending_query = "What are the 29 columns in the output?"
                st.session_state.nav_to_docs = True
                st.session_state.doc_tab = 5  # AI Assistant tab
                print(f"[CP1] CHECKPOINT 1: Set ai_pending_query = '{st.session_state.ai_pending_query}'")
                st.rerun()
            if st.button("❓ How does grouped tree work?", use_container_width=True):
                print("[CP1] CHECKPOINT 1: Button clicked - 'How does grouped tree work?'")
                st.session_state.ai_pending_query = "How does the grouped tree structure work?"
                st.session_state.nav_to_docs = True
                st.session_state.doc_tab = 5  # AI Assistant tab
                print(f"[CP1] CHECKPOINT 1: Set ai_pending_query = '{st.session_state.ai_pending_query}'")
                st.rerun()
        
        with example_cols[1]:
            if st.button("❓ No tables found?", use_container_width=True):
                print("[CP1] CHECKPOINT 1: Button clicked - 'No tables found?'")
                st.session_state.ai_pending_query = "What should I do if no tables are found in my PDF?"
                st.session_state.nav_to_docs = True
                st.session_state.doc_tab = 5  # AI Assistant tab
                print(f"[CP1] CHECKPOINT 1: Set ai_pending_query = '{st.session_state.ai_pending_query}'")
                st.rerun()
            if st.button("❓ Configure credentials?", use_container_width=True):
                print("[CP1] CHECKPOINT 1: Button clicked - 'Configure credentials?'")
                st.session_state.ai_pending_query = "How do I configure SAP Cloud SDK for AI credentials?"
                st.session_state.nav_to_docs = True
                st.session_state.doc_tab = 5  # AI Assistant tab
                print(f"[CP1] CHECKPOINT 1: Set ai_pending_query = '{st.session_state.ai_pending_query}'")
                st.rerun()
            if st.button("❓ Export formats?", use_container_width=True):
                print("[CP1] CHECKPOINT 1: Button clicked - 'Export formats?'")
                st.session_state.ai_pending_query = "What export formats are available and when should I use each?"
                st.session_state.nav_to_docs = True
                st.session_state.doc_tab = 5  # AI Assistant tab
                print(f"[CP1] CHECKPOINT 1: Set ai_pending_query = '{st.session_state.ai_pending_query}'")
                st.rerun()
    
    except Exception as e:
            st.error(f"⚠️ Error loading AI Assistant: {str(e)}")
            st.info("Please check your configuration and try again. If the problem persists, check the error details below.")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

def render_documentation_page():
    """Render the documentation page with tabs for different documents."""
    st.title("📚 Documentation Center")
    st.markdown("""
    Welcome to the Documentation Center. Select a document from the tabs below to access user guides, 
    training materials, FAQs, and troubleshooting information.
    """)
    
    # Create tabs for different documentation sections
    doc_tabs = st.tabs([
        "📖 User Guide",
        "🎓 Training Manual", 
        "❓ FAQ",
        "🔧 Troubleshooting Guide",
        "🚶 Walkthrough"
    ])
    
    with doc_tabs[0]:
        st.markdown("# 📖 User Guide")
        st.markdown("---")
        user_guide = load_documentation('user_guide.md')
        st.markdown(user_guide)
        
        # Download button for User Guide
        st.download_button(
            label="⬇️ Download User Guide (Markdown)",
            data=user_guide,
            file_name="user_guide.md",
            mime="text/markdown"
        )
    
    with doc_tabs[1]:
        st.markdown("# 🎓 Training Manual")
        st.markdown("---")
        training_manual = load_documentation('training_manual.md')
        st.markdown(training_manual)
        
        # Download button for Training Manual
        st.download_button(
            label="⬇️ Download Training Manual (Markdown)",
            data=training_manual,
            file_name="training_manual.md",
            mime="text/markdown"
        )
    
    with doc_tabs[2]:
        st.markdown("# ❓ Frequently Asked Questions (FAQ)")
        st.markdown("---")
        faq = load_documentation('faq.md')
        st.markdown(faq)
        
        # Download button for FAQ
        st.download_button(
            label="⬇️ Download FAQ (Markdown)",
            data=faq,
            file_name="faq.md",
            mime="text/markdown"
        )
    
    with doc_tabs[3]:
        st.markdown("# 🔧 Troubleshooting Guide")
        st.markdown("---")
        troubleshooting = load_documentation('troubleshooting_guide.md')
        st.markdown(troubleshooting)
        
        # Download button for Troubleshooting Guide
        st.download_button(
            label="⬇️ Download Troubleshooting Guide (Markdown)",
            data=troubleshooting,
            file_name="troubleshooting_guide.md",
            mime="text/markdown"
        )
    
    with doc_tabs[4]:
        st.markdown("# 🚶 User Walkthrough - Case Study")
        st.markdown("---")
        st.markdown("""
        ### QT_real_sample.pdf Case Study
        
        This walkthrough provides a complete step-by-step guide using a real-world PDF document as an example.
        Follow along to learn the complete workflow from PDF upload to final export.
        """)
        walkthrough = load_documentation('walkthrough_case_study.md')
        st.markdown(walkthrough)
        
        # Download button for Walkthrough
        st.download_button(
            label="⬇️ Download Walkthrough (Markdown)",
            data=walkthrough,
            file_name="walkthrough_case_study.md",
            mime="text/markdown"
        )
    
    # Quick links section
    st.divider()
    st.markdown("### 🔗 Quick Links")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("**📖 [User Guide](#user-guide)**")
    with col2:
        st.markdown("**🎓 [Training](#training-manual)**")
    with col3:
        st.markdown("**❓ [FAQ](#faq)**")
    with col4:
        st.markdown("**🔧 [Troubleshooting](#troubleshooting)**")
    with col5:
        st.markdown("**🚶 [Walkthrough](#walkthrough)**")

def main():
    # Main navigation - choose between App and Documentation
    # Check if user wants to navigate to docs
    if 'nav_to_docs' in st.session_state and st.session_state.nav_to_docs:
        st.session_state.nav_to_docs = False
        page = "📚 Documentation"
    else:
        # Initialize page state if not set
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Main Application"
        
        page = st.sidebar.selectbox(
            "📑 Navigation",
            ["🏠 Main Application", "📚 Documentation"],
            index=1 if st.session_state.current_page == "📚 Documentation" else 0
        )
        st.session_state.current_page = page
    
    if page == "📚 Documentation":
        render_documentation_page()
        return
    
    # Main application page
    st.title("📄 PDF → Grouped Tree Structure Extractor")
    
    # Executive Summary Section
    render_executive_summary()
    
    st.markdown("""
    **Two-Step Process**: Extract PDF tables → Transform to grouped tree structure for validation
    
    This app extracts tables from PDFs and creates a standardized grouped tree structure:
    - **Step 1**: Uses **Camelot** + **SAP Cloud SDK for AI (generative)** (GPT-4o or other available model, or OpenAI) to extract and structure data to 29-column format
    - **Step 2**: Transforms raw XML into grouped tree structure (Solution/Tier/Server hierarchy)
    - **Output**: Grouped tree XML ready for GDO validation and comparison
    """)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Documentation link
        st.markdown("---")
        st.markdown("### 📚 Documentation")
        if st.button("📖 Open Documentation Center", use_container_width=True):
            st.session_state.nav_to_docs = True
        
        st.markdown("---")
        
        # SAP Cloud SDK for AI Connection Test
        st.subheader("🔌 SAP Cloud SDK for AI")
        if st.button("Test Connection", use_container_width=True):
            with st.spinner("Testing connection to SAP Cloud SDK for AI (generative)..."):
                success, message, details = test_sap_gen_ai_hub_connection()
                if success:
                    st.success(message)
                else:
                    st.error(message)
                
                # Show details in expander
                with st.expander("Connection Details"):
                    st.json(details)
        
        # Show credential status
        is_valid, cred_message = validate_sap_credentials()
        if is_valid:
            st.success("✅ SAP credentials configured")
        else:
            st.warning(f"⚠️ {cred_message}")
        
        st.divider()
        
        st.header("📄 PDF Extraction")
        pages_input = st.text_input("Pages to extract", value="all", help="e.g., 'all', '1-4', '1,2,3'")
        flavor_option = st.selectbox("Camelot Flavor", ["lattice", "stream"], help="lattice for tables with lines, stream for tables without")
        
        st.divider()
        
        st.header("⚡ Performance")
        use_parallel = st.checkbox("Enable Parallel Processing", value=True, help="Process multiple tables simultaneously for faster execution")
        max_workers = st.slider("Max Parallel Workers", min_value=1, max_value=5, value=3, help="Number of parallel AI processing threads (1-5)")
        if use_parallel:
            st.info(f"⚡ Parallel mode: Up to {max_workers} tables processed simultaneously")
        else:
            st.info("🐌 Sequential mode: Tables processed one at a time")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        help="Select a PDF file containing tables to extract"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📎 File uploaded: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
        
        # Initialize session state
        if 'structured_df' not in st.session_state:
            st.session_state.structured_df = None
        if 'tables_extracted' not in st.session_state:
            st.session_state.tables_extracted = None
        if 'processed_filename' not in st.session_state:
            st.session_state.processed_filename = None
        if 'raw_xml' not in st.session_state:
            st.session_state.raw_xml = None
        if 'grouped_tree_xml' not in st.session_state:
            st.session_state.grouped_tree_xml = None
        
        # Process button
        if st.button("🔄 Extract & Structure Data", type="primary", use_container_width=True):
            # Lazy-load SAP client only when actually needed (not on page load)
            sap_client = get_sap_gen_ai_client()
            if not sap_client:
                st.error("Cannot process PDF: No AI client configured. Please configure SAP Cloud SDK for AI credentials or OpenAI API key.")
                return
            
            # Step 1: Extract tables with Camelot
            with st.spinner("📊 Step 1/2: Extracting tables from PDF using Camelot..."):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Parse pages input
                    pages = pages_input if pages_input.lower() != "all" else "all"
                    
                    tables, tmp_path = extract_tables_with_camelot(uploaded_file, pages=pages, flavor=flavor_option)
                    
                    if not tables:
                        st.error("❌ No tables found in the PDF. Please check if the PDF contains tables.")
                        return
                    
                    st.success(f"✅ Extracted {len(tables)} table(s) from PDF")
                    st.session_state.tables_extracted = tables
                    
                    # Show table extraction summary
                    with st.expander("📋 Table Extraction Summary"):
                        for i, table in enumerate(tables):
                            st.write(f"**Table {i+1}** (Page {table.page}): {len(table.df)} rows × {len(table.df.columns)} columns")
                    
                except Exception as e:
                    st.error(f"❌ Error extracting tables: {str(e)}")
                    import traceback
                    with st.expander("Debug Info"):
                        st.code(traceback.format_exc())
                    return
                finally:
                    # Clean up temp file
                    try:
                        if 'tmp_path' in locals() and os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                    except:
                        pass
            
            # Step 2: Structure data with SAP Cloud SDK for AI (generative) (GPT-4o or other model) or OpenAI
            # Lazy-load SAP client only when actually needed (not on page load)
            sap_client = get_sap_gen_ai_client()
            ai_provider = "SAP Cloud SDK for AI" if sap_client else "OpenAI"
            use_parallel = st.session_state.get('use_parallel', True)
            max_workers = st.session_state.get('max_workers', 3)
            num_tables = len(st.session_state.tables_extracted) if st.session_state.tables_extracted else 0
            
            if use_parallel and num_tables > 1:
                spinner_text = f"🤖 Step 2/3: Structuring {num_tables} tables in parallel using {ai_provider} (up to {max_workers} workers)..."
            else:
                spinner_text = f"🤖 Step 2/3: Structuring data to 29-column format using {ai_provider}..."
            
            with st.spinner(spinner_text):
                try:
                    if sap_client:
                        structured_data = structure_data_with_sap_gen_ai(
                            sap_client, 
                            st.session_state.tables_extracted, 
                            COLUMN_STRUCTURE,
                            use_parallel=use_parallel,
                            max_workers=max_workers
                        )
                    else:
                        st.error("❌ No AI client available. Please configure SAP Cloud SDK for AI credentials or OpenAI API key.")
                        return
                    
                    if not structured_data:
                        st.warning(f"⚠️ No structured data returned from {ai_provider}. Please check the PDF content.")
                        return
                    
                    # Create DataFrame with 29 columns
                    df = create_29_column_dataframe(structured_data)
                    st.session_state.structured_df = df
                    st.session_state.processed_filename = uploaded_file.name
                    
                    # Update processing statistics
                    if 'processing_stats' not in st.session_state:
                        st.session_state.processing_stats = {
                            'total_processed': 0,
                            'total_tables_extracted': 0,
                            'total_rows_structured': 0,
                            'last_processed': None
                        }
                    
                    st.session_state.processing_stats['total_processed'] += 1
                    st.session_state.processing_stats['total_tables_extracted'] += len(st.session_state.tables_extracted) if st.session_state.tables_extracted else 0
                    st.session_state.processing_stats['total_rows_structured'] += len(df)
                    st.session_state.processing_stats['last_processed'] = uploaded_file.name
                    
                    st.success(f"✅ Structured {len(df)} row(s) into 29-column format")
                    
                except Exception as e:
                    st.error(f"❌ Error structuring data: {str(e)}")
                    import traceback
                    with st.expander("Debug Info"):
                        st.code(traceback.format_exc())
                    return
            
            # Step 3: Generate raw XML (step 1 output) and transform to grouped tree (step 2)
            with st.spinner("🌳 Step 3/3: Generating grouped tree structure (Solution/Tier/Server)..."):
                try:
                    # Generate raw XML from DataFrame
                    raw_xml = dataframe_to_xml(st.session_state.structured_df)
                    st.session_state.raw_xml = raw_xml
                    
                    # Transform to grouped tree structure
                    grouped_tree_xml = transform_to_grouped_tree(raw_xml)
                    st.session_state.grouped_tree_xml = grouped_tree_xml
                    
                    # Count solutions and tiers for display
                    tree_root = ET.fromstring(grouped_tree_xml)
                    solutions = tree_root.findall('.//Solution')
                    tiers = tree_root.findall('.//Tier')
                    servers = tree_root.findall('.//Server')
                    
                    st.success(f"✅ Generated grouped tree: {len(solutions)} Solution(s), {len(tiers)} Tier(s), {len(servers)} Server(s)")
                    
                except Exception as e:
                    st.error(f"❌ Error generating grouped tree: {str(e)}")
                    import traceback
                    with st.expander("Debug Info"):
                        st.code(traceback.format_exc())
                    return
        
        # Display results if available
        if st.session_state.structured_df is not None:
            st.divider()
            
            # Main tabs
            tab_main, tab_raw, tab_grouped, tab_json, tab_csv = st.tabs([
                "📊 29-Column Table", 
                "📄 Raw XML (Step 1)", 
                "🌳 Grouped Tree (Step 2)", 
                "📋 JSON View", 
                "📊 CSV View"
            ])
            
            with tab_main:
                # Main table view
                display_29_column_table(st.session_state.structured_df)
            
            with tab_raw:
                if st.session_state.raw_xml:
                    st.markdown("### 📄 Raw XML Output (Step 1)")
                    st.markdown("**This is the ungrouped, flat XML structure from step 1.**")
                    st.code(st.session_state.raw_xml, language="xml")
                    
                    st.download_button(
                        label="⬇️ Download Raw XML",
                        data=st.session_state.raw_xml,
                        file_name=f"{st.session_state.processed_filename.replace('.pdf', '')}_raw.xml",
                        mime="application/xml"
                    )
                else:
                    st.info("Raw XML not available. Please process the PDF first.")
            
            with tab_grouped:
                if st.session_state.grouped_tree_xml:
                    st.markdown("### 🌳 Grouped Tree Structure (Step 2)")
                    st.markdown("""
                    **This is the grouped tree structure for GDO validation:**
                    - **Configuration** → **Solutions** → **Solution** → **Tiers** → **Tier** → **Servers** → **Server**
                    - Grouped by: Service (Solution) → System/Tier → Server
                    - Ready for comparison and validation
                    """)
                    
                    # Display tree structure summary
                    tree_root = ET.fromstring(st.session_state.grouped_tree_xml)
                    solutions = tree_root.findall('.//Solution')
                    
                    st.markdown(f"**📊 Tree Summary:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Solutions", len(solutions))
                    with col2:
                        tiers = tree_root.findall('.//Tier')
                        st.metric("Tiers", len(tiers))
                    with col3:
                        servers = tree_root.findall('.//Server')
                        st.metric("Servers", len(servers))
                    
                    # Extract all servers with 29 columns for display
                    servers_df = extract_servers_from_grouped_tree(st.session_state.grouped_tree_xml)
                    
                    # Display solutions in expandable sections with drill-down to all 29 columns
                    st.markdown("**📋 Solutions Overview with Complete Server Drill-Down:**")
                    for i, solution in enumerate(solutions, 1):
                        solution_name = solution.find('SolutionName')
                        solution_name_text = solution_name.text if solution_name is not None else f"Solution {i}"
                        tiers_in_solution = solution.findall('.//Tier')
                        
                        with st.expander(f"🔹 {solution_name_text} ({len(tiers_in_solution)} Tier(s))"):
                            for j, tier in enumerate(tiers_in_solution, 1):
                                tier_type = tier.find('TierType')
                                tier_type_text = tier_type.text if tier_type is not None else "Unknown"
                                system_name = tier.find('.//system_name')
                                system_name_text = system_name.text if system_name is not None else "Unknown"
                                servers_in_tier = tier.findall('.//Server')
                                
                                st.markdown(f"**Tier {j}:** {system_name_text} ({tier_type_text}) - {len(servers_in_tier)} Server(s)")
                                
                                # Display each server with all 29 columns
                                for k, server in enumerate(servers_in_tier, 1):
                                    server_name_elem = server.find('server')
                                    server_name = server_name_elem.text if server_name_elem is not None else f"Server {k}"
                                    
                                    with st.expander(f"🖥️ Server {k}: {server_name}", expanded=False):
                                        # Filter servers_df for this specific server
                                        server_data = servers_df[
                                            (servers_df['Solution'] == solution_name_text) &
                                            (servers_df['server'] == server_name)
                                        ]
                                        
                                        if not server_data.empty:
                                            # Display all 29 columns in a table
                                            st.markdown("**All 29 Columns:**")
                                            
                                            # Create a two-column layout for better readability
                                            col1, col2 = st.columns(2)
                                            
                                            with col1:
                                                for idx, col in enumerate(COLUMN_STRUCTURE[:15]):
                                                    value = server_data[col].iloc[0] if col in server_data.columns else ""
                                                    st.markdown(f"**{col}:** {value}")
                                            
                                            with col2:
                                                for idx, col in enumerate(COLUMN_STRUCTURE[15:]):
                                                    value = server_data[col].iloc[0] if col in server_data.columns else ""
                                                    st.markdown(f"**{col}:** {value}")
                                            
                                            # Also show as a compact table
                                            st.markdown("**Table View:**")
                                            display_cols = ['Solution', 'TierType'] + COLUMN_STRUCTURE
                                            available_cols = [col for col in display_cols if col in server_data.columns]
                                            st.dataframe(
                                                server_data[available_cols],
                                                use_container_width=True,
                                                hide_index=True
                                            )
                                        else:
                                            # Fallback: extract directly from XML
                                            st.markdown("**All 29 Columns (from XML):**")
                                            col1, col2 = st.columns(2)
                                            
                                            def get_server_value(server_elem, tag):
                                                elem = server_elem.find(tag)
                                                return elem.text if elem is not None and elem.text else ""
                                            
                                            with col1:
                                                for idx, col in enumerate(COLUMN_STRUCTURE[:15]):
                                                    value = get_server_value(server, col)
                                                    st.markdown(f"**{col}:** {value}")
                                            
                                            with col2:
                                                for idx, col in enumerate(COLUMN_STRUCTURE[15:]):
                                                    value = get_server_value(server, col)
                                                    st.markdown(f"**{col}:** {value}")
                    
                    st.divider()
                    
                    # Display all servers in a comprehensive table for comparison
                    if not servers_df.empty:
                        st.markdown("**📊 Complete Server Comparison Table (All 29 Columns):**")
                        st.markdown("**Use this table to compare all servers across different contract versions.**")
                        
                        # Show filter options
                        col_filter1, col_filter2, col_filter3 = st.columns(3)
                        with col_filter1:
                            solution_filter = st.multiselect(
                                "Filter by Solution",
                                options=sorted(servers_df['Solution'].unique()) if 'Solution' in servers_df.columns else [],
                                default=[]
                            )
                        with col_filter2:
                            tier_filter = st.multiselect(
                                "Filter by Tier Type",
                                options=sorted(servers_df['TierType'].unique()) if 'TierType' in servers_df.columns else [],
                                default=[]
                            )
                        with col_filter3:
                            server_filter = st.text_input("Search Server Name", "")
                        
                        # Apply filters
                        filtered_df = servers_df.copy()
                        if solution_filter:
                            filtered_df = filtered_df[filtered_df['Solution'].isin(solution_filter)]
                        if tier_filter:
                            filtered_df = filtered_df[filtered_df['TierType'].isin(tier_filter)]
                        if server_filter:
                            filtered_df = filtered_df[
                                filtered_df['server'].str.contains(server_filter, case=False, na=False)
                            ]
                        
                        # Display filtered table
                        st.dataframe(
                            filtered_df,
                            use_container_width=True,
                            height=600,
                            hide_index=True
                        )
                        
                        st.info(f"**Showing {len(filtered_df)} of {len(servers_df)} servers**")
                        
                        # Download filtered data
                        csv_filtered = dataframe_to_csv(filtered_df)
                        st.download_button(
                            label="⬇️ Download Filtered Server Data (CSV)",
                            data=csv_filtered,
                            file_name=f"{st.session_state.processed_filename.replace('.pdf', '')}_servers_comparison.csv",
                            mime="text/csv"
                        )
                    
                    st.divider()
                    st.download_button(
                        label="⬇️ Download Grouped Tree XML",
                        data=st.session_state.grouped_tree_xml,
                        file_name=f"{st.session_state.processed_filename.replace('.pdf', '')}_grouped_tree.xml",
                        mime="application/xml"
                    )
                else:
                    st.info("Grouped tree XML not available. Please process the PDF first.")
            
            with tab_json:
                json_data = dataframe_to_json(st.session_state.structured_df)
                st.code(json_data, language="json")
            
            with tab_csv:
                csv_data = dataframe_to_csv(st.session_state.structured_df)
                st.code(csv_data, language="csv")
            
            # Summary
            with st.expander("📈 Summary"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(st.session_state.structured_df))
                with col2:
                    st.metric("Total Columns", len(COLUMN_STRUCTURE))
                with col3:
                    non_empty_rows = st.session_state.structured_df.notna().any(axis=1).sum()
                    st.metric("Rows with Data", non_empty_rows)
    
    else:
        st.info("👆 Please upload a PDF file to get started.")
        
        # Instructions
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            ### How to Use:
            
            1. **Upload a PDF**: Click the upload area above and select your PDF file containing tables
            2. **Configure**: Adjust extraction settings in the sidebar (pages, flavor)
            3. **Process**: Click "Extract & Structure Data" to:
               - Extract tables using Camelot
               - Structure data to 29-column format using OpenAI
            4. **View Results**: 
               - See the 29-column table view
               - Download in CSV, JSON, or XML format
               - View raw data in different tabs
            
            ### 29-Column Structure:
            The output follows this standardized structure:
            - amount, system_name, service, database, tiername, tier_type
            - system_id, ram_gib, cpus_physvirt, saps
            - no_of_add_hana_nodes, no_of_standby_nodes, tenant__user_data_size
            - amount_storage_1_gb, iops1, through_put1
            - amount_storage_2_gb, iops2, through_put2
            - storage_information_1, backup_class, os, sla, dr
            - add_hw_for_dr, pacemaker_included, add_requirements, phase, server
            
            ### Requirements:
            - **Camelot** requires Ghostscript to be installed on your system
            - **OpenAI API key** must be configured (check config_local.py or Streamlit secrets)
            """)

if __name__ == "__main__":
    print('Starting Streamlit app...')
    main()

