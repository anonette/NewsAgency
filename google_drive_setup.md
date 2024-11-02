# Google Drive Setup Guide for Streamlit Deployment

## Local Development Structure

The application supports both local files and Google Drive files. Local files should be organized as follows:

```
project_root/
├── text_archive/
│   ├── IL/
│   │   └── IL_YYYYMMDD_log.json
│   ├── LB/
│   ├── IR/
│   └── CZ/
└── archive/
    ├── IL/
    │   └── IL_YYYYMMDD_analysis.mp3
    ├── LB/
    ├── IR/
    └── CZ/
```

## Google Drive Setup (Optional)

If you want to use Google Drive for file storage:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: "streamlit-drive-access" (or your preferred name)
   - Description: "Service account for Streamlit app to access Drive files"
   - Click "Create"
4. Skip role assignment (we'll handle permissions through Drive sharing)
5. Click "Done"

### Generate Service Account Key

1. In the Credentials page, click on your newly created service account
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" format
5. Click "Create" - this will download the key file

### Configure Google Drive

1. Create a folder structure in Google Drive matching the local structure:
   ```
   Archive/
   ├── IL/
   ├── LB/
   ├── IR/
   └── CZ/
   ```
2. Share the Archive folder with the service account email (found in the key file)
3. Give "Viewer" access to the service account

### Configure Streamlit Secrets

1. For local development:
   - Create `.streamlit/secrets.toml`
   - Add your service account credentials:
   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "your-private-key"
   client_email = "your-service-account-email"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "your-cert-url"
   ```
2. For Streamlit Cloud:
   - Add the same credentials in your app's settings under "Secrets"

## File Naming Convention

Files should follow these naming patterns:
- Log files: `{COUNTRY_CODE}_{YYYYMMDD}_log.json`
- Audio files: `{COUNTRY_CODE}_{YYYYMMDD}_analysis.mp3`

Example:
```
IL_20231201_log.json
IL_20231201_analysis.mp3
```

## Deployment

1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Configure secrets in Streamlit Cloud if using Google Drive
4. Deploy!

## File Priority

The application will:
1. Check for files in the local text_archive directory first
2. If a file isn't found locally, check Google Drive (if configured)
3. Display all available files in the date selector, regardless of source

## Troubleshooting

1. If local files aren't loading:
   - Check file permissions
   - Verify file naming convention
   - Ensure files are in correct directories

2. If Drive files aren't loading:
   - Check Drive API is enabled
   - Verify service account has access
   - Confirm secrets are properly configured

3. For other issues:
   - Check Streamlit logs
   - Verify file paths and naming
   - Ensure proper file structure in both local and Drive storage
