# Setting Up Google Cloud Storage for Streamlit Deployment

## 1. Google Cloud Setup

1. Create a Google Cloud Project:
   ```bash
   # Install Google Cloud CLI
   # Visit: https://cloud.google.com/sdk/docs/install
   
   # Login to Google Cloud
   gcloud auth login
   
   # Create new project
   gcloud projects create israel-trends-viewer
   
   # Set project
   gcloud config set project israel-trends-viewer
   ```

2. Enable Google Cloud Storage API:
   - Visit Google Cloud Console
   - Go to "APIs & Services" > "Library"
   - Search for "Cloud Storage"
   - Click "Enable"

3. Create a Storage Bucket:
   ```bash
   # Create bucket
   gsutil mb gs://israel-trends-archive
   
   # Set bucket permissions (public read)
   gsutil iam ch allUsers:objectViewer gs://israel-trends-archive
   ```

4. Create Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `israel-trends-storage`
   - Role: "Storage Object Admin"
   - Create and download JSON key file

## 2. Local Development Setup

1. Install Dependencies:
   ```bash
   pip install google-cloud-storage
   ```

2. Set Environment Variables:
   ```bash
   # Add to .env file
   GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   BUCKET_NAME="israel-trends-archive"
   ```

3. Upload Archive:
   ```bash
   # Run upload script
   python cloud_storage.py
   ```

## 3. Streamlit Cloud Deployment

1. Create GitHub Repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. Set Up Streamlit Cloud:
   - Visit https://share.streamlit.io
   - Connect your GitHub repository
   - Add Environment Variables:
     - `GOOGLE_APPLICATION_CREDENTIALS_JSON`: Copy entire content of service account JSON key
     - `BUCKET_NAME`: israel-trends-archive

3. Required Files:
   ```
   .
   ├── requirements.txt      # Add google-cloud-storage
   ├── cloud_storage.py     # Cloud storage utilities
   ├── israel4_viewer.py    # Main viewer code
   └── streamlit_hebrew.py  # Entry point
   ```

## 4. File Structure in Cloud Storage

```
israel-trends-archive/
├── text_archive/
│   └── IL2/
│       └── IL2_YYYYMMDD_HHMMSS_log.json
└── audio/
    └── IL2/
        └── IL2_YYYYMMDD_HHMMSS_analysis.mp3
```

## 5. Security Notes

1. Service Account:
   - Keep service account key secure
   - Use minimal required permissions
   - Rotate keys periodically

2. Bucket Access:
   - Configure CORS if needed
   - Use signed URLs for audio files
   - Monitor usage and costs

## 6. Maintenance

1. Backup:
   ```bash
   # Backup bucket
   gsutil -m cp -r gs://israel-trends-archive backup/
   ```

2. Clean Old Files:
   ```bash
   # List old files
   gsutil ls -l gs://israel-trends-archive
   
   # Remove old files (careful!)
   gsutil rm gs://israel-trends-archive/path/to/old/files/*
   ```

3. Monitor:
   - Check Cloud Console for:
     - Storage usage
     - Bandwidth costs
     - Error rates
