import os
import shutil
from pathlib import Path

def prepare_deployment():
    """Prepare text_archive for Streamlit Cloud deployment"""
    # Get the absolute path to the pages directory
    pages_dir = Path('pages').absolute()
    
    # Create pages directory if it doesn't exist
    pages_dir.mkdir(exist_ok=True)
    
    # Create text_archive directory inside pages
    pages_archive = pages_dir / 'text_archive'
    pages_archive.mkdir(exist_ok=True)
    
    print(f"Creating archive in: {pages_archive}")
    
    # Copy country folders and their contents
    for country in ['IL', 'LB', 'IR', 'CZ']:
        # Source paths
        src_json = Path('text_archive') / country
        src_audio = Path('archive') / country
        
        # Destination path
        dst = pages_archive / country
        
        print(f"\nProcessing {country}:")
        print(f"JSON source: {src_json}")
        print(f"Audio source: {src_audio}")
        print(f"Destination: {dst}")
        
        if src_json.exists():
            # Remove existing destination if it exists
            if dst.exists():
                shutil.rmtree(dst)
            # Copy the folder
            shutil.copytree(src_json, dst)
            print(f"Copied {country} JSON files")
            
            # Copy any audio files if they exist
            if src_audio.exists():
                for file in os.listdir(src_audio):
                    if file.endswith('_analysis.mp3'):
                        src_file = src_audio / file
                        dst_file = dst / file
                        shutil.copy2(src_file, dst_file)
                        print(f"Copied audio file: {file}")

if __name__ == '__main__':
    print("Preparing files for deployment...")
    prepare_deployment()
    print("\nDone! Files are ready for Streamlit Cloud deployment.")
    print("\nNext steps:")
    print("1. Check the pages/text_archive directory")
    print("2. Run 'streamlit run streamlit_app.py' to test locally")
    print("3. If everything works, commit and push to deploy")
