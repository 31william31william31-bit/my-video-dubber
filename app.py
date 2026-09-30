import os
import asyncio
import streamlit as st
import pandas as pd
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
import edge_tts
import whisper

st.set_page_config(page_title="Video to Myanmar Dubbing & Subtitle Editor", layout="wide")

st.title("🎬 AI Video Dubbing & Subtitle Editor (Myanmar)")
st.write("ဗီဒီယိုတင်ပါ၊ အလိုအလျောက် ဘာသာပြန်ပြီး စာသားများကို စိတ်ကြိုက်ပြင်ဆင်ကာ အသံအသစ်ထုတ်ယူပါ။")

# Whisper Model ကို Load လုပ်ရန်
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

# Edge TTS ဖြင့် အသံဖိုင်ထုတ်ရန် Async Function
async def generate_audio(text, output_path, voice="my-MM-NilarNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

# UI: Video Upload
uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ (MP4, MKV, AVI)", type=["mp4", "mkv", "avi"])

if uploaded_file is not None:
    input_video_path = "temp_input.mp4"
    with open(input_video_path, "wb") as f:
        f.write(uploaded_file.read())
    
    st.video(input_video_path)
    
    if st.button("🚀 ဗီဒီယိုကို စတင် ဘာသာပြန်ပြီး အသံခွဲမည်"):
        with st.spinner("AI ဖြင့် အသံများကို စစ်ဆေးနေပါပြီ... ခဏစောင့်ပေးပါ။"):
            video_clip = VideoFileClip(input_video_path)
            temp_audio_path = "temp_audio.mp3"
            video_clip.audio.write_audiofile(temp_audio_path, logger=None)
            
            result = model.transcribe(temp_audio_path)
            segments = result["segments"]
            
            data = []
            for i, seg in enumerate(segments):
                data.append({
                    "ID": i + 1,
                    "Start": round(seg["start"], 2),
                    "End": round(seg["end"], 2),
                    "Original Text": seg["text"].strip(),
                    "Myanmar Subtitle / Dubbing Text": seg["text"].strip()
                })
            
            df = pd.DataFrame(data)
            st.session_state["transcript_df"] = df
            st.session_state["video_duration"] = video_clip.duration
            st.success("✅ အောင်မြင်စွာ ခွဲထုတ်ပြီးပါပြီ! အောက်ပါဇယားတွင် စာသားများကို လိုသလို ပြင်ဆင်နိုင်ပါသည်။")

if "transcript_df" in st.session_state:
    st.subheader("📝 စာသားများနှင့် အချိန်ဇယား တည်းဖြတ်ရန်")
    st.info("'Myanmar Subtitle / Dubbing Text' ကော်လံထဲတွင် မြန်မာလို ဘန်းစကားများ၊ လိုအပ်သည်များကို ဝင်ရောက်ပြင်ဆင်နိုင်ပါသည်။")
    
    edited_df = st.data_editor(st.session_state["transcript_df"], num_rows="dynamic", use_container_width=True)
    
    if st.button("✨ ပြင်ဆင်ပြီးသား စာသားများဖြင့် အသံနှင့် ဗီဒီယိုအသစ် ပြန်ထုတ်မည်"):
        with st.spinner("အသံအသစ်များ ဖန်တီးပြီး ဗီဒီယိုနှင့် ပြန်လည်ပေါင်းစပ်နေပါပြီ..."):
            output_audio_path = "final_output_audio.mp3"
            full_text_to_speak = " . ".join(edited_df["Myanmar Subtitle / Dubbing Text"].tolist())
            
            asyncio.run(generate_audio(full_text_to_speak, output_audio_path))
            
            video_clip = VideoFileClip("temp_input.mp4")
            new_audio = AudioFileClip(output_audio_path)
            final_video = video_clip.set_audio(new_audio)
            
            output_video_path = "final_output_video.mp4"
            final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", logger=None)
            
            st.success("🎉 ဗီဒီယိုအသစ် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
            st.video(output_video_path)
            
            with open(output_video_path, "rb") as file:
                st.download_button(
                    label="📥 ဗီဒီယိုဖိုင်ကို သိမ်းဆည်းရန် (Download)",
                    data=file,
                    file_name="dubbed_video.mp4",
                    mime="video/mp4"
                )
