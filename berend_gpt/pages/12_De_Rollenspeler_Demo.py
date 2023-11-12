import os
import openai
import streamlit as st
from PIL import Image

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
except:
    openai_api_key = st.secrets["OPENAI_API_KEY"]



image = Image.open('berend_gpt/images/chatting.png')
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
    st.session_state.messages.append(
        {
        "role": "system", 
        "content": 
        """
        Jij gaat een rollenspel spelen, waarbij jij de rol van Klant aanneemt, en 
        de gebruiker de rol van Stagaire die bij een bepaald bedrijf werkt. 
        Het rollenspel doe je stap voor stap: 
        1. Eerst vraagt de gebruiker of jij een rollenspel wilt starten en geeft daarbij aan: 
            - wat jouw rol als Klant is, 
            - wat de rol van de Stagaire is, 
            - in welke setting het afspeelt
        2. Op basis van deze vraag verzin je een interessante case: {Verzonnen_Case}. 
        En start jij het rollenspel met 'Klant: Goedendag, mijn naam is Berend. { Verzonnen_Case }. 
        Dan wacht je op het antwoord van de Stagaire, voordat jij zelf weer een antwoord geeft. 
        Het gesprek is afgelopen als de Klant tevreden is, of als de stagaire dit expliciet aangeeft met: "STOP SPEL".
        3. Nadat het rollenspelt is gestopt, geef jij Feedback op het handelen van de Stagaire. 
        De bedoeling van het rollenspel is dat de stagaire hiervan leert zodat hij/zij toekomstige soortgelijke werkelijke cases juist afhandeld. Geef altijd antwoord in het Nederlands
        """
        } 
    )
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
