import asyncio
import streamlit as st
import pandas as pd
import edge_tts
import whisper
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Video Subtitle & Dubbing Generator", layout="wide")

st.title("🎬 Video to Myanmar Subtitle & Dubbing Editor")
st.write("ဗီဒီယိုဖိုင် တင်ပါ၊ စာသားများထုတ်ယူပြီး မြန်မာလို အမှန်တကယ် ဘာသာပြန်ပေးပါမည်။")

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

with st.spinner("AI Whisper Model ကို ချိတ်ဆက်နေပါပြီ..."):
    model = load_whisper_model()

async def generate_audio(text, output_path, voice="my-MM-NilarNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def translate_to_myanmar(text):
    text_lower = text.lower().strip()
    
    # Custom Slang / Phrase Dictionary
    slang_dict = {
        "wan le": "ပြီးသွားပြီ / ခက်ပြီ",
        "完 了": "ပြီးသွားပြီ / အလုပ်ဖြစ်ပြီ",
        "wán le": "ပြီးသွားပြီ / ခက်ပြီ",
        "omg": "အိုဘုရားရေ",
        "lol": "ဟားဟား",
        "wtf": "ဘာဖြစ်တာလဲကွာ",
        "bro": "သူငယ်ချင်း",
        "aiya": "အားယား (သေပါပြီ)",
        "哎呀": "အားယား (သေပါပြီ)"
    }
    
    for key, val in slang_dict.items():
        if key in text_lower:
            return f"{text} ({val})"
            
    try:
        translated = GoogleTranslator(source='auto', target='my').translate(text)
        return translated if translated else text
    except Exception as e:
        return text

uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ (MP4, MKV)", type=["mp4", "mkv"])

if uploaded_file is not None:
    input_video_path = "temp_input.mp4"
    with open(input_video_path, "wb") as f:
        f.write(uploaded_file.read())
    
    st.video(input_video_path)
    
    if st.button("🚀 ဗီဒီယိုမှ စာသားခွဲထုတ်ပြီး မြန်မာလို ဘာသာပြန်မည်"):
        with st.spinner("ဗီဒီယိုကို စစ်ဆေးပြီး ဘာသာပြန်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပေးပါ။"):
            result = model.transcribe(input_video_path)
            segments = result.get("segments", [])
            
            data = []
            for i, seg in enumerate(segments):
                start_time = str(int(seg['start']))
                end_time = str(int(seg['end']))
                orig_text = seg['text'].strip()
                
                my_trans = translate_to_myanmar(orig_text)
                
                data.append({
                    "No.": i + 1,
                    "Start": start_time,
                    "End": end_time,
                    "Original Text": orig_text,
                    "Myanmar Translation": my_trans
                })
            
            if not data:
                text_content = result.get("text", "")
                data = [{
                    "No.": 1,
                    "Start": "0",
                    "End": "5",
                    "Original Text": text_content,
                    "Myanmar Translation": translate_to_myanmar(text_content)
                }]
            
            df = pd.DataFrame(data)
            st.session_state["transcript_df"] = df
            st.success("✅ စာသားခွဲထုတ်ခြင်းနှင့် မြန်မာလို ဘာသာပြန်ဆိုခြင်း ပြီးစီးပါပြီ!")

if "transcript_df" in st.session_state:
    st.subheader("📝 မြန်မာဘာသာပြန် စာသားများ တည်းဖြတ်ရန်")
    
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
