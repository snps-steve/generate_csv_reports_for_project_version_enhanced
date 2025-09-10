#!/usr/bin/env python3
"""
BlackDuck Connection Test Script
Tests connectivity and lists available projects
"""

import os
import sys
from blackduck.HubRestApi import HubInstance

def test_blackduck_connection():
    """Test connection to BlackDuck and list basic info"""
    
    try:
        # Initialize connection
        print("🔗 Connecting to BlackDuck...")
        hub = HubInstance()
        
        # Test basic connectivity
        print(f"✅ Connected to: {hub.get_urlbase()}")
        
        # Get current user info
        current_user = hub.get_current_user()
        print(f"👤 Authenticated as: {current_user.get('userName', 'Unknown')}")
        
        # List first 5 projects to verify read access
        print("\n📂 Testing project access...")
        projects = hub.get_projects(limit=5)
        
        if projects.get('totalCount', 0) > 0:
            print(f"✅ Found {projects['totalCount']} projects. Sample projects:")
            for project in projects.get('items', [])[:5]:
                print(f"   • {project['name']}")
        else:
            print("⚠️  No projects found (or no read access)")
        
        print("\n🎉 Connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your BLACKDUCK_URL environment variable")
        print("2. Verify your BLACKDUCK_API_TOKEN is correct")
        print("3. Ensure your token has appropriate permissions")
        print("4. Check if your BlackDuck server is accessible")
        return False

def check_environment():
    """Check if required environment variables are set"""
    
    print("🔍 Checking environment configuration...")
    
    required_vars = ['BLACKDUCK_URL', 'BLACKDUCK_API_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'BLACKDUCK_API_TOKEN':
                print(f"✅ {var}: {'*' * 20} (hidden)")
            else:
                print(f"✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
    
    optional_vars = ['BLACKDUCK_TIMEOUT', 'BLACKDUCK_TRUST_CERT']
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"ℹ️  {var}: {value}")
    
    if missing_vars:
        print(f"\n⚠️  Missing required variables: {', '.join(missing_vars)}")
        print("\nSet them with:")
        for var in missing_vars:
            if var == 'BLACKDUCK_URL':
                print(f'export {var}="https://your-blackduck-server.com"')
            elif var == 'BLACKDUCK_API_TOKEN':
                print(f'export {var}="your-api-token-here"')
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 BlackDuck Connection Test\n")
    
    # Check environment first
    if not check_environment():
        sys.exit(1)
    
    print()
    
    # Test connection
    if test_blackduck_connection():
        print("\n✅ Your BlackDuck configuration is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ BlackDuck connection test failed.")
        sys.exit(1)
