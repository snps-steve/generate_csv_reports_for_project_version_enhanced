#!/usr/bin/env python3
"""
BlackDuck Connection Test Script
Tests connectivity using .restconfig.json (required by hub-rest-api-python library)

This script helps you:
1. Work with the hub-rest-api-python library to test connectivity (see: https://github.com/blackducksoftware/hub-rest-api-python)
1. Check if .restconfig.json exists and is valid
2. Test BlackDuck Server connectivity
3. Create .restconfig.json from environment variables if needed
4. Verify your setup before running the enhanced reports script

Usage:
    python test_blackduck_connection.py
"""

import os
import sys
import json
import urllib3
from pathlib import Path

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_restconfig_file():
    """Check if .restconfig.json exists and is valid"""
    
    print("🔍 Checking .restconfig.json file...")
    
    if not os.path.exists('.restconfig.json'):
        print("❌ .restconfig.json file not found in current directory")
        return False, None
    
    try:
        with open('.restconfig.json', 'r') as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = ['baseurl', 'api_token']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"❌ .restconfig.json missing required fields: {missing_fields}")
            return False, config
        
        print("✅ .restconfig.json file found and appears valid")
        
        # Show configuration (hide token)
        masked_config = config.copy()
        if 'api_token' in masked_config:
            masked_config['api_token'] = '*' * 20 + ' (hidden)'
        
        print("📋 Configuration:")
        for key, value in masked_config.items():
            print(f"   {key}: {value}")
        
        return True, config
        
    except json.JSONDecodeError:
        print("❌ .restconfig.json contains invalid JSON")
        return False, None
    except Exception as e:
        print(f"❌ Error reading .restconfig.json: {e}")
        return False, None

def test_blackduck_connection(config):
    """Test BlackDuck connection using .restconfig.json"""
    
    print("\n🔗 Testing BlackDuck connection...")
    
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
        user_type = user.get('type', 'Unknown')
        print(f"👤 Authenticated as: {username} ({user_type})")
        
        # Test project access
        print("\n📂 Testing project access...")
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
                
                if project_count > sample_count:
                    print(f"   ... and {project_count - sample_count} more")
        else:
            print("⚠️  No projects found")
            print("   This could mean:")
            print("   - You have no projects assigned to your account")
            print("   - Limited read permissions")
            print("   - This is a new BlackDuck instance")
        
        print(f"\n🎉 Connection test successful!")
        return True
        
    except ImportError:
        print("❌ BlackDuck library not installed")
        print("   Run: pip install blackduck")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        
        # Provide specific guidance based on error type
        if 'unauthorized' in error_msg.lower() or '401' in error_msg:
            print("\n💡 Authentication issue:")
            print("   - Check your API token in BlackDuck UI")
            print("   - Ensure the token hasn't expired")
            print("   - Verify token has appropriate permissions")
        
        elif 'ssl' in error_msg.lower() or 'certificate' in error_msg.lower():
            print("\n💡 SSL certificate issue:")
            print("   - For self-signed certificates, set 'trust_cert': true in .restconfig.json")
            print("   - For IP addresses, always use 'trust_cert': true")
        
        elif 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
            print("\n💡 Network issue:")
            print("   - Verify the server URL is accessible")
            print("   - Check firewall/network connectivity")
            print("   - Try increasing timeout in .restconfig.json")
        
        return False

def create_restconfig_from_env():
    """Create .restconfig.json from environment variables"""
    
    print("\n🔧 Checking environment variables...")
    
    blackduck_url = os.getenv('BLACKDUCK_URL')
    blackduck_token = os.getenv('BLACKDUCK_API_TOKEN')
    
    if not blackduck_url:
        print("❌ BLACKDUCK_URL environment variable not set")
        return False
    
    if not blackduck_token:
        print("❌ BLACKDUCK_API_TOKEN environment variable not set")
        return False
    
    print("✅ Environment variables found")
    print(f"   BLACKDUCK_URL: {blackduck_url}")
    print(f"   BLACKDUCK_API_TOKEN: {'*' * 20} (hidden)")
    
    # Ask user if they want to create .restconfig.json
    response = input("\nCreate .restconfig.json from environment variables? (y/N): ")
    
    if response.lower() not in ['y', 'yes']:
        print("❌ User declined to create .restconfig.json")
        return False
    
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
        print("🔒 File permissions set to 600 (owner read/write only)")
        
        # Add to .gitignore if it exists
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
            
            if '.restconfig.json' not in gitignore_content:
                with open('.gitignore', 'a') as f:
                    f.write('\n.restconfig.json\n')
                print("✅ Added .restconfig.json to .gitignore")
        else:
            print("💡 Consider creating a .gitignore file with .restconfig.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .restconfig.json: {e}")
        return False

