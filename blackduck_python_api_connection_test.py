'''
Created on Dec 19, 2018
Updated on Sept 20, 2024

@author: gsnyder
@contributor: smiths

Generate a CSV report for a given project-version and enhance with "File Paths", "How to Fix", and 
"References and Related Links"

Requirements:
- The BlackDuck hub-rest-api-python library requires a .restconfig.json file
- This file must be present in the directory where you run this script
- See README.md for setup instructions
'''

import argparse
import csv
import io
import json
import logging
import os
import time
import zipfile
import urllib3
from blackduck.HubRestApi import HubInstance
from requests.exceptions import MissingSchema

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s"
)

version_name_map = {
    'version': 'VERSION',
    'scans': 'CODE_LOCATIONS',
    'components': 'COMPONENTS',
    'vulnerabilities': 'SECURITY',
    'source': 'FILES',
    'cryptography': 'CRYPTO_ALGORITHMS',
    'license_terms': 'LICENSE_TERM_FULFILLMENT',
    'component_additional_fields': 'BOM_COMPONENT_CUSTOM_FIELDS',
    'project_version_additional_fields': 'PROJECT_VERSION_CUSTOM_FIELDS',
    'vulnerability_matches': 'VULNERABILITY_MATCH'
}

all_reports = list(version_name_map.keys())

parser = argparse.ArgumentParser("A program to create reports for a given project-version")
parser.add_argument("project_name")
parser.add_argument("version_name")
parser.add_argument("-z", "--zip_file_name", default="reports.zip")
parser.add_argument("-r", "--reports",
    default=",".join(all_reports), 
    help=f"Comma separated list (no spaces) of the reports to generate - {list(version_name_map.keys())}. Default is all reports.",
    type=lambda s: s.upper())
parser.add_argument('--format', default='CSV', choices=["CSV"], help="Report format - only CSV available for now")
parser.add_argument('-t', '--tries', default=5, type=int, help="How many times to retry downloading the report, i.e. wait for the report to be generated")
parser.add_argument('-s', '--sleep_time', default=30, type=int, help="The amount of time to sleep in-between (re-)tries to download the report")

args = parser.parse_args()

def check_restconfig_file():
    """Check if .restconfig.json exists and has the correct BlackDuck library format"""
    
    if not os.path.exists('.restconfig.json'):
        print("\n❌ .restconfig.json file not found!")
        print("\n🔧 The BlackDuck Python library requires a .restconfig.json file.")
        print("   This file must be present in the directory where you run this script.")
        print("\n📄 Create .restconfig.json with the correct format:")
        print('   {')
        print('     "baseurl": "https://your-blackduck-server.com",')
        print('     "api_token": "your-api-token-here",')
        print('     "insecure": true,')
        print('     "debug": false')
        print('   }')
        print("\n🔒 Secure the file:")
        print("   chmod 600 .restconfig.json")
        print("\n📚 For detailed setup instructions, see README.md")
        print("💡 Or run: python test_blackduck_connection.py")
        exit(1)
    
    try:
        with open('.restconfig.json', 'r') as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = ['baseurl', 'api_token']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"\n❌ .restconfig.json missing required fields: {missing_fields}")
            print("   Required fields: baseurl, api_token")
            print("   See README.md for correct format")
            exit(1)
        
        # Check for incorrect SSL parameters (common mistakes)
        if 'trust_cert' in config:
            print("\n⚠️  Found 'trust_cert' in .restconfig.json")
            print("   The BlackDuck library uses 'insecure': true instead")
            print("   Update your .restconfig.json format")
            exit(1)
        
        if 'verify' in config:
            print("\n⚠️  Found 'verify' in .restconfig.json")
            print("   The BlackDuck library uses 'insecure': true instead")
            print("   Update your .restconfig.json format")
            exit(1)
        
        logging.info("✅ .restconfig.json file found and valid")
        return True
        
    except json.JSONDecodeError:
        print("\n❌ .restconfig.json contains invalid JSON")
        print("   Check the file format - it must be valid JSON")
        print("   See README.md for correct format")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error reading .restconfig.json: {e}")
        exit(1)

