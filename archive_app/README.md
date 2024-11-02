# Middle East Pulse News Agency

## Overview
A Streamlit application that displays news analysis and trends from various Middle Eastern countries, featuring audio commentary and trend analysis.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run main_app.py
```

Note: No secrets or credentials are required as the application uses direct HTTP access to files.

## File Structure
The application expects files to be hosted on an HTTP server (default: http://95.216.199.241:8080/) with the following structure:

```
server_root/
├── IL/
│   ├── IL_20240101_log.json
│   └── IL_20240101_analysis.mp3
├── LB/
│   ├── LB_20240101_log.json
│   └── LB_20240101_analysis.mp3
├── IR/
│   ├── IR_20240101_log.json
│   └── IR_20240101_analysis.mp3
└── CZ/
    ├── CZ_20240101_log.json
    └── CZ_20240101_analysis.mp3
```

### File Naming Convention
- JSON files: `{country_code}_{YYYYMMDD}_log.json`
- MP3 files: `{country_code}_{YYYYMMDD}_analysis.mp3`

## JSON File Format
Each JSON file should contain:
```json
{
    "headlines": [
        "Headline 1",
        "Headline 2"
    ],
    "trends": [
        {
            "title": "Trend Title",
            "related": [
                "Related Search 1",
                "Related Search 2"
            ]
        }
    ],
    "analysis": "Optional analysis text"
}
