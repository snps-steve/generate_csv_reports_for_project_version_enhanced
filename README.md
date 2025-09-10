# Enhanced CSV Reports Generator for BlackDuck

A Python script that generates CSV reports for BlackDuck project versions with enhanced security vulnerability information including file paths, remediation guidance, and reference links.

## Overview

This script extends the standard BlackDuck reporting functionality by:
- Generating standard BlackDuck CSV reports for projects and versions
- **Enhancing security reports** with additional valuable information:
  - **File Paths**: Shows exactly which files in your codebase contain the vulnerable components
  - **How to Fix**: Provides remediation guidance and solutions for vulnerabilities
  - **References and Related Links**: Includes relevant security advisories and documentation links

## Prerequisites

### Required Dependencies
```bash
pip install blackduck
```

### BlackDuck Configuration
Ensure you have BlackDuck Hub credentials configured. The script uses `HubInstance()` which typically reads from:
- Environment variables (`BLACKDUCK_URL`, `BLACKDUCK_API_TOKEN`)
- Configuration files (`~/.blackduck/config.json`)
- Command line authentication

## Installation

1. Download the script:
```bash
wget https://your-repo/generate_csv_reports_for_project_version_enhanced.py
# or
git clone https://your-repo/blackduck-enhanced-reports.git
```

2. Make it executable:
```bash
chmod +x generate_csv_reports_for_project_version_enhanced.py
```

## Basic Usage

### Credentials

## Method #1: Exports

# Required
export BLACKDUCK_URL="https://your-blackduck-server.com"
export BLACKDUCK_API_TOKEN="your-api-token-here"

# Optional
export BLACKDUCK_TIMEOUT=120
export BLACKDUCK_TRUST_CERT=true  # For self-signed certificates

## Method #2: Config File 
Create a configuration file at ~/.blackduck/config.json:
{
    "url": "https://your-blackduck-server.com",
    "api_token": "your-api-token-here",
    "timeout": 120,
    "trust_cert": true
}

## Method #3: Embed Creds into Script (not recommended)
# Option A: Using environment variables (current approach)
from blackduck.HubRestApi import HubInstance
hub = HubInstance()  # Automatically reads from env vars or config file

# Option B: Direct configuration
from blackduck.HubRestApi import HubInstance
hub = HubInstance(
    baseurl="https://your-blackduck-server.com",
    api_token="your-api-token-here",
    timeout=120,
    trust_cert=True  # Set to True for self-signed certificates
)

# Option C: Using username/password (less secure, not recommended)
from blackduck.HubRestApi import HubInstance
hub = HubInstance(
    baseurl="https://your-blackduck-server.com",
    username="your-username",
    password="your-password",
    timeout=120,
    trust_cert=True
)

# Option D: Configuration with SSL verification disabled (development only)
from blackduck.HubRestApi import HubInstance
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

hub = HubInstance(
    baseurl="https://your-blackduck-server.com",
    api_token="your-api-token-here",
    verify=False,  # Disables SSL verification - use only for testing
    timeout=120
)

### Generate All Reports (with Security Enhancement)
```bash
python generate_csv_reports_for_project_version_enhanced.py "MyProject" "v1.0.0"
```

### Generate Only Security Reports (Enhanced)
```bash
python generate_csv_reports_for_project_version_enhanced.py "MyProject" "v1.0.0" -r vulnerabilities
```

### Generate Multiple Specific Reports
```bash
python generate_csv_reports_for_project_version_enhanced.py "MyProject" "v1.0.0" -r vulnerabilities,components,license_terms
```

## Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `project_name` | BlackDuck project name (required) | - | `"MyWebApp"` |
| `version_name` | Project version name (required) | - | `"v2.1.0"` |
| `-z, --zip_file_name` | Output zip filename | `reports.zip` | `-z "myproject_reports.zip"` |
| `-r, --reports` | Comma-separated report types | All reports | `-r "vulnerabilities,components"` |
| `--format` | Report format | `CSV` | `--format CSV` |
| `-t, --tries` | Download retry attempts | `5` | `-t 3` |
| `-s, --sleep_time` | Wait time between retries (seconds) | `30` | `-s 60` |

## Available Report Types

| Report Type | BlackDuck Name | Description |
|-------------|----------------|-------------|
| `version` | `VERSION` | Project version information |
| `scans` | `CODE_LOCATIONS` | Scan locations and details |
| `components` | `COMPONENTS` | Component inventory |
| `vulnerabilities` | `SECURITY` | **Security vulnerabilities (Enhanced)** |
| `source` | `FILES` | Source file information |
| `cryptography` | `CRYPTO_ALGORITHMS` | Cryptographic algorithms |
| `license_terms` | `LICENSE_TERM_FULFILLMENT` | License compliance |
| `component_additional_fields` | `BOM_COMPONENT_CUSTOM_FIELDS` | Custom component fields |
| `project_version_additional_fields` | `PROJECT_VERSION_CUSTOM_FIELDS` | Custom version fields |
| `vulnerability_matches` | `VULNERABILITY_MATCH` | Vulnerability matching details |

## Enhanced Security Reports

When you include `vulnerabilities` in your reports, the script automatically enhances the security report with three additional columns:

### Enhanced Columns Explained

1. **File Paths** 
   - Shows the exact file locations in your codebase where vulnerable components are found
   - Format: `src/main/java/com/example/App.java; lib/vulnerable-lib.jar`
   - Helps developers quickly locate and assess impact

