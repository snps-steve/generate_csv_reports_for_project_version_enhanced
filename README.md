# Enhanced BlackDuck CSV Reports Generator

An advanced Python script that generates comprehensive CSV reports for BlackDuck project versions with enhanced security vulnerability information, including precise file paths, remediation guidance, and authoritative reference links.

## Table of Contents

- [Overview](#overview)
- [What Makes This "Enhanced"?](#what-makes-this-enhanced)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Command Reference](#command-reference)
- [Understanding the Output](#understanding-the-output)
- [DevSecOps Integration](#devsecops-integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Contributing](#contributing)

## Overview

This script extends BlackDuck's standard reporting capabilities by automatically enriching security vulnerability reports with actionable intelligence that development and security teams need to efficiently remediate issues.

### Standard BlackDuck Reports vs Enhanced Reports

| Feature | Standard Reports | Enhanced Reports |
|---------|------------------|------------------|
| Component inventory | ✅ | ✅ |
| Vulnerability identification | ✅ | ✅ |
| File location mapping | ❌ | ✅ **NEW** |
| Remediation guidance | ❌ | ✅ **NEW** |
| Reference links | ❌ | ✅ **NEW** |
| Developer-friendly format | ❌ | ✅ **NEW** |

## What Makes This "Enhanced"?

When processing security reports, the script automatically adds three critical columns that transform raw vulnerability data into actionable intelligence:

### 🎯 **File Paths**
- **What it shows**: Exact file locations where vulnerable components are detected
- **Why it matters**: Enables developers to immediately locate affected code without manual searching
- **Example**: `src/main/java/com/example/App.java; lib/jackson-databind-2.9.8.jar; pom.xml`

### 🔧 **How to Fix** 
- **What it shows**: Specific remediation guidance from BlackDuck's vulnerability database
- **Why it matters**: Provides clear next steps instead of just identifying problems
- **Example**: "Upgrade to version 2.9.9.3 or later. Apply security patch from vendor advisory."

### 📚 **References and Related Links**
- **What it shows**: Authoritative sources and security advisories in structured JSON format
- **Why it matters**: Gives security teams and developers access to detailed vulnerability research
- **Example**: `[{"rel": "cve", "href": "https://nvd.nist.gov/vuln/detail/CVE-2019-12384"}]`

## Prerequisites

### System Requirements
- Python 3.7 or higher
- Network access to your BlackDuck instance
- Appropriate BlackDuck user permissions

### Required Python Dependencies
```bash
pip install blackduck
```

### BlackDuck Permissions Required
Your BlackDuck user account needs:
- **Project access**: Read access to the projects you want to report on
- **Report generation**: Permission to create and download reports
- **Component details**: Access to component and matched files APIs
- **Vulnerability details**: Access to vulnerability information APIs

## Installation & Setup

### 1. Download the Script
```bash
# Option A: Direct download
wget https://github.com/snps-steve/generate_csv_reports_for_project_version_enhanced/

# Option B: Clone the repository
git clone https://github.com/snps-steve/generate_csv_reports_for_project_version_enhanced/
cd generate_csv_reports_for_project_version_enhanced/
```

### 2. Install Dependencies
```bash
pip install blackduck
```

### 3. Make Script Executable (Linux/macOS)
```bash
chmod +x generate_csv_reports_for_project_version_enhanced.py
```

## Configuration

### ⚠️ Important: .restconfig.json is Required

The BlackDuck Python library **requires** a `.restconfig.json` file to be present in the directory where you run the script. This is a hard requirement of the `hub-rest-api-python` library.

### Method 1: Create .restconfig.json Manually (Local Development)

Create a `.restconfig.json` file in the directory where you'll run the script:

```bash
# Create the configuration file
cat > .restconfig.json << 'EOF'
{
    "baseurl": "https://your-blackduck-server.com",
    "api_token": "your-api-token-here",
    "timeout": 120,
    "trust_cert": true
}
EOF

# Secure the file (important!)
chmod 600 .restconfig.json

# Add to .gitignore to prevent accidental commits
echo ".restconfig.json" >> .gitignore
```

**⚠️ Security Note**: Never commit `.restconfig.json` to version control as it contains your API token.

### Method 2: Create .restconfig.json from Environment Variables (CI/CD)

For automated environments like CI/CD pipelines, you can create the `.restconfig.json` file dynamically from environment variables:

```bash
#!/bin/bash
# CI/CD script to create .restconfig.json from environment variables

# Ensure required environment variables are set
if [[ -z "$BLACKDUCK_URL" || -z "$BLACKDUCK_API_TOKEN" ]]; then
    echo "❌ Required environment variables not set"
    echo "Set BLACKDUCK_URL and BLACKDUCK_API_TOKEN"
    exit 1
fi

# Create .restconfig.json from environment variables
cat > .restconfig.json << EOF
{
    "baseurl": "${BLACKDUCK_URL}",
    "api_token": "${BLACKDUCK_API_TOKEN}",
    "timeout": ${BLACKDUCK_TIMEOUT:-120},
    "trust_cert": ${BLACKDUCK_TRUST_CERT:-true}
}
EOF

# Secure the file
chmod 600 .restconfig.json

echo "✅ Created .restconfig.json from environment variables"
```

### Method 3: Using the Setup Helper Script

Use our provided setup script to create `.restconfig.json` interactively:

```bash
python setup_blackduck_config.py
```

### Creating Your BlackDuck API Token

1. **Log into BlackDuck Web UI**
2. **Navigate to User Profile**: Click your username in the top-right corner
3. **Access Token Management**: Go to "My Access Tokens"
4. **Create New Token**: 
   - Name: `Enhanced CSV Reports Script`
   - Scopes: Select `read` and `write` (for report generation)
   - Expiration: Set according to your security policy
5. **Copy Token**: ⚠️ **Save immediately** - you won't see it again!

### Testing Your Configuration

Use the connection test script to verify your setup:

```bash
python test_blackduck_connection.py
```

## Usage

### Basic Examples

#### Generate Enhanced Security Report Only
```bash
python generate_csv_reports_for_project_version_enhanced.py "MyProject" "v1.0.0" -r vulnerabilities
```

#### Generate All Available Reports (with Security Enhancement)
```bash
python generate_csv_reports_for_project_version_enhanced.py "MyProject" "v1.0.0"
```

#### Generate Multiple Specific Reports
```bash
python generate_csv_reports_for_project_version_enhanced.py "MyProject" "v1.0.0" -r vulnerabilities,components,license_terms
```

#### Custom Output File with Retry Configuration
```bash
python generate_csv_reports_for_project_version_enhanced.py \
  "MyProject" "v1.0.0" \
  -r vulnerabilities \
  -z "security_report_$(date +%Y%m%d).zip" \
  -t 3 \
  -s 45
```

### Real-World Scenarios

#### DevSecOps Pipeline Integration
```bash
#!/bin/bash
# CI/CD security scanning script

# Create .restconfig.json from environment variables
cat > .restconfig.json << EOF
{
    "baseurl": "${BLACKDUCK_URL}",
    "api_token": "${BLACKDUCK_API_TOKEN}",
    "timeout": 120,
    "trust_cert": true
}
EOF
chmod 600 .restconfig.json

# Generate enhanced security report
PROJECT_NAME="${CI_PROJECT_NAME}"
VERSION_NAME="${CI_COMMIT_TAG:-${CI_COMMIT_SHORT_SHA}}"
OUTPUT_FILE="security_scan_${CI_PIPELINE_ID}.zip"

python generate_csv_reports_for_project_version_enhanced.py \
  "${PROJECT_NAME}" \
  "${VERSION_NAME}" \
  -r vulnerabilities \
  -z "${OUTPUT_FILE}"

# Clean up credentials
rm -f .restconfig.json

# Archive results
cp "${OUTPUT_FILE}" "${CI_PROJECT_DIR}/artifacts/"
```

## Command Reference

### Required Arguments
| Argument | Description | Example |
|----------|-------------|---------|
| `project_name` | BlackDuck project name (case-sensitive) | `"MyWebApplication"` |
| `version_name` | Project version name (case-sensitive) | `"v2.1.0"` or `"main"` |

### Optional Arguments
| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `-z, --zip_file_name` | Output zip filename | `reports.zip` | `-z "security_$(date +%Y%m%d).zip"` |
| `-r, --reports` | Comma-separated report types | All reports | `-r "vulnerabilities,components"` |
| `--format` | Report format (currently only CSV) | `CSV` | `--format CSV` |
| `-t, --tries` | Number of download retry attempts | `5` | `-t 3` |
| `-s, --sleep_time` | Wait time between retries (seconds) | `30` | `-s 60` |

### Available Report Types

| Report Type | Internal Name | Description | Enhanced? |
|-------------|---------------|-------------|-----------|
| `version` | `VERSION` | Project version metadata | ❌ |
| `scans` | `CODE_LOCATIONS` | Scan locations and details | ❌ |
| `components` | `COMPONENTS` | Component inventory (BOM) | ❌ |
| `vulnerabilities` | `SECURITY` | Security vulnerabilities | ✅ **Enhanced** |
| `source` | `FILES` | Source file inventory | ❌ |
| `cryptography` | `CRYPTO_ALGORITHMS` | Cryptographic algorithms detected | ❌ |
| `license_terms` | `LICENSE_TERM_FULFILLMENT` | License compliance status | ❌ |
| `component_additional_fields` | `BOM_COMPONENT_CUSTOM_FIELDS` | Custom component metadata | ❌ |
| `project_version_additional_fields` | `PROJECT_VERSION_CUSTOM_FIELDS` | Custom version metadata | ❌ |
| `vulnerability_matches` | `VULNERABILITY_MATCH` | Vulnerability matching details | ❌ |

## Understanding the Output

### Output Structure
```
reports.zip
├── security_20241201-143022.csv                           # Original BlackDuck security report
├── enhanced_security_20241201-143022.csv                  # 🎯 Enhanced with additional columns
├── components_20241201-143022.csv                         # Component inventory
└── license_terms_20241201-143022.csv                     # License information
```

### Enhanced Security Report Format

The enhanced report includes all original BlackDuck columns plus three new ones:

#### Sample Enhanced Row
```csv
Component,Version,Vulnerability,Severity,CVSS,File Paths,How to Fix,References and Related Links
"jackson-databind","2.9.8","CVE-2019-12384","HIGH","7.5","src/lib/jackson-databind-2.9.8.jar; pom.xml","Upgrade to version 2.9.9.3 or later to resolve deserialization vulnerability","[{\"rel\":\"cve\",\"href\":\"https://nvd.nist.gov/vuln/detail/CVE-2019-12384\"},{\"rel\":\"advisory\",\"href\":\"https://github.com/advisories/GHSA-...\"}]"
```

## DevSecOps Integration

### Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    
    environment {
        BLACKDUCK_URL = 'https://your-blackduck-server.com'
        BLACKDUCK_API_TOKEN = credentials('blackduck-api-token')
    }
    
    stages {
        stage('Enhanced Security Scan') {
            steps {
                script {
                    // Create .restconfig.json with correct BlackDuck library format
                    sh '''
                        cat > .restconfig.json << EOF
{
  "baseurl": "${BLACKDUCK_URL}",
  "api_token": "${BLACKDUCK_API_TOKEN}",
  "insecure": true,
  "debug": false
}
EOF
                        chmod 600 .restconfig.json
                    '''
                    
                    def reportFile = "security_${env.BUILD_NUMBER}_${env.GIT_COMMIT.take(8)}.zip"
                    
                    sh """
                        python generate_csv_reports_for_project_version_enhanced.py \\
                            "${env.JOB_NAME}" \\
                            "${env.GIT_BRANCH}" \\
                            -r vulnerabilities \\
                            -z "${reportFile}"
                    """
                    
                    // Archive the enhanced report
                    archiveArtifacts artifacts: "${reportFile}"
                }
            }
            
            post {
                always {
                    // Clean up credentials
                    sh 'rm -f .restconfig.json'
                }
            }
        }
    }
}
```

### GitHub Actions Workflow
```yaml
name: Enhanced Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install blackduck
    
    - name: Create BlackDuck Configuration
      env:
        BLACKDUCK_URL: ${{ secrets.BLACKDUCK_URL }}
        BLACKDUCK_API_TOKEN: ${{ secrets.BLACKDUCK_API_TOKEN }}
      run: |
        cat > .restconfig.json << EOF
        {
          "baseurl": "${BLACKDUCK_URL}",
          "api_token": "${BLACKDUCK_API_TOKEN}",
          "insecure": true,
          "debug": false
        }
        EOF
        chmod 600 .restconfig.json
    
    - name: Generate Enhanced Security Report
      run: |
        python generate_csv_reports_for_project_version_enhanced.py \
          "${{ github.repository }}" \
          "${{ github.ref_name }}" \
          -r vulnerabilities \
          -z "security_report_${{ github.sha }}.zip"
    
    - name: Upload Enhanced Report
      uses: actions/upload-artifact@v4
      with:
        name: enhanced-security-report
        path: security_report_*.zip
        retention-days: 30
    
    - name: Clean up credentials
      if: always()
      run: rm -f .restconfig.json
```

## Troubleshooting

### Common Issues

#### 1. No .restconfig.json File Found

**Symptoms**: `[Errno 2] No such file or directory: '.restconfig.json'`

**Solution**: The BlackDuck library requires this file. Create it:

```bash
cat > .restconfig.json << 'EOF'
{
    "baseurl": "https://your-blackduck-server.com",
    "api_token": "your-api-token-here",
    "timeout": 120,
    "trust_cert": true
}
EOF
chmod 600 .restconfig.json
```

#### 2. Authentication Failures

**Symptoms**: "Failed to authenticate" or "401 Unauthorized" errors

**Solutions**:

- **Check .restconfig.json format**:
  ```bash
  cat .restconfig.json | python -m json.tool  # Validate JSON
  ```

- **Verify your API token**:
  ```bash
  # Check token in BlackDuck UI - ensure it hasn't expired
  ```

- **Test connection**:
  ```bash
  python test_blackduck_connection.py
  ```

#### 3. SSL Certificate Issues

**Symptoms**: SSL verification errors or certificate warnings

**Solutions**:

- **For self-signed certificates**, update `.restconfig.json`:
  ```json
  {
      "baseurl": "https://34.211.43.204",
      "api_token": "your-token",
      "timeout": 120,
      "trust_cert": true
  }
  ```

- **For IP addresses** (like `https://34.211.43.204`), always set `"trust_cert": true`

#### 4. Project or Version Not Found

**Symptoms**: "Did not find project" or "Did not find version" messages

**Solutions**:

- **List available projects**:
  ```bash
  python -c "
  from blackduck.HubRestApi import HubInstance
  hub = HubInstance()
  projects = hub.get_projects(limit=100)
  for p in projects['items']:
      print(f'Project: {p[\"name\"]}')
      versions = hub.get_project_versions(p, limit=10)
      for v in versions['items']:
          print(f'  Version: {v[\"versionName\"]}')
  "
  ```

- **Use exact names** from BlackDuck UI (case-sensitive)

## Best Practices

### Configuration Security

1. **Never commit .restconfig.json** to version control
   ```bash
   echo ".restconfig.json" >> .gitignore
   ```

2. **Set restrictive file permissions**
   ```bash
   chmod 600 .restconfig.json
   ```

3. **Clean up in CI/CD pipelines**
   ```bash
   # Always remove .restconfig.json after use
   rm -f .restconfig.json
   ```

### For Development Teams

1. **Local Development Setup**:
   ```bash
   # Create .restconfig.json once for local development
   # Keep it secure and don't commit it
   ```

2. **Team Coordination**:
   - Share setup instructions, not credentials
   - Each developer should have their own API token
   - Use project-specific .gitignore rules

### For DevSecOps Teams

1. **CI/CD Integration**:
   - Store credentials in CI/CD secrets
   - Create .restconfig.json dynamically in pipelines
   - Always clean up credentials after use

2. **Automation**:
   ```bash
   # Example automation script
   #!/bin/bash
   setup_blackduck() {
       cat > .restconfig.json << EOF
   {
       "baseurl": "${BLACKDUCK_URL}",
       "api_token": "${BLACKDUCK_API_TOKEN}",
       "timeout": 120,
       "trust_cert": true
   }
   EOF
       chmod 600 .restconfig.json
   }
   
   cleanup_blackduck() {
       rm -f .restconfig.json
   }
   
   # Use trap to ensure cleanup happens
   trap cleanup_blackduck EXIT
   setup_blackduck
   
   # Your script execution here
   python generate_csv_reports_for_project_version_enhanced.py ...
   ```

## Contributing

### Development Setup

1. **Clone and setup development environment**:
   ```bash
   git clone https://your-repo/blackduck-enhanced-reports.git
   cd blackduck-enhanced-reports
   
   # Create .restconfig.json for development
   cp .restconfig.json.example .restconfig.json
   # Edit with your credentials
   
   # Install dependencies
   pip install blackduck pytest
   ```

2. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

### Making Changes

When modifying this script:

1. **Maintain .restconfig.json compatibility** - this is a hard requirement
2. **Add comprehensive error handling** for new API calls
3. **Update this README** with any new features or breaking changes
4. **Test with various BlackDuck configurations** and project sizes
5. **Follow security best practices** for credential handling

## Support and Resources

### Documentation Links
- [BlackDuck REST API Documentation](https://your-blackduck-server.com/api-doc/public.html)
- [BlackDuck Python SDK](https://github.com/blackducksoftware/blackduck-python)
- [CSV Processing in Python](https://docs.python.org/3/library/csv.html)

### Getting Help

For issues related to:

- **BlackDuck API or platform issues**: Contact BlackDuck support
- **Script functionality or bugs**: Create an issue in this repository with:
  - Complete error messages and logs
  - Your .restconfig.json structure (with credentials redacted)
  - Steps to reproduce the issue
- **Configuration help**: Use our connection test script: `python test_blackduck_connection.py`

### Changelog

**Version 2.1** (Current):
- ✅ Updated to properly work with .restconfig.json requirement
- ✅ Simplified configuration approach
- ✅ Enhanced CI/CD integration examples
- ✅ Improved security guidance

**Version 2.0**:
- ✅ Fixed filename collision bug in enhanced report generation
- ✅ Added comprehensive file path mapping
- ✅ Improved error handling and logging
- ✅ Enhanced progress tracking and user feedback

**Version 1.0**:
- Initial release with basic enhancement functionality
