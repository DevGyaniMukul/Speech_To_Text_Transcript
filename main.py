import streamlit as st
import whisper
from gtts import gTTS
import csv
import tempfile
import os

# --- Model Loading ---
# This decorator tells Streamlit to load this object only once across all user sessions.
@st.cache_resource
def load_whisper_model(model_name="base"):
    """
    Loads the Whisper model. Caching ensures it only loads once,
    saving memory and startup time.
    """
    try:
        # Note: Using "tiny" might be necessary if "base" exceeds memory limits on free hosting.
        return whisper.load_model(model_name)
    except Exception as e:
        st.error(f"Error loading Whisper model. Check your dependencies and available memory: {e}")
        st.stop()

# Load model globally on app startup
model = load_whisper_model("base") 

st.set_page_config('Speech-Text', page_icon='📣')

# === Title ===
st.title("🎙️ All-in-One Speech-to-Text & Text-to-Speech App")
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

    # Use a temporary directory for secure, system-friendly file handling
    with tempfile.TemporaryDirectory() as tmpdir:
        st.info(f"Processing {len(uploaded_files)} file(s). This may take a moment.")
        
        for i, uploaded_file in enumerate(uploaded_files, start=1):
            filename_stem = os.path.splitext(uploaded_file.name)[0]
            
            # 1. Define input path and save uploaded file to the temporary directory
            input_filepath = os.path.join(tmpdir, uploaded_file.name)
            with open(input_filepath, "wb") as f:
                f.write(uploaded_file.read())

            try:
                # 2. Transcribe using local Whisper
                # This call now uses the full path in the temp directory, solving file access issues.
                with st.spinner(f"Transcribing {uploaded_file.name} with Whisper..."):
                    result = model.transcribe(input_filepath)
                
                transcript = result["text"]
                
                # Add to CSV data
                transcripts.append([i, uploaded_file.name, transcript])

                # Show results
                st.subheader(f"File {i}: {uploaded_file.name}")
                st.write(transcript)

                # 3. TTS with gTTS
                tts_filename = f"{filename_stem}_tts.mp3"
                tts_filepath = os.path.join(tmpdir, tts_filename)
                
                tts = gTTS(transcript)
                tts.save(tts_filepath)
                
                # Display and download TTS audio
                st.audio(tts_filepath)
                with open(tts_filepath, "rb") as audio_file:
                    st.download_button(
                        label=f"Download TTS for {uploaded_file.name}",
                        data=audio_file,
                        file_name=tts_filename,
                        mime="audio/mp3"
                    )

            except Exception as e:
                # Provide a more user-friendly error message for the FFmpeg/Whisper issue
                st.error(
                    f"An error occurred while transcribing {uploaded_file.name}. "
                    "This often happens because a dependency (like FFmpeg) is missing or cannot be executed. "
                    "Ensure 'ffmpeg-python' and 'pydub' are in your requirements.txt."
                    f"Full error: {e}"
                )
                
        # 4. Save combined CSV
        st.markdown("---")
        st.subheader("Combined Transcripts")
        csv_filename = "all_transcripts.csv"
        csv_filepath = os.path.join(tmpdir, csv_filename)

        with open(csv_filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Number", "Filename", "Transcript"])
            writer.writerows(transcripts)

        with open(csv_filepath, "rb") as f:
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
        # Use temp directory for custom TTS generation too
        with tempfile.TemporaryDirectory() as tmpdir_custom:
            try:
                custom_tts = gTTS(custom_text, lang=accent)
                custom_filename = "custom_tts.mp3"
                custom_filepath = os.path.join(tmpdir_custom, custom_filename)
                custom_tts.save(custom_filepath)

                st.audio(custom_filepath)
                with open(custom_filepath, "rb") as audio_file:
                    st.download_button(
                        label="Download Custom TTS",
                        data=audio_file,
                        file_name=custom_filename,
                        mime="audio/mp3"
                    )
            except Exception as e:
                st.error(f"Error generating custom TTS: {e}")
    else:
        st.warning("Please enter some text first!")

st.markdown("---")
st.caption("""
✨Made by Mukul Sapra | [Github](https://github.com/DevGyaniMukul) | [LinkedIn](https://www.linkedin.com/in/mukul-sapra-ba31b3372/) | [Gmail](mukulsapra1234@gmail.com)
""")
