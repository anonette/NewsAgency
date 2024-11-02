import os
import shutil

def prepare_deployment():
    """Prepare text_archive for Streamlit Cloud deployment"""
    # Create pages directory if it doesn't exist
    if not os.path.exists('pages'):
        os.makedirs('pages')
        
    # Create text_archive directory inside pages
    pages_archive = os.path.join('pages', 'text_archive')
    if not os.path.exists(pages_archive):
        os.makedirs(pages_archive)
    
    # Copy country folders
    for country in ['IL', 'LB', 'IR', 'CZ']:
        src = os.path.join('text_archive', country)
        dst = os.path.join(pages_archive, country)
        
        if os.path.exists(src):
            # Remove existing destination if it exists
            if os.path.exists(dst):
                shutil.rmtree(dst)
            # Copy the folder
            shutil.copytree(src, dst)
            print(f"Copied {country} folder")

if __name__ == '__main__':
    print("Preparing files for deployment...")
    prepare_deployment()
    print("\nDone! Files are ready for Streamlit Cloud deployment.")
    print("Make sure to commit and push these changes to your repository.")