def create_hub_instance():
    """Create BlackDuck Hub instance - requires .restconfig.json file with SSL handling"""
    
    # Verify .restconfig.json exists and is valid
    check_restconfig_file()
    
    try:
        # Try standard approach first
        hub = HubInstance()
        logging.info("Successfully created BlackDuck Hub instance using .restconfig.json")
        return hub
    
    except Exception as e:
        error_msg = str(e)
        
        # If we get an 'insecure' error, try explicit SSL bypass
        if 'insecure' in error_msg.lower():
            logging.warning("Standard connection failed with 'insecure' error, trying explicit SSL bypass")
            try:
                # Read .restconfig.json to get credentials for explicit connection
                with open('.restconfig.json', 'r') as f:
                    config = json.load(f)
                
                # Create hub instance with explicit SSL bypass
                hub = HubInstance(
                    baseurl=config['baseurl'],
                    api_token=config['api_token'],
                    timeout=config.get('timeout', 120),
                    trust_cert=True,
                    verify=False  # Explicitly disable SSL verification
                )
                logging.info("Successfully created BlackDuck Hub instance with SSL bypass")
                return hub
                
            except Exception as ssl_error:
                logging.error(f"SSL bypass attempt also failed: {ssl_error}")
        
        # If both attempts failed, provide guidance
        print(f"\n❌ Failed to connect to BlackDuck: {error_msg}")
        
        # Provide specific guidance based on error type
        if 'insecure' in error_msg.lower():
            print("\n💡 SSL 'insecure' error:")
            print("   This is common with IP addresses and self-signed certificates")
            print("   Try adding 'verify': false to your .restconfig.json:")
            print('   {')
            print('     "baseurl": "https://34.211.43.204",')
            print('     "api_token": "your-token",')
            print('     "timeout": 120,')
            print('     "trust_cert": true,')
            print('     "verify": false')
            print('   }')
        
        elif 'unauthorized' in error_msg.lower() or '401' in error_msg:
            print("\n💡 Authentication issue:")
            print("   - Check your API token in .restconfig.json")
            print("   - Ensure the token hasn't expired")
            print("   - Verify token has appropriate permissions")
        
        elif 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
            print("\n💡 Network issue:")
            print("   - Verify the server URL is accessible")
            print("   - Check firewall/network connectivity")
            print("   - Try increasing timeout in .restconfig.json")
        
        print("\n🔧 Test your connection:")
        print("   python test_blackduck_connection.py")
        exit(1)

# Create hub instance
hub = create_hub_instance()

class FailedReportDownload(Exception):
    pass

def download_report(location, filename, retries=args.tries):
    report_id = location.split("/")[-1]

    for attempt in range(retries):
        
        # Wait for 30 seconds before attempting to download
        print(f"Waiting 30 seconds before attempting to download...")
        time.sleep(30)

        # Retries
        print(f"Attempt {attempt + 1} of {retries} to retrieve report {report_id}")        
        
        # Report Retrieval 
        print(f"Retrieving generated report from {location}")
        response = hub.download_report(report_id)
        
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Successfully downloaded zip file to {filename} for report {report_id}")
            return response.content
        else:
            print(f"Failed to retrieve report {report_id}")
            if attempt < retries - 1:  # If it's not the last attempt
                wait_time = args.sleep_time
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print(f"Maximum retries reached. Unable to download report.")
    
    raise FailedReportDownload(f"Failed to retrieve report {report_id} after {retries} tries")

