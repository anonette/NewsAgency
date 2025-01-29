from google.cloud import storage
from google.oauth2 import service_account
import streamlit as st
import os
import json
import tempfile
from datetime import datetime

class CloudStorage:
    def __init__(self, bucket_name="israel-trends-archive"):
        """Initialize Google Cloud Storage client
        
        Args:
            bucket_name: Name of the Google Cloud Storage bucket
        """
        # Use the storage client from session state
        import streamlit as st
        if 'storage_client' not in st.session_state:
            raise ValueError(
                "Storage client not found in session state. Please ensure streamlit_hebrew.py is the entry point."
            )
        self.storage_client = st.session_state.storage_client
        # Set up bucket with debug info
        self.bucket_name = bucket_name
        st.write("Debug: Accessing bucket:", bucket_name)
        self.bucket = self.storage_client.bucket(bucket_name)
        
        # Test bucket access
        try:
            # List a few blobs to test access
            blobs = list(self.storage_client.list_blobs(bucket_name, max_results=1))
            st.write("Debug: Successfully accessed bucket")
            st.write("Debug: Found", len(blobs), "blobs")
        except Exception as e:
            st.write("Debug: Error accessing bucket:", str(e))
            raise ValueError(f"Error accessing bucket {bucket_name}: {str(e)}")

    def upload_analysis(self, json_path, audio_path=None):
        """Upload analysis JSON and audio file to cloud storage
        
        Args:
            json_path: Path to JSON analysis file
            audio_path: Optional path to MP3 audio file
        """
        try:
            # Extract timestamp from filename (IL2_20250126_173220_log.json)
            parts = os.path.basename(json_path).split('_')
            if len(parts) < 3:
                print(f"Invalid filename format: {json_path}")
                return False
                
            date = parts[1]  # 20250126
            time = parts[2]  # 173220
            timestamp = f"{date}_{time}"  # 20250126_173220
            
            # Upload JSON file
            json_blob = self.bucket.blob(f"text_archive/IL2/IL2_{date}_log.json")
            json_blob.upload_from_filename(json_path)
            print(f"JSON file uploaded to: {json_blob.name}")
            
            # Upload audio file if provided
            if audio_path and os.path.exists(audio_path):
                print(f"Uploading audio file: {audio_path}")
                audio_blob = self.bucket.blob(f"audio/IL2/IL2_{timestamp}_analysis.mp3")
                audio_blob.upload_from_filename(audio_path)
                print(f"Audio file uploaded to: {audio_blob.name}")
                return True
            else:
                if not audio_path:
                    print("No audio path provided")
                elif not os.path.exists(audio_path):
                    print(f"Audio file not found at: {audio_path}")
                return False
        except Exception as e:
            print(f"Error uploading files: {str(e)}")
            return False

    def get_available_dates(self):
        """Get list of available analysis dates"""
        try:
            print(f"Listing blobs in bucket: {self.bucket_name}")
            print(f"Using prefix: text_archive/IL2/")
            
            # List all JSON files in text_archive
            blobs = self.storage_client.list_blobs(
                self.bucket_name, 
                prefix="text_archive/IL2/"
            )
            
            dates = []
            blob_list = list(blobs)  # Convert iterator to list
            print(f"Found {len(blob_list)} blobs")
            
            for blob in blob_list:
                print(f"Processing blob: {blob.name}")
                # Extract date from filename (format: text_archive/IL2/IL2_20250126_152118_log.json)
                parts = blob.name.split('/')[-1].split('_')  # Get last part of path and split
                if len(parts) >= 2:
                    date_str = parts[1]
                try:
                    date = datetime.strptime(date_str, '%Y%m%d')
                    dates.append(date)
                    print(f"Added date: {date}")
                except ValueError as ve:
                    print(f"Invalid date format in blob: {blob.name}, error: {str(ve)}")
                    continue
            
            # Sort dates in reverse chronological order
            sorted_dates = sorted(set(dates), reverse=True)
            print(f"Returning {len(sorted_dates)} unique dates")
            return sorted_dates
            
        except Exception as e:
            print(f"Error getting dates: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return []

    def load_analysis(self, date_str):
        """Load analysis data for a specific date
        
        Args:
            date_str: Date string in YYYYMMDD format
        """
        try:
            print(f"Loading analysis for date: {date_str}")
            
            # Find matching JSON file
            prefix = f"text_archive/IL2/IL2_{date_str}"
            print(f"Looking for files with prefix: {prefix}")
            
            blobs = self.storage_client.list_blobs(
                self.bucket_name,
                prefix=prefix
            )
            
            matching_blobs = list(blobs)
            print(f"Found {len(matching_blobs)} matching blobs")
            
            if not matching_blobs:
                return None
                
            # Download and parse JSON
            blob = matching_blobs[0]
            print(f"Using blob: {blob.name}")
            
            json_str = blob.download_as_string()
            data = json.loads(json_str)
            print(f"Loaded data with timestamp: {data.get('timestamp')}")
            
            return data
            
        except Exception as e:
            print(f"Error loading analysis: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    def get_audio_url(self, timestamp):
        """Get signed URL for audio file
        
        Args:
            timestamp: Timestamp string from analysis data
        """
        try:
            # List all audio files to debug
            print("Listing all blobs in bucket:")
            all_blobs = list(self.storage_client.list_blobs(self.bucket_name))
            for b in all_blobs:
                print(f"Found blob: {b.name}")
            
            # Try to find the audio file
            audio_path = f"audio/IL2/IL2_{timestamp}_analysis.mp3"
            print(f"Looking for audio file: {audio_path}")
            
            blob = self.bucket.blob(audio_path)
            exists = blob.exists()
            print(f"Audio file exists: {exists}")
            
            if not exists:
                return None
                
            # Generate signed URL that expires in 1 hour
            url = blob.generate_signed_url(
                version="v4",
                expiration=3600,  # 1 hour
                method="GET"
            )
            print(f"Generated signed URL: {url}")
            return url
            
        except Exception as e:
            print(f"Error getting audio URL: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

def upload_archive_to_cloud():
    """Utility function to upload IL2 archive files to cloud storage"""
    storage = CloudStorage()
    
    # Process IL2 files from text_archive and audio from IL2 directory
    json_dir = os.path.join("archive", "text_archive", "IL2")
    audio_dir = os.path.join("archive", "IL2")
    
    if not os.path.exists(json_dir):
        print(f"IL2 text_archive directory not found at: {json_dir}")
        return
        
    if not os.path.exists(audio_dir):
        print(f"IL2 audio directory not found at: {audio_dir}")
        return
        
    # Get all JSON files from text_archive/IL2
    for file in os.listdir(json_dir):
        if file.endswith("_log.json"):
            # Upload JSON file
            json_path = os.path.join(json_dir, file)
            
            # Find corresponding audio file
            parts = file.split('_')  # IL2_20250126_173220_log.json
            if len(parts) >= 3:
                timestamp = f"{parts[1]}_{parts[2]}"  # 20250126_173220
                audio_path = os.path.join(audio_dir, f"IL2_{timestamp}_analysis.mp3")
                print(f"Looking for audio file at: {audio_path}")
            
            # Upload both JSON and audio files
            if storage.upload_analysis(json_path, audio_path):
                print(f"Uploaded JSON: {file}")
                print(f"Uploaded Audio: {os.path.basename(audio_path)}")
            else:
                print(f"Failed to upload files for timestamp {timestamp}")

if __name__ == "__main__":
    # Run this to upload entire archive
    upload_archive_to_cloud()