2. **How to Fix**
   - Provides remediation guidance from BlackDuck's vulnerability database
   - Includes upgrade recommendations, patches, or workarounds
   - Sourced directly from BlackDuck's solution database

3. **References and Related Links**
   - JSON-formatted list of related security advisories, CVE links, and documentation
   - Includes NIST, vendor advisories, and other authoritative sources
   - Format: `[{"rel": "advisory", "href": "https://..."}]`

## Example Usage Scenarios

### DevSecOps Pipeline Integration
```bash
# Generate security report for CI/CD pipeline
python generate_csv_reports_for_project_version_enhanced.py \
  "${CI_PROJECT_NAME}" \
  "${CI_COMMIT_TAG}" \
  -r vulnerabilities \
  -z "security_scan_${CI_COMMIT_SHA}.zip"
```

### Compliance Reporting
```bash
# Generate comprehensive compliance reports
python generate_csv_reports_for_project_version_enhanced.py \
  "ProductionApp" \
  "release-2024.1" \
  -r vulnerabilities,license_terms,components \
  -z "compliance_report_$(date +%Y%m%d).zip"
```

### Developer Security Review
```bash
# Quick security assessment for developers
python generate_csv_reports_for_project_version_enhanced.py \
  "MyFeatureBranch" \
  "develop" \
  -r vulnerabilities \
  --sleep_time 15
```

## Output Structure

The script generates a zip file containing:

### Standard Reports
- `{report_type}_{timestamp}.csv` - Standard BlackDuck reports

### Enhanced Security Reports
- `enhanced_{original_security_report_name}_{timestamp}.csv` - Enhanced with additional columns

### Example Output
```
reports.zip
├── security_20241201-143022.csv                    # Original security report
├── enhanced_security_20241201-143022.csv           # Enhanced with file paths, fixes, references
├── components_20241201-143022.csv                  # Component inventory
└── license_terms_20241201-143022.csv              # License information
```

## Understanding Enhanced CSV Output

### Sample Enhanced Security Report Row
```csv
Component,Version,Vulnerability,Severity,File Paths,How to Fix,References and Related Links
"jackson-databind","2.9.8","CVE-2019-12384","HIGH","src/lib/jackson-databind-2.9.8.jar; pom.xml","Upgrade to version 2.9.9.3 or later","[{""rel"":""cve"",""href"":""https://nvd.nist.gov/vuln/detail/CVE-2019-12384""}]"
```

## Troubleshooting

### Common Issues

#### No Enhanced Files Generated
**Problem**: Enhanced files don't appear in the zip
**Solutions**:
1. Ensure you're requesting security reports: `-r vulnerabilities`
2. Check logs for error messages about API calls
3. Verify BlackDuck credentials and permissions

#### Empty File Paths Column
**Problem**: "No file paths available" appears frequently
**Possible Causes**:
- Component IDs missing from report data
- Insufficient permissions to access matched files API
- Components detected through package managers vs. direct file scanning

#### API Rate Limiting
**Problem**: Script fails with API errors
**Solutions**:
- Increase sleep time: `-s 60`
- Reduce retry attempts: `-t 3`
- Run during off-peak hours

### Debug Mode
Enable detailed logging by modifying the script's logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Verify Output
Check what's in your zip file:
```bash
unzip -l reports.zip
```

## Best Practices

### For DevSecOps Teams
1. **Automate in CI/CD**: Include enhanced reports in your security pipeline
2. **Filter by Severity**: Process high/critical vulnerabilities first
3. **Track Over Time**: Compare reports across versions to track security improvements

### For Development Teams
1. **Focus on File Paths**: Use the enhanced path information to prioritize fixes
2. **Use Remediation Guidance**: Follow the "How to Fix" recommendations
3. **Reference Links**: Use provided links for deeper vulnerability research

### For Security Teams
1. **Comprehensive Reporting**: Generate all report types for complete visibility
2. **Regular Scanning**: Schedule automated report generation
3. **Integration**: Import enhanced data into security dashboards or SIEM systems

## Integration Examples

### Jenkins Pipeline
```groovy
pipeline {
    stages {
        stage('Security Scan') {
            steps {
                script {
                    sh """
                        python generate_csv_reports_for_project_version_enhanced.py \\
                            "${env.JOB_NAME}" \\
                            "${env.BUILD_NUMBER}" \\
                            -r vulnerabilities \\
                            -z "security_${env.BUILD_NUMBER}.zip"
                    """
                    archiveArtifacts artifacts: 'security_*.zip'
                }
            }
        }
    }
}
```

### GitHub Actions
```yaml
- name: Generate Enhanced Security Report
  run: |
    python generate_csv_reports_for_project_version_enhanced.py \
      "${{ github.repository }}" \
      "${{ github.ref_name }}" \
      -r vulnerabilities \
      -z "security_report_${{ github.sha }}.zip"
    
- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: security-report
    path: security_report_*.zip
```

## Contributing

When modifying this script:
1. Test with various BlackDuck project configurations
2. Ensure backward compatibility with existing report formats
3. Add appropriate error handling for new API calls
4. Update this README with any new features or changes

## Support

For issues related to:
- **BlackDuck API**: Check BlackDuck documentation and support
- **Script functionality**: Review logs and verify input parameters
- **Enhanced features**: Ensure proper permissions for matched files and vulnerability APIs
