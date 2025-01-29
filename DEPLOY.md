# Deploying to Streamlit Cloud

## 1. Prepare Repository

1. Create a new GitHub repository
2. Push these files:
   ```
   .streamlit/
   ├── config.toml
   cloud_storage.py
   israel4_viewer.py
   streamlit_hebrew.py
   requirements.txt
   .gitignore
   ```

## 2. Set Up Streamlit Cloud

1. Go to https://share.streamlit.io
2. Connect your GitHub repository
3. Set main file to: `streamlit_hebrew.py`

## 3. Configure Environment Variables

Add these environment variables in Streamlit Cloud settings:

1. GOOGLE_APPLICATION_CREDENTIALS_JSON
   - Go to your local key.json file
   - Copy entire contents (including all curly braces and quotes)
   - Paste as the value
   - This allows secure access to Google Cloud Storage
   
2. BUCKET_NAME
   - Value: israel-trends-archive
   - This bucket contains both JSON analyses and MP3 audio files
   - Files are organized in these paths:
     * text_archive/IL2/IL2_[DATE]_log.json
     * audio/IL2/IL2_[DATE]_[TIME]_analysis.mp3

Note: The service account must have Storage Object Viewer role to generate signed URLs for audio files.

## 4. Deploy Settings

1. Python version: 3.9
2. Packages: requirements.txt will be used automatically
3. Secrets: Environment variables will be securely stored

## 5. Testing Deployment

1. Initial deployment will start automatically
2. Check logs for any issues
3. Verify:
   - Cloud storage connection
   - File listing
   - Audio playback
   - Sharing functionality

## 6. Maintenance

1. Monitor usage in Google Cloud Console:
   - Storage usage
   - Bandwidth costs
   - API requests

2. Update procedure:
   - Push changes to GitHub
   - Streamlit Cloud will auto-deploy

## 7. Security Notes

1. Never commit key.json to repository
2. Keep environment variables secure
3. Monitor access logs
4. Rotate credentials periodically

## 8. Troubleshooting

1. Check Streamlit Cloud logs
2. Verify environment variables
3. Test cloud storage access
4. Check file permissions

## 9. Backup

1. Keep local copy of key.json
2. Document all environment variables
3. Maintain backup of cloud storage data
