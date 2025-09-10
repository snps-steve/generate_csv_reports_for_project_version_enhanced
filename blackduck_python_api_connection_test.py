#!/usr/bin/env python3
"""
BlackDuck Connection Test Script - Corrected Version
Tests connectivity using proper .restconfig.json format (based on actual library requirements)

The BlackDuck library expects this format:
{
  "baseurl": "https://your-server.com",
  "api_token": "your-token",
  "insecure": true,
  "debug": false
}

Usage:
    python test_blackduck_connection.py
"""

import os
import sys
import json
import urllib3
from pathlib import Path

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_restconfig_file():
    """Check if .restconfig.json exists and has the correct format"""
    
    print("Checking .restconfig.json file...")
    
    if not os.path.exists('.restconfig.json'):
        print("❌ .restconfig.json file not found in current directory")
        return False, None
    
    try:
        with open('.restconfig.json', 'r') as f:
            config = json.load(f)
        
        # Check required fields for API token method
        required_fields = ['baseurl', 'api_token']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"❌ .restconfig.json missing required fields: {missing_fields}")
            return False, config
        
        print("✅ .restconfig.json file found and appears valid")
        
        # Show configuration (hide token)
        masked_config = config.copy()
        if 'api_token' in masked_config:
            token = masked_config['api_token']
            if len(token) > 20:
                masked_config['api_token'] = token[:10] + '...' + token[-10:] + ' (truncated)'
            else:
                masked_config['api_token'] = '*' * len(token) + ' (hidden)'
        
        print("Configuration:")
        for key, value in masked_config.items():
            print(f"   {key}: {value}")
        
        return True, config
        
    except json.JSONDecodeError:
        print("❌ .restconfig.json contains invalid JSON")
        return False, None
    except Exception as e:
        print(f"❌ Error reading .restconfig.json: {e}")
        return False, None

def test_blackduck_connection():
    """Test BlackDuck connection using .restconfig.json"""
    
    print("\nTesting BlackDuck connection...")
    
    try:
        from blackduck.HubRestApi import HubInstance
        
        # Create hub instance (will automatically read .restconfig.json)
        hub = HubInstance()
        
        # Test connection
        server_url = hub.get_urlbase()
        print(f"✅ Connected to: {server_url}")
        
        # Test authentication
        user = hub.get_current_user()
        username = user.get('userName', 'Unknown')
        print(f"👤 Authenticated as: {username}")
        
        # Test project access
        print("\nTesting project access...")
        projects = hub.get_projects(limit=5)
        project_count = projects.get('totalCount', 0)
        
        if project_count > 0:
            print(f"✅ Found {project_count} accessible projects")
            
            # Show sample projects
            sample_count = min(3, len(projects.get('items', [])))
            if sample_count > 0:
                print("   Sample projects:")
                for project in projects['items'][:sample_count]:
                    project_name = project.get('name', 'Unknown')
                    print(f"   • {project_name}")
        
        print(f"\n🎉 Connection test successful!")
        return True
        
    except ImportError:
        print("❌ BlackDuck library not installed")
        print("   Run: pip install blackduck")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        
        if 'insecure' in error_msg.lower():
            print("\n💡 SSL 'insecure' error:")
            print("   Add 'insecure': true to your .restconfig.json")
        elif 'unauthorized' in error_msg.lower() or '401' in error_msg:
            print("\n💡 Authentication issue:")
            print("   - Check your API token")
            print("   - Ensure the token hasn't expired")
        
        return False

def main():
    """Main function"""
    
    print("🚀 BlackDuck Connection Test\n")
    
    # Check configuration file
    config_valid, config = check_restconfig_file()
    
    if config_valid:
        # Test connection
        if test_blackduck_connection():
            print("\n✅ Your BlackDuck connection is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Connection failed - check your configuration")
            sys.exit(1)
    else:
        print("\n❌ Fix your .restconfig.json file and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
