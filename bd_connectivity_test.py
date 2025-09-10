#!/usr/bin/env python3
"""
Smart BlackDuck Connection Handler
Implements intelligent fallback for configuration methods:
1. .restconfig.json file (if exists)
2. Environment variables (if available)
3. Helpful error messages if neither works
"""

import os
import sys
import json
import urllib3
import logging
from blackduck.HubRestApi import HubInstance

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_smart_hub_instance():
    """
    Create BlackDuck Hub instance using intelligent configuration detection.
    Priority order:
    1. .restconfig.json file (if exists)
    2. Environment variables (if available)
    3. Error with helpful guidance
    """
    
    config_method = None
    config_source = None
    
    # Method 1: Check for .restconfig.json file first
    if os.path.exists('.restconfig.json'):
        try:
            logging.info("Found .restconfig.json file, attempting to use it")
            with open('.restconfig.json', 'r') as f:
                config = json.load(f)
            
            # Validate required fields
            if 'baseurl' in config and 'api_token' in config:
                config_method = "restconfig_file"
                config_source = ".restconfig.json"
                logging.info("Using .restconfig.json for BlackDuck configuration")
                
                # Let HubInstance() pick up the .restconfig.json automatically
                return HubInstance(), config_method, config_source
            else:
                logging.warning(".restconfig.json exists but missing required fields (baseurl, api_token)")
        
        except json.JSONDecodeError:
            logging.warning(".restconfig.json exists but contains invalid JSON")
        except Exception as e:
            logging.warning(f"Found .restconfig.json but couldn't read it: {e}")
    
    # Method 2: Check for environment variables
    blackduck_url = os.getenv('BLACKDUCK_URL')
    blackduck_token = os.getenv('BLACKDUCK_API_TOKEN')
    
    if blackduck_url and blackduck_token:
        config_method = "environment_variables"
        config_source = "Environment variables (BLACKDUCK_URL, BLACKDUCK_API_TOKEN)"
        logging.info("Using environment variables for BlackDuck configuration")
        
        try:
            # Create hub instance with environment variables
            hub = HubInstance(
                baseurl=blackduck_url.rstrip('/'),  # Remove trailing slash
                api_token=blackduck_token,
                timeout=int(os.getenv('BLACKDUCK_TIMEOUT', 120)),
                trust_cert=os.getenv('BLACKDUCK_TRUST_CERT', 'true').lower() == 'true',
                verify=False  # Disable SSL verification for self-signed certs
            )
            return hub, config_method, config_source
        
        except Exception as e:
            logging.error(f"Failed to create hub instance with environment variables: {e}")
            # Fall through to error handling
    
    # Method 3: Try default HubInstance() as last resort
    try:
        logging.info("Attempting default BlackDuck configuration")
        hub = HubInstance()
        config_method = "default_config"
        config_source = "Default HubInstance() configuration"
        return hub, config_method, config_source
    except Exception as e:
        logging.error(f"Default configuration failed: {e}")
    
    # If all methods fail, provide comprehensive error message
    print("\n❌ Could not establish BlackDuck connection!")
    print("\n🔍 Configuration Detection Results:")
    
    # Check what we found
    if os.path.exists('.restconfig.json'):
        print("   📁 .restconfig.json: Found but invalid/incomplete")
    else:
        print("   📁 .restconfig.json: Not found")
    
    if blackduck_url:
        print(f"   🌐 BLACKDUCK_URL: Found ({blackduck_url})")
    else:
        print("   🌐 BLACKDUCK_URL: Not set")
    
    if blackduck_token:
        print("   🔑 BLACKDUCK_API_TOKEN: Found (hidden)")
    else:
        print("   🔑 BLACKDUCK_API_TOKEN: Not set")
    
    print("\n🔧 Configuration Options (choose one):")
    print("\n📄 Option 1: .restconfig.json file (in current directory)")
    print("   Create .restconfig.json with:")
    print('   {')
    print('     "baseurl": "https://your-blackduck-server.com",')
    print('     "api_token": "your-api-token-here",')
    print('     "timeout": 120,')
    print('     "trust_cert": true')
    print('   }')
    
    print("\n🌍 Option 2: Environment variables (recommended)")
    print("   Add to ~/.bashrc:")
    print('   export BLACKDUCK_URL="https://your-blackduck-server.com"')
    print('   export BLACKDUCK_API_TOKEN="your-api-token-here"')
    print('   export BLACKDUCK_TRUST_CERT=true')
    print('   export BLACKDUCK_TIMEOUT=120')
    print("   Then run: source ~/.bashrc")
    
    print("\n📚 See README.md for detailed configuration instructions")
    
    sys.exit(1)

def test_smart_connection():
    """Test the smart connection with detailed feedback"""
    
    print("🚀 Smart BlackDuck Connection Test\n")
    
    try:
        # Use smart connection method
        hub, config_method, config_source = create_smart_hub_instance()
        
        print(f"✅ Configuration Method: {config_method}")
        print(f"📋 Configuration Source: {config_source}")
        
        # Test connection
        print(f"\n🔗 Connected to: {hub.get_urlbase()}")
        
        # Test authentication
        user = hub.get_current_user()
        username = user.get('userName', 'Unknown')
        print(f"👤 Authenticated as: {username}")
        
        # Test project access
        projects = hub.get_projects(limit=5)
        project_count = projects.get('totalCount', 0)
        print(f"📂 Found {project_count} accessible projects")
        
        if project_count > 0:
            print("   Sample projects:")
            for project in projects.get('items', [])[:3]:
                print(f"   • {project['name']}")
        
        print(f"\n🎉 Connection successful using: {config_method}")
        
        # Show configuration recommendations
        if config_method == "restconfig_file":
            print("\n💡 Using .restconfig.json file")
            print("   ✅ This works great for local development")
            print("   ⚠️  Remember to keep this file secure and don't commit it to git")
        
        elif config_method == "environment_variables":
            print("\n💡 Using environment variables")
            print("   ✅ This is the recommended approach for production and CI/CD")
            print("   ✅ More secure than config files")
        
        return True
        
    except SystemExit:
        # This is our controlled exit from create_smart_hub_instance()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

# Usage example for your enhanced script
def get_configured_hub():
    """
    Get a configured BlackDuck hub instance for use in your enhanced script.
    This is the function you'd call in your main enhanced script.
    """
    
    try:
        hub, config_method, config_source = create_smart_hub_instance()
        logging.info(f"BlackDuck configured using: {config_method}")
        return hub
    
    except SystemExit:
        # Configuration failed - error message already shown
        raise Exception("BlackDuck configuration failed")

if __name__ == "__main__":
    # Test the smart connection
    success = test_smart_connection()
    
    if success:
        print("\n🚀 Ready to run enhanced reports script!")
        print("   Your BlackDuck configuration is working correctly")
        sys.exit(0)
    else:
        print("\n❌ Please configure BlackDuck and try again")
        sys.exit(1)
