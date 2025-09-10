#!/usr/bin/env python3
"""
Practical BlackDuck Connection Handler
Works with the hub-rest-api-python library's requirements:
1. If environment variables exist, use them directly with HubInstance parameters
2. If .restconfig.json exists, let HubInstance() use it automatically
3. If neither, provide clear guidance
"""

import os
import sys
import json
import urllib3
import logging
from blackduck.HubRestApi import HubInstance

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_blackduck_hub():
    """
    Create BlackDuck Hub instance working with library requirements.
    
    The hub-rest-api-python library expects .restconfig.json by default,
    so we either:
    1. Use environment variables with explicit parameters
    2. Let it use existing .restconfig.json
    3. Create .restconfig.json from environment variables
    """
    
    # Check for environment variables first
    blackduck_url = os.getenv('BLACKDUCK_URL')
    blackduck_token = os.getenv('BLACKDUCK_API_TOKEN')
    
    # Method 1: Use environment variables with explicit parameters
    if blackduck_url and blackduck_token:
        logging.info("Using environment variables for BlackDuck configuration")
        
        try:
            hub = HubInstance(
                baseurl=blackduck_url.rstrip('/'),
                api_token=blackduck_token,
                timeout=int(os.getenv('BLACKDUCK_TIMEOUT', 120)),
                trust_cert=os.getenv('BLACKDUCK_TRUST_CERT', 'true').lower() == 'true',
                verify=False  # Disable SSL verification for self-signed certs
            )
            return hub, "environment_variables", "Environment variables"
        
        except Exception as e:
            logging.error(f"Failed to create hub instance with environment variables: {e}")
            # Fall through to other methods
    
    # Method 2: Check if .restconfig.json exists and let HubInstance use it
    if os.path.exists('.restconfig.json'):
        try:
            logging.info("Found .restconfig.json, letting HubInstance use it")
            
            # Validate the file first
            with open('.restconfig.json', 'r') as f:
                config = json.load(f)
            
            if 'baseurl' in config and 'api_token' in config:
                hub = HubInstance()  # Let it read .restconfig.json automatically
                return hub, "restconfig_file", ".restconfig.json file"
            else:
                logging.warning(".restconfig.json missing required fields")
        
        except json.JSONDecodeError:
            logging.warning(".restconfig.json contains invalid JSON")
        except Exception as e:
            logging.warning(f"Error reading .restconfig.json: {e}")
    
    # Method 3: If we have environment variables but no .restconfig.json,
    # offer to create the .restconfig.json file
    if blackduck_url and blackduck_token and not os.path.exists('.restconfig.json'):
        print("🔧 Environment variables found but no .restconfig.json")
        response = input("Create .restconfig.json from environment variables? (y/N): ")
        
        if response.lower() in ['y', 'yes']:
            try:
                config = {
                    "baseurl": blackduck_url.rstrip('/'),
                    "api_token": blackduck_token,
                    "timeout": int(os.getenv('BLACKDUCK_TIMEOUT', 120)),
                    "trust_cert": os.getenv('BLACKDUCK_TRUST_CERT', 'true').lower() == 'true'
                }
                
                with open('.restconfig.json', 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Secure the file
                os.chmod('.restconfig.json', 0o600)
                
                print("✅ Created .restconfig.json from environment variables")
                hub = HubInstance()
                return hub, "created_restconfig", "Created .restconfig.json from environment variables"
            
            except Exception as e:
                print(f"❌ Failed to create .restconfig.json: {e}")
    
    # If all methods fail, provide clear guidance
    print("\n❌ Could not establish BlackDuck connection!")
    print("\n🔍 Available options:")
    
    if blackduck_url and blackduck_token:
        print("   ✅ Environment variables are set")
        print("   💡 Try running the script again with explicit parameters")
    else:
        print("   ❌ Environment variables not set")
    
    if os.path.exists('.restconfig.json'):
        print("   ❌ .restconfig.json exists but appears invalid")
    else:
        print("   ❌ .restconfig.json not found")
    
    print("\n🔧 Solutions:")
    print("\n1️⃣ Use environment variables (recommended):")
    print('   export BLACKDUCK_URL="https://your-server.com"')
    print('   export BLACKDUCK_API_TOKEN="your-token"')
    print('   export BLACKDUCK_TRUST_CERT=true')
    print('   source ~/.bashrc')
    
    print("\n2️⃣ Or create .restconfig.json:")
    print('   {')
    print('     "baseurl": "https://your-server.com",')
    print('     "api_token": "your-token",')
    print('     "timeout": 120,')
    print('     "trust_cert": true')
    print('   }')
    
    sys.exit(1)

def test_connection():
    """Test BlackDuck connection with practical approach"""
    
    print("🚀 BlackDuck Connection Test (Practical Approach)\n")
    
    try:
        hub, method, source = create_blackduck_hub()
        
        print(f"✅ Configuration Method: {method}")
        print(f"📋 Configuration Source: {source}")
        
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
        
        print(f"\n🎉 Connection successful!")
        
        # Show what configuration is actually being used
        if method == "environment_variables":
            print("\n💡 Using environment variables directly")
            print("   ✅ No .restconfig.json file needed")
            print("   ✅ Great for CI/CD and production")
        
        elif method == "restconfig_file":
            print("\n💡 Using existing .restconfig.json file")
            print("   ✅ Good for local development")
            print("   ⚠️  Keep this file secure")
        
        elif method == "created_restconfig":
            print("\n💡 Created .restconfig.json from environment variables")
            print("   ✅ Best of both worlds")
            print("   ✅ Library requirements satisfied")
        
        return True
        
    except SystemExit:
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

# Function for use in your enhanced script
def get_hub_instance():
    """
    Get a configured BlackDuck hub instance for your enhanced script.
    This handles the library's .restconfig.json requirement properly.
    """
    
    # Check for environment variables
    blackduck_url = os.getenv('BLACKDUCK_URL')
    blackduck_token = os.getenv('BLACKDUCK_API_TOKEN')
    
    if blackduck_url and blackduck_token:
        # Use environment variables directly
        return HubInstance(
            baseurl=blackduck_url.rstrip('/'),
            api_token=blackduck_token,
            timeout=int(os.getenv('BLACKDUCK_TIMEOUT', 120)),
            trust_cert=os.getenv('BLACKDUCK_TRUST_CERT', 'true').lower() == 'true',
            verify=False
        )
    
    elif os.path.exists('.restconfig.json'):
        # Use existing .restconfig.json
        return HubInstance()
    
    else:
        # No configuration available
        print("❌ No BlackDuck configuration found!")
        print("Set environment variables or create .restconfig.json")
        sys.exit(1)

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("\n🚀 Ready to run enhanced reports script!")
        sys.exit(0)
    else:
        print("\n❌ Please configure BlackDuck and try again")
        sys.exit(1)
