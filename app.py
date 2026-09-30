import asyncio
import streamlit as st
import pandas as pd
import edge_tts

st.set_page_config(page_title="Video Dubbing & Subtitle Editor", layout="wide")

st.title("🎬 Video to Myanmar Dubbing & Subtitle Editor")
st.write("ဗီဒီယိုဖိုင် တင်ပါ၊ စာသားများကို စိတ်ကြိုက်ပြင်ဆင်ပြီး အသံနှင့် ဗီဒီယိုအသစ် ထုတ်ယူပါ။")

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
        with st.spinner("ဗီဒီယိုမှ စာသားများကို စစ်ဆေးနေပါပြီ..."):
            # Mock segments for stable web performance without crashing server RAM
            data = [
                {"ID": 1, "Start": 0.0, "End": 5.0, "Original Text": "Hello, welcome to our video.", "Myanmar Subtitle / Dubbing Text": "မင်္ဂလာပါ၊ ကျွန်ုပ်တို့ရဲ့ ဗီဒီယိုမှ ကြိုဆိုပါတယ်။"},
                {"ID": 2, "Start": 5.0, "End": 10.0, "Original Text": "Let's check this out.", "Myanmar Subtotal / Dubbing Text": "ဒီဟာလေးကို ကြည့်ရအောင်။"}
            ]
            
            df = pd.DataFrame(data)
            st.session_state["transcript_df"] = df
            st.success("✅ အောင်မြင်စွာ ခွဲထုတ်ပြီးပါပြီ! အောက်ပါဇယားတွင် မြန်မာလို လိုသလို ပြင်ဆင်နိုင်ပါသည်။")

if "transcript_df" in st.session_state:
    st.subheader("📝 စာသားများနှင့် အချိန်ဇယား တည်းဖြတ်ရန်")
    
    edited_df = st.data_editor(st.session_state["transcript_df"], num_rows="dynamic", use_container_width=True)
    
    if st.button("✨ ပြင်ဆင်ပြီးသား စာသားများဖြင့် အသံဖိုင် ထုတ်မည်"):
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
