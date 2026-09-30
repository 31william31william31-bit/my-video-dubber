import asyncio
import streamlit as st
import pandas as pd
import edge_tts

st.set_page_config(page_title="Myanmar Voice & Subtitle Generator", layout="wide")

st.title("🎬 AI Myanmar Subtitle & Voice Generator")
st.write("စာသားများကို ထည့်သွင်းပြီး အမြန်ဆုံး အသံနှင့် စာတန်းများ ထုတ်ယူပါ။")

async def generate_audio(text, output_path, voice="my-MM-NilarNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

user_text = st.text_area("ဘာသာပြန်လိုသော သို့မဟုတ် ပြောလိုသော စာသားများကို ရိုက်ထည့်ပါ:", "ပြဿနာပဲ၊ နောက်ကျတော့မယ်။")

if st.button("✨ အသံဖိုင် ထုတ်ယူမည်"):
    if user_text:
        with st.spinner("အသံဖိုင် ဖန်တီးနေပါပြီ..."):
            output_audio_path = "output.mp3"
            asyncio.run(generate_audio(user_text, output_audio_path))
            
            st.success("🎉 အသံဖိုင် အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
            st.audio(output_audio_path)
            
            with open(output_audio_path, "rb") as f:
                st.download_button(
                    label="📥 အသံဖိုင်ကို သိမ်းဆည်းရန် (Download)",
                    data=f,
                    file_name="myanmar_voice.mp3",
                    mime="audio/mp3"
                )
