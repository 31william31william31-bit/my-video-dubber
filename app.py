import os
import asyncio
import streamlit as st
import pandas as pd
import edge_tts
import whisper

st.set_page_config(page_title="Video to Myanmar Dubbing & Subtitle Editor", layout="wide")

st.title("🎬 AI Video Dubbing & Subtitle Editor (Myanmar)")
st.write("ဗီဒီယိုတင်ပါ၊ အလိုအလျောက် ဘာသာပြန်ပြီး စာသားများကို စိတ်ကြိုက်ပြင်ဆင်ကာ အသံဖိုင်ထုတ်ယူပါ။")

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()

async def generate_audio(text, output_path, voice="my-MM-NilarNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ (MP4, MKV, AVI)", type=["mp4", "mkv", "avi"])

if uploaded_file is not None:
    input_video_path = "temp_input.mp4"
    with open(input_video_path, "wb") as f:
        f.write(uploaded_file.read())
    
    st.video(input_video_path)
    
    if st.button("🚀 ဗီဒီယိုကို စတင် ဘာသာပြန်ပြီး အသံခွဲမည်"):
        with st.spinner("AI ဖြင့် အသံများကို စစ်ဆေးနေပါပြီ... ခဏစောင့်ပေးပါ။"):
            # Moviepy ကို မသုံးဘဲ Whisper ဖြင့် တိုက်ရိုက် အသံထုတ်ယူခြင်း
            result = model.transcribe(input_video_path)
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
            st.success("✅ အောင်မြင်စွာ ခွဲထုတ်ပြီးပါပြီ! အောက်ပါဇယားတွင် စာသားများကို လိုသလို ပြင်ဆင်နိုင်ပါသည်။")

if "transcript_df" in st.session_state:
    st.subheader("📝 စာသားများနှင့် အချိန်ဇယား တည်းဖြတ်ရန်")
    st.info("'Myanmar Subtitle / Dubbing Text' ကော်လံထဲတွင် မြန်မာလို ဘန်းစကားများ၊ လိုအပ်သည်များကို ဝင်ရောက်ပြင်ဆင်နိုင်ပါသည်။")
    
    edited_df = st.data_editor(st.session_state["transcript_df"], num_rows="dynamic", use_container_width=True)
    
    if st.button("✨ ပြင်ဆင်ပြီးသား စာသားများဖြင့် အသံအသစ် ထုတ်မည်"):
        with st.spinner("အသံအသစ်များ ဖန်တီးနေပါပြီ..."):
            output_audio_path = "final_output_audio.mp3"
            full_text_to_speak = " . ".join(edited_df["Myanmar Subtitle / Dubbing Text"].tolist())
            
            asyncio.run(generate_audio(full_text_to_speak, output_audio_path))
            
            st.success("🎉 အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
            st.audio(output_audio_path)
            
            with open(output_audio_path, "rb") as file:
                st.download_button(
                    label="📥 အသံဖိုင်ကို သိမ်းဆည်းရန် (Download)",
                    data=file,
                    file_name="dubbed_audio.mp3",
                    mime="audio/mp3"
                )
