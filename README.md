# Thai + English Google gTTS — Streamlit

Fixes the Python `audioop` / `pyaudioop` import error by **removing pydub** and using the system `ffmpeg` executable directly to concatenate MP3 clips.

## Deploy on Streamlit Community Cloud

Upload these **three files into the repository root** (alongside README.md):

- `app.py` (replace existing file)
- `requirements.txt` (replace existing file)
- `packages.txt` (replace existing file)

Commit changes on branch `main`. The existing Streamlit deployment will normally redeploy automatically. No new Streamlit app is needed.

## Local run

Install Python and FFmpeg (available on PATH), then:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Google gTTS requires internet access. This release is syntax-checked but cannot be end-to-end tested without network access to Google TTS and the Streamlit server.
