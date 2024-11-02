# Middle East Pulse News Agency

## Deployment Guide

### 1. Google Cloud Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable the Google Drive API
3. Create a service account with the following roles:
   - Cloud Storage Viewer

### 2. Google Drive Setup
1. Share your country folders with the service account email
2. Note down the folder IDs from the URLs:
   - IL: 18G3s5z9n0L8WeQz2BZd-aJyX4zRwJrdf
   - LB: 181l44LQO7bzfqx81QCa5gQZVGGDXUzHn
   - IR: 193N2sZSHVpiyYnOGZ3Zb-IWxm-CYFX-c
   - CZ: 18IOIsintq1t3SkZ496XcgRLfhTJfL5T7

### 3. Streamlit Cloud Setup
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Add the following secrets in Streamlit Cloud settings:

```toml
[gcp_service_account]
type = "service_account"
project_id = "newstrends2024"
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"

[folder_ids]
IL = "18G3s5z9n0L8WeQz2BZd-aJyX4zRwJrdf"
LB = "181l44LQO7bzfqx81QCa5gQZVGGDXUzHn"
IR = "193N2sZSHVpiyYnOGZ3Zb-IWxm-CYFX-c"
CZ = "18IOIsintq1t3SkZ496XcgRLfhTJfL5T7"
```

### 4. File Structure
The application expects:
- JSON files in text_archive/{country_code}/
- MP3 files in archive/{country_code}/
- Files named like: {country_code}_{YYYYMMDD}_{HHMMSS}_log.json and {country_code}_{YYYYMMDD}_{HHMMSS}_analysis.mp3
