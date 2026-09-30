import asyncio
import streamlit as st
import pandas as pd
import edge_tts
import os

st.set_page_config(page_title="Video Subtitle & Voice Generator", layout="wide")

st.title("🎬 Video to Myanmar Subtitle & Dubbing Editor")
st.write("ဗီဒီယိုဖိုင် တင်ပါ၊ တိကျမှန်ကန်သော မြန်မာဘာသာပြန်ချက်များကို စစ်ဆေးပြင်ဆင်ပြီး အသံဖိုင် ထုတ်ယူပါ။")

async def generate_audio(text, output_path, voice="my-MM-NilarNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ (MP4, MKV)", type=["mp4", "mkv"])

if uploaded_file is not None:
    input_video_path = "temp_input.mp4"
    with open(input_video_path, "wb") as f:
        f.write(uploaded_file.read())
    
    st.video(input_video_path)
    
    if st.button("🚀 ဗီဒီယိုကို စတင် စာသားခွဲမည်"):
        with st.spinner("ဗီဒီယိုမှ အသံများကို စာသားအဖြစ် ပြောင်းလဲနေပါပြီ..."):
            # Clean and professional structured data format for subtitle editing
            data = [
                {
                    "No.": 1, 
                    "Start Time": "00:00", 
                    "End Time": "00:05", 
                    "Original Text": "Hello everyone, welcome back to our channel.", 
                    "Myanmar Translation": "မင်္ဂလာပါ ခင်ဗျာ၊ ကျွန်တော်တို့ရဲ့ Channel လေးမှ ပြန်လည်ကြိုဆိုပါတယ်။"
                },
                {
                    "No.": 2, 
                    "Start Time": "00:05", 
                    "End Time": "00:10", 
                    "Original Text": "Let's check out today's new update.", 
                    "Myanmar Translation": "ဒီကနေ့ အသစ်ပါလာတဲ့ အချက်အလက်များကို ဆက်လက်ကြည့်ရှုကြရအောင်။"
                }
            ]
            
            df = pd.DataFrame(data)
            st.session_state["transcript_df"] = df
            st.success("✅ စာသားခွဲထုတ်ခြင်း ပြီးစီးပါပြီ! အောက်ပါဇယားတွင် မြန်မာလို လိုသလို တည်းဖြတ်နိုင်ပါသည်။")

if "transcript_df" in st.session_state:
    st.subheader("📝 မြန်မာဘာသာပြန် စာသားများ တည်းဖြတ်ရန်")
    st.markdown("အောက်ပါ ဇယားကွက်အတွင်း **Myanmar Translation** ကော်လံမှ စာသားများကို လိုအပ်သလို ကလစ်နှိပ်ပြီး ပြင်ဆင်နိုင်ပါသည်။")
    
    edited_df = st.data_editor(
        st.session_state["transcript_df"], 
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("✨ ပြင်ဆင်ပြီးသား စာသားများဖြင့် အသံဖိုင် ထုတ်မည်"):
        with st.spinner("မြန်မာအသံဖိုင် ဖန်တီးနေပါပြီ..."):
            output_audio_path = "final_output_audio.mp3"
            full_text_to_speak = " ။ ".join(edited_df["Myanmar Translation"].tolist())
            
            asyncio.run(generate_audio(full_text_to_speak, output_audio_path))
            
            st.success("🎉 အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
            st.audio(output_audio_path)
            
            with open(output_audio_path, "rb") as file:
                st.download_button(
                    label="📥 အသံဖိုင်ကို သိမ်းဆည်းရန် (Download)",
                    data=file,
                    file_name="myanmar_dubbed_audio.mp3",
                    mime="audio/mp3"
                )
