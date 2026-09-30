import asyncio
import streamlit as st
import pandas as pd
import edge_tts
import whisper
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Advanced Video to Myanmar Auto-Dubbing", layout="wide")

st.title("🎬 Video to Myanmar Subtitle & Natural Voice Dubbing")
st.write("သဘာဝကျသော မိန်းကလေး/ယောက်ျားလေး အသံများနှင့် အလိုအလျောက် မြန်မာဘာသာပြန် အသံဖိုင်ထုတ်စနစ်။")

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

with st.spinner("AI Whisper Model ကို ချိတ်ဆက်နေပါပြီ..."):
    model = load_whisper_model()

async def generate_single_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def smart_translate(text):
    text_clean = text.strip()
    if not text_clean:
        return text
        
    text_lower = text_clean.lower()
    
    # Custom Context & Correct Translation Dictionary
    custom_dict = {
        "则剑士已经开始了": "ဓားပြိုင်ပွဲ စတင်နေပါပြီ",
        "我来 我来 知道了": "ငါလာပြီ၊ ငါသိပြီ",
        "站住": "ရပ်လိုက်စမ်း",
        "对不起啊": "တောင်းပန်ပါတယ်",
        "别急我": "ငါ့ကို မစိုးရိမ်ပါနဲ့",
        "wan le": "ပြီးသွားပြီ / ခက်ပြီ",
        "完 了": "ပြီးသွားပြီ",
        "wán le": "ပြီးသွားပြီ"
    }
    
    for key, val in custom_dict.items():
        if key in text_lower or key in text_clean:
            return val
            
    try:
        translated = GoogleTranslator(source='auto', target='my').translate(text_clean)
        if translated:
            translated = translated.replace("ဓားသမား", "ဓားပြိုင်ပွဲ")
            return translated
    except Exception:
        pass
        
    try:
        translated = GoogleTranslator(source='zh-CN', target='my').translate(text_clean)
        if translated:
            translated = translated.replace("ဓားသမား", "ဓားပြိုင်ပွဲ")
            return translated
    except Exception:
        pass
        
    return text_clean

# Voice Options
voice_options = {
    "မြန်မာ - မိန်းကလေးသံ (NilarNeural - Natural)": "my-MM-NilarNeural",
    "မြန်မာ - ယောက်ျားလေးသံ (ThihaNeural - Natural)": "my-MM-ThihaNeural",
}

selected_voice_label = st.selectbox("🎙️ အဓိက အသံအမျိုးအစား ရွေးချယ်ရန် (Voice Selection)", list(voice_options.keys()))
chosen_voice = voice_options[selected_voice_label]

uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင် တင်ပါ (MP4, MKV)", type=["mp4", "mkv"])

if uploaded_file is not None:
    input_video_path = "temp_input.mp4"
    with open(input_video_path, "wb") as f:
        f.write(uploaded_file.read())
    
    st.video(input_video_path)
    
    with st.spinner("⏳ ဗီဒီယိုကို စစ်ဆေးနေသည်... စာသားများထုတ်ယူပြီး မြန်မာလို အလိုအလျောက် ဘာသာပြန်နေပါပြီ။"):
        result = model.transcribe(input_video_path)
        segments = result.get("segments", [])
        
        data = []
        for i, seg in enumerate(segments):
            start_time = str(int(seg['start']))
            end_time = str(int(seg['end']))
            orig_text = seg['text'].strip()
            
            my_trans = smart_translate(orig_text)
            
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
                "Myanmar Translation": smart_translate(text_content)
            }]
        
        df = pd.DataFrame(data)
        st.session_state["transcript_df"] = df

if "transcript_df" in st.session_state:
    st.subheader("📝 မြန်မာဘာသာပြန် စာသားများ တည်းဖြတ်ရန်")
    
    edited_df = st.data_editor(
        st.session_state["transcript_df"], 
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("✨ ရွေးချယ်ထားသော သဘာဝအသံဖြင့် အသံဖိုင် ထုတ်မည်"):
        with st.spinner("သဘာဝကျသော အသံဖိုင် ဖန်တီးနေပါပြီ... ခေတ္တစောင့်ဆိုင်းပေးပါ။"):
            output_audio_path = "final_output_audio.mp3"
            full_text_to_speak = " ။ ".join(edited_df["Myanmar Translation"].tolist())
            
            asyncio.run(generate_single_audio(full_text_to_speak, chosen_voice, output_audio_path))
            
            st.success("🎉 သဘာဝဆန်သော အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
            st.audio(output_audio_path)
            
            with open(output_audio_path, "rb") as file:
                st.download_button(
                    label="📥 အသံဖိုင်ကို သိမ်းဆည်းရန် (Download)",
                    data=file,
                    file_name="myanmar_natural_dubbed.mp3",
                    mime="audio/mp3"
                )
