# Thai + English Text to MP3

Streamlit app using Google gTTS, with automatic Thai/English segment detection, MP3 playback and download.

## Run locally

1. Install Python 3.10+ and FFmpeg (ensure `ffmpeg` and `ffprobe` are on PATH).
2. In this directory:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit (usually http://localhost:8501).

## Streamlit Community Cloud

Push `app.py`, `requirements.txt`, and `packages.txt` to a GitHub repository. Deploy with `app.py` as the entry point. `packages.txt` installs FFmpeg on Streamlit Community Cloud.

## Notes

- Internet connection is required to generate audio; gTTS uses an online Google Translate speech service.
- gTTS is **not** Microsoft Neural Voice, and may have request limits or temporary outages.
- Alternating languages may sound discontinuous because each language segment is synthesized separately.
- The app processes up to 3,000 characters per request.