def provide_setup_guidance():
    """Provide guidance on setting up .restconfig.json"""
    
    print("\n🔧 Setup Guidance")
    print("\nThe BlackDuck Python library requires a .restconfig.json file.")
    print("Here are your options:")
    
    print("\n📄 Option 1: Create .restconfig.json manually")
    print("   Create a file named .restconfig.json in this directory:")
    print()
    print('   {')
    print('     "baseurl": "https://your-blackduck-server.com",')
    print('     "api_token": "your-api-token-here",')
    print('     "timeout": 120,')
    print('     "trust_cert": true')
    print('   }')
    print()
    print("   Then run: chmod 600 .restconfig.json")
    
    print("\n🌍 Option 2: Set environment variables, then run this script again")
    print("   export BLACKDUCK_URL=\"https://your-blackduck-server.com\"")
    print("   export BLACKDUCK_API_TOKEN=\"your-api-token-here\"")
    print("   export BLACKDUCK_TRUST_CERT=true")
    print("   python test_blackduck_connection.py")
    
    print("\n🔑 To get your API token:")
    print("   1. Log into BlackDuck Web UI")
    print("   2. Click your username (top-right) → My Access Tokens")
    print("   3. Create new token with 'read' and 'write' scopes")
    print("   4. Copy the token immediately (you won't see it again)")
    
    print("\n⚠️  Security reminders:")
    print("   - Never commit .restconfig.json to version control")
    print("   - Set file permissions to 600 (owner read/write only)")
    print("   - Add .restconfig.json to your .gitignore file")

def show_next_steps():
    """Show what to do after successful connection"""
    
    print("\n🚀 Next Steps:")
    print("✅ Your BlackDuck connection is working correctly!")
    print("\n📊 You can now run the enhanced CSV reports script:")
    print("   python generate_csv_reports_for_project_version_enhanced.py \\")
    print('     "YourProjectName" "YourVersionName" -r vulnerabilities')
    
    print("\n🔍 To find your exact project and version names:")
    print("   1. Check the BlackDuck Web UI")
    print("   2. Or run this command to list them:")
    print("      python -c \"")
    print("from blackduck.HubRestApi import HubInstance")
    print("hub = HubInstance()")
    print("projects = hub.get_projects(limit=10)")
    print("for p in projects['items']:")
    print("    print(f'Project: {p[\\\"name\\\"]}')\"")

def main():
    """Main function - orchestrates the connection test"""
    
    print("🚀 BlackDuck Connection Test")
    print("   Tests .restconfig.json configuration and connectivity\n")
    
    # Step 1: Check if .restconfig.json exists and is valid
    config_valid, config = check_restconfig_file()
    
    if config_valid:
        # Step 2: Test connection using existing .restconfig.json
        if test_blackduck_connection(config):
            show_next_steps()
            sys.exit(0)
        else:
            print("\n❌ Connection failed with existing .restconfig.json")
            print("   Check your credentials and server accessibility")
            sys.exit(1)
    
    else:
        # Step 3: .restconfig.json doesn't exist or is invalid
        # Try to create it from environment variables
        if create_restconfig_from_env():
            print("\n🔄 Testing connection with newly created .restconfig.json...")
            _, new_config = check_restconfig_file()
            if test_blackduck_connection(new_config):
                show_next_steps()
                sys.exit(0)
            else:
                print("\n❌ Connection failed even with new .restconfig.json")
                sys.exit(1)
        else:
            # Provide setup guidance
            provide_setup_guidance()
            sys.exit(1)

if __name__ == "__main__":
    main()
