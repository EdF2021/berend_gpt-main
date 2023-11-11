import os
import openai
import streamlit as st
from PIL import Image

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
except:
    openai_api_key = st.secrets["OPENAI_API_KEY"]



image = Image.open('berend_gpt/images/chatachtergrond.png')
st.set_page_config(
        page_title=" : genie: Berend Skills",
        page_icon=" :genie: ",
        layout="wide",
        initial_sidebar_state="collapsed" )

col1, col2 = st.columns(2)

with col1:
        st.header(":genie: Berend Skills" )
        st.subheader(":male-teacher: De Rollenspeler -\n*waarom zou je moeilijk doen ....?* ")
        st.markdown(
                """ 
                ##### Dit is Berend's Rollenspeler. De Rollenspeler kan helpen bij het oefenen van bepaalde vaardigheden door middel van een rollenspel. Jij geeft aan welke rol Berend speelt, en welke rol jij hebt. 
                
                ###### Bijvoorbeeld: Berend speelt een klant, en jij een stagair die bij een kinderdagverblijf werkt. De Case zal in eerste instantie door Berend worden verzonnen. 
                """
        )
with col2:
        st.image(image, caption=None, width=240, use_column_width=True, clamp=True, channels="RGB", output_format="auto")
        st.markdown(""" """)



# openai.api_key = st.secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": """Jij gaat een rollenspel spelen, waarbij jij de rol van Klant aanneemt, en de gebruiker de rol van Stagair die bij een bepaald bedrijf werkt. Als de gebruiker je gevraagd heeft om het rollenspel te starten, begin jij het rollenspel als Klant en stel je een vraag op basis van eendoor jou verzonnen case, die past bij de de gegevens die de gebruiker in de vraag aan je heeft verstrekt. Je wacht dan op het antwoord van de Stagair. Je wacht dus na jouw antwoord/vraag altijd op respons van de stagiare. Geef altijd antwoord in het Nederlands"""})
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] != "system":
            st.markdown(message["content"])

if prompt := st.chat_input("Hoe gaat het?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
