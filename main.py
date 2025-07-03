import streamlit as st
import whisper
from gtts import gTTS
import csv

# Load local Whisper model once
model = whisper.load_model("base")  # or "tiny" if you want very light

st.set_page_config('Speech-Text', page_icon='📣')

# === Title ===
st.title("🎙️ All-in-One Speech-to-Text & Text-to-Speech App (Local Whisper)")
st.header("📢 Upload audio/video files (.wav, .mp3, .mp4)")

# === Upload Files ===
uploaded_files = st.file_uploader(
    "Upload",
    type=["wav", "mp3", "mp4"],
    accept_multiple_files=True
)

# === Process Files ===
if uploaded_files:
    transcripts = []

    for i, uploaded_file in enumerate(uploaded_files, start=1):
        filename = uploaded_file.name

        # Save file locally
        with open(filename, "wb") as f:
            f.write(uploaded_file.read())

        # Transcribe using local Whisper
        result = model.transcribe(filename)
        transcript = result["text"]

        # Add to CSV data
        transcripts.append([i, filename, transcript])

        # Show results
        st.subheader(f"File {i}: {filename}")
        st.write(transcript)

        # TTS with gTTS
        tts_filename = f"{filename}_tts.mp3"
        tts = gTTS(transcript)
        tts.save(tts_filename)

        st.audio(tts_filename)
        with open(tts_filename, "rb") as audio_file:
            st.download_button(
                label=f"Download TTS for {filename}",
                data=audio_file,
                file_name=tts_filename,
                mime="audio/mp3"
            )

    # Save combined CSV
    csv_filename = "transcripts.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Number", "Filename", "Transcript"])
        writer.writerows(transcripts)

    with open(csv_filename, "rb") as f:
        st.download_button(
            label="📥 Download All Transcripts CSV",
            data=f,
            file_name=csv_filename,
            mime="text/csv"
        )

# === Custom Text-to-Speech ===
st.header("📝 Custom Text-to-Speech")

custom_text = st.text_area("Enter your custom text:")

accent = st.selectbox(
    "Choose accent:",
    ["en", "en-us", "en-uk", "en-au"]
)

if st.button("Generate TTS for Custom Text"):
    if custom_text.strip():
        custom_tts = gTTS(custom_text, lang=accent)
        custom_filename = "custom_tts.mp3"
        custom_tts.save(custom_filename)

        st.audio(custom_filename)
        with open(custom_filename, "rb") as audio_file:
            st.download_button(
                label="Download Custom TTS",
                data=audio_file,
                file_name=custom_filename,
                mime="audio/mp3"
            )
    else:
        st.warning("Please enter some text first!")

st.markdown("---")
st.caption("""
✨Made by Mukul Sapra | [Github](https://github.com/DevGyaniMukul) | [LinkedIn](https://www.linkedin.com/in/mukul-sapra-ba31b3372/) | [Gmail](mukulsapra1234@gmail.com)
""")
