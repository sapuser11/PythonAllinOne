import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
from io import BytesIO

API_URL = "http://localhost:8000"

st.title("🤖 Anubhav Trainings Multimodal Assistant")
st.write("Upload images or record voice to interact with Anubhav Trainings Multimodal Assistant")

# Create tabs
tab1, tab2 = st.tabs(["📷 Image", "🎤 Voice"])

# Image Processing Tab
with tab1:
    st.header("Image Description")
    uploaded_image = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
        
        if st.button("Describe Image"):
            with st.spinner("Processing..."):
                files = {"file": uploaded_image}
                response = requests.post(f"{API_URL}/process-image", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Description:")
                    st.write(result["result"])
                else:
                    st.error("Error processing image")

# Voice Processing Tab
with tab2:
    st.header("Voice Input")
    st.write("Click the microphone to record your voice")
    
    audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=16000)
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        if st.button("Process Voice"):
            with st.spinner("Converting speech to text and processing..."):
                # Save audio to file
                audio_file = BytesIO(audio_bytes)
                files = {"file": ("recording.wav", audio_file, "audio/wav")}
                
                response = requests.post(f"{API_URL}/process-audio", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.success("Transcription:")
                        st.info(result.get("transcription", ""))
                        
                        st.success("Response:")
                        st.write(result.get("response", ""))
                else:
                    st.error("Error processing audio")

# Footer
st.markdown("---")
st.caption("Make sure FastAPI server is running on localhost:8000")