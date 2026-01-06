#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify SAP Cloud SDK for AI (generative) connection"""
import sys
import io
# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load SAP Service Key credentials from environment variables
# Support both AICORE_* and SAP_* naming conventions
SAP_CLIENT_ID = os.environ.get('SAP_CLIENT_ID') or os.environ.get('AICORE_CLIENT_ID', '')
SAP_CLIENT_SECRET = os.environ.get('SAP_CLIENT_SECRET') or os.environ.get('AICORE_CLIENT_SECRET', '')
SAP_AUTH_URL = os.environ.get('SAP_AUTH_URL') or os.environ.get('AICORE_AUTH_URL', '')
aicore_base_url = os.environ.get('AICORE_BASE_URL', '')
if aicore_base_url:
    SAP_AI_API_URL = aicore_base_url.rstrip('/v2').rstrip('/v1').rstrip('/')
else:
    SAP_AI_API_URL = os.environ.get('SAP_AI_API_URL', 'https://api.ai.internalprod.eu-central-1.aws.ml.hana.ondemand.com')
SAP_RESOURCE_GROUP = os.environ.get('AICORE_RESOURCE_GROUP', 'default')

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)
print(f"SAP_CLIENT_ID: {'[SET]' if SAP_CLIENT_ID else '[NOT SET]'}")
print(f"SAP_CLIENT_SECRET: {'[SET]' if SAP_CLIENT_SECRET else '[NOT SET]'}")
print(f"SAP_AUTH_URL: {SAP_AUTH_URL[:60]}..." if len(SAP_AUTH_URL) > 60 else f"SAP_AUTH_URL: {SAP_AUTH_URL}")
print(f"SAP_AI_API_URL: {SAP_AI_API_URL}")
print(f"SAP_RESOURCE_GROUP: {SAP_RESOURCE_GROUP}")
print()

# Import the test function from app.py
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import test_sap_gen_ai_hub_connection
    
    print("=" * 60)
    print("Testing SAP Cloud SDK for AI (generative) Connection")
    print("=" * 60)
    success, message, details = test_sap_gen_ai_hub_connection()
    
    if success:
        print(f"[SUCCESS] {message}")
    else:
        print(f"[FAILED] {message}")
    
    if details:
        print("\nConnection Details:")
        for key, value in details.items():
            print(f"  {key}: {value}")
            
except Exception as e:
    print(f"[ERROR] Error testing connection: {str(e)}")
    import traceback
    traceback.print_exc()

