import os
import openai
import streamlit as st
from PIL import Image

openai_api_key = st.secrets["OPENAI_API_KEY"]

image = Image.open("berend_gpt/images/broodje_achtergrond.png")
st.set_page_config(
    page_title="Berend-Botje Skills",
    page_icon=" :genie: ",
    layout="wide",
    initial_sidebar_state="collapsed",
)

response = ""

col1, col2 = st.columns(2)

with col1:
    st.header(" :genie: Berend-Botje Skills")
    st.subheader(
        " :bread: :male-cook: Het broodje van Berend :baguette_bread: :\n*waarom zou je moeilijk doen ....?* "
    )
    st.markdown(
        """ ##### Zin in een lekker :sandwich: broodje, gemaakt met de ingredienten die je in :house: hebt? 
    **Berend's Broodje kan je hierbij helpen**
    - Maak een foto van wat je aan eetbare spulleb in huis hebt: brood, beleg, ui, eieren, sla, sausjes, ... ja zelfs de inhoud van je koelkast.
    - Upload de foto hier
    - De AI van Berend-Botje verzint dan met deze ingredienten een recept voor je waarmee je het overheerlijke broodje maakt :cooking:
    - Met enig geluk zal de AI zelfs alvast je broodje op de foto zetten. *Met wisselend succes :smiley:* 
    - **Eet smakelijk!!** """
    )


with col2:
    st.image(
        image,
        caption=None,
        width=240,
        use_column_width=True,
        clamp=True,
        channels="RGB",
        output_format="auto",
    )


uploaded_file = st.file_uploader(
    "**:notebook: :red[Hier je foto uploaden!]**",
    type=["jpg, jpeg, png"],
    help="Op dit moment ondersteunen we alleen foto's in jpg, jpeg, png formaat ",
)

if not uploaded_file:
    st.stop()
    

openai.api_key = st.secrets["OPENAI_API_KEY"]

    

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(
        {
            "role": "system", 
            "content": "Je bent een behulpzame assistent bot, en je kan op basis van ingredienten recepten voor heerlijke broodjes maken."
        }
    )

full_response = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] != "system":
            st.markdown(message["content"])
        
if prompt := st.chat_input("Hoe gaat het?"):
    prompt = prompt + " zijn je ingredienten. Gebruik nu alleen deze ingredienten om een recept te maken voor een heerlijk broodje!" 
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # full_response = ""
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
if full_response == "":
    st.stop()
    
with st.spinner("Bezig met het maken van de afbeelding... "):
        aprompt = (
            """ Maak een foto van een broodje volgens dit recept """ + ' """ ' + str(full_response[0:900]) + ' """ ')
        myresponse = openai.Moderation.create(
            input=aprompt,
        )
        # st.write(myresponse)

        for i in "  ", "-", "1-9", "\n":
            aprompt = aprompt.replace(i, " ")

        aprompt = aprompt.replace("  ", " ")
        # print(aprompt)

        response = openai.Image.create(prompt=str(aprompt), n=1, size="1024x1024")
        image_url = response["data"][0]["url"]
        # st.write(response['data'][0]['url'])
                    
        st.image(image_url, caption=""" 
                ### Het heerlijke broodje is tot stand gekomen dankzij **powered by OpenAi, ChatGPT en DALE** """, width=340,
        )
    
