# Setting up Google Drive for Streamlit App

## 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" at the top of the page
3. Click "New Project"
4. Name it "trends-to-stories" and create

## 2. Enable Google Drive API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click "Enable"

## 3. Create Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in:
   - Name: "trends-to-stories-service"
   - Role: "Editor"
4. Click "Done"
5. Click on the created service account
6. Go to "Keys" tab
7. Add Key > Create new key > JSON
8. Save the downloaded JSON file as `google_drive_credentials.json`

## 4. Google Drive Setup
Your Google Drive is already set up with the correct structure:
- Main folder: trends-to-stories (ID: 17xIMeFyuv1thVSH1vpvto5smTXihx8Hy)
  - CZ (Czech Republic)
  - IL (Israel)
  - IR (Iran)
  - LB (Lebanon)

Make sure all folders are shared with "Anyone with the link" for public access.

## 5. Environment Variables
Add these to your .env file:
```
GOOGLE_DRIVE_CREDENTIALS_PATH=path/to/google_drive_credentials.json
```

## 6. For Streamlit Cloud Deployment
1. Go to your app settings in Streamlit Cloud
2. Add the contents of google_drive_credentials.json as a secret named GOOGLE_DRIVE_CREDENTIALS
3. The app will automatically use the credentials from secrets when deployed

## Important Notes:
- Keep your credentials JSON file secure and never commit it to version control
- For Streamlit Cloud deployment, use secrets management
- Test the setup locally before deploying
- Monitor usage to stay within Google Drive API quotas
