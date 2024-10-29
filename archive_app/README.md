# Trends Analysis Archive

A Streamlit app that provides access to historical analyses comparing official news headlines with real search trends.

## Deployment to Streamlit Cloud

1. Create a new repository on GitHub:
   - Create a new repository
   - Push the contents of this directory to the repository

2. Deploy on Streamlit Community Cloud:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set the main file path as `streamlit_app.py`
   - Click "Deploy"

## File Structure

```
archive_app/
├── streamlit_app.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── README.md            # Documentation
├── archive/             # Audio files
│   └── [country]/      # Audio files by country
└── text_archive/        # JSON data files
    └── [country]/      # JSON files by country
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run streamlit_app.py