def get_file_paths(hub, project_id, project_version_id, component_id, component_version_id, component_origin_id):
    url = f"{hub.get_urlbase()}/api/projects/{project_id}/versions/{project_version_id}/components/{component_id}/versions/{component_version_id}/origins/{component_origin_id}/matched-files"
    headers = {
        "Accept": "application/vnd.blackducksoftware.bill-of-materials-6+json",
        "Authorization": f"Bearer {hub.token}"
    }
    
    logging.debug(f"Making API call to: {url}")
    
    try:
        response = hub.execute_get(url)
        if response.status_code == 200:
            data = response.json()
            file_paths = []
            for item in data.get('items', []):
                file_path = item.get('filePath', {})
                composite_path = file_path.get('compositePathContext', '')
                if composite_path:
                    file_paths.append(composite_path)
            return file_paths
        else:
            logging.error(f"Failed to fetch matched files. Status code: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"Error making API request: {str(e)}")
        return []

def get_vulnerability_details(hub, vulnerability_id):
    url = f"{hub.get_urlbase()}/api/vulnerabilities/{vulnerability_id}"
    
    try:
        response = hub.execute_get(url)
        if response.status_code == 200:
            data = response.json()
            solution = data.get('solution', '')
            references = []
            meta_data = data.get('_meta', {})
            links = meta_data.get('links', [])
            for link in links:
                references.append({
                    'rel': link.get('rel', ''),
                    'href': link.get('href', '')
                })
            return solution, references
        else:
            logging.error(f"Failed to fetch vulnerability details. Status code: {response.status_code}")
            return '', []
    except Exception as e:
        logging.error(f"Error making API request for vulnerability details: {str(e)}")
        return '', []

def enhance_security_report(hub, zip_content, project_id, project_version_id):
    logging.info(f"Enhancing security report for Project ID: {project_id}, Project Version ID: {project_version_id}")
    
    # Generate timestamp once outside the loop
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zin:
        csv_files = [f for f in zin.namelist() if f.endswith('.csv')]
        
        # Filter for security-related CSV files (adjust pattern as needed)
        security_csv_files = [f for f in csv_files if 'security' in f.lower() or 'vulnerability' in f.lower()]
        
        # If no security files found, process all CSV files as fallback
        if not security_csv_files:
            security_csv_files = csv_files
            logging.warning("No security-specific CSV files found. Processing all CSV files.")
        
        enhanced_files_created = 0
        
        for csv_file in security_csv_files:
            logging.info(f"Processing CSV file: {csv_file}")
            csv_content = zin.read(csv_file).decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_content))
            
            # Count total rows
            total_rows = sum(1 for row in reader)
            reader = csv.DictReader(io.StringIO(csv_content))  # Reset reader
            
            fieldnames = reader.fieldnames + ["File Paths", "How to Fix", "References and Related Links"]
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            processed_components = 0
            skipped_components = 0

            for index, row in enumerate(reader, 1):
                print(f"\rProcessing {csv_file} - row {index} of {total_rows} ({index/total_rows*100:.2f}%)", end='', flush=True)
                
                component_id = row.get('Component id', '')
                component_version_id = row.get('Version id', '')
                component_origin_id = row.get('Origin id', '')
                vulnerability_id = row.get('Vulnerability id', '')

                if not all([component_id, component_version_id, component_origin_id]):
                    logging.warning(f"Missing component information. Component ID: {component_id}, Component Version ID: {component_version_id}, Origin ID: {component_origin_id}")
                    skipped_components += 1
                    file_paths = []
                else:
                    file_paths = get_file_paths(hub, project_id, project_version_id, component_id, component_version_id, component_origin_id)
                    processed_components += 1

                if vulnerability_id:
                    solution, references = get_vulnerability_details(hub, vulnerability_id)
                else:
                    solution, references = '', []

                row["File Paths"] = '; '.join(file_paths) if file_paths else "No file paths available"
                row["How to Fix"] = solution
                row["References and Related Links"] = json.dumps(references)
                
                writer.writerow(row)

            print()  # New line after progress

            # Create enhanced filename based on original filename
            base_name = csv_file.replace('.csv', '')
            enhanced_filename = f"enhanced_{base_name}_{timestamp}.csv"

            # Add enhanced report to zip file
            with zipfile.ZipFile(args.zip_file_name, 'a') as zout:
                zout.writestr(enhanced_filename, output.getvalue())
                enhanced_files_created += 1
                logging.info(f"Created enhanced file: {enhanced_filename}")

            logging.info(f"Processed components for {csv_file}: {processed_components}")
            logging.info(f"Skipped components for {csv_file}: {skipped_components}")

    logging.info(f"Enhanced security report processing complete. Created {enhanced_files_created} enhanced files in {args.zip_file_name}")
    
    # List contents of zip file for debugging
    try:
        with zipfile.ZipFile(args.zip_file_name, 'r') as zverify:
            logging.info(f"Final zip file contents: {zverify.namelist()}")
    except Exception as e:
        logging.error(f"Could not verify zip file contents: {str(e)}")

def main():
    project = hub.get_project_by_name(args.project_name)

    if project:
        project_id = project['_meta']['href'].split('/')[-1]
        logging.info(f"Project ID: {project_id}")

        version = hub.get_version_by_name(project, args.version_name)
        if version:
            project_version_id = version['_meta']['href'].split('/')[-1]
            logging.info(f"Project Version ID: {project_version_id}")

            reports_l = [version_name_map.get(r.strip().lower(), r.strip()) for r in args.reports.split(",")]

            valid_reports = set(version_name_map.values())
            invalid_reports = [r for r in reports_l if r not in valid_reports]
            if invalid_reports:
                print(f"Error: Invalid report type(s): {', '.join(invalid_reports)}")
                print(f"Valid report types are: {', '.join(valid_reports)}")
                exit(1)

            # Debug output to verify security report is requested
            logging.info(f"Reports requested: {reports_l}")
            logging.info(f"'SECURITY' in reports: {'SECURITY' in reports_l}")

            response = hub.create_version_reports(version, reports_l, args.format)

            if response.status_code == 201:
                print(f"Successfully created reports ({args.reports}) for project {args.project_name} and version {args.version_name}")
                location = response.headers['Location']
                zip_content = download_report(location, args.zip_file_name)
                
                if 'SECURITY' in reports_l:
                    enhance_security_report(hub, zip_content, project_id, project_version_id)
                else:
                    logging.info("No SECURITY report requested, skipping enhancement")
            else:
                print(f"Failed to create reports for project {args.project_name} version {args.version_name}, status code returned {response.status_code}")
        else:
            print(f"Did not find version {args.version_name} for project {args.project_name}")
    else:
        print(f"Did not find project with name {args.project_name}")

if __name__ == "__main__":
    main()
