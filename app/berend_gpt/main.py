import os
import streamlit as st
from PIL import Image
import openai
from streamlit.logger import get_logger
# import berend_gpt as app

from berend_gpt.ui import (
    wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from berend_gpt.core.caching import bootstrap_caching
from berend_gpt.core.parsing import read_file
from berend_gpt.core.chunking import chunk_file
from berend_gpt.core.embedding import embed_files
from berend_gpt.core.qa import query_folder
from berend_gpt.core.utils import get_llm


LOGGER = get_logger(__name__)
print(str(__name__))

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
except:
    openai_api_key = st.secrets["OPENAI_API_KEY"]

# st.session_state.get("OPENAI_API_KEY")

image = Image.open("/images/producttoer.jpeg")

# from berend_gpt.components.sidebar import sidebar



EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL_LIST = ["gpt-3.5-turbo", "gpt-4"]

# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")


########### Pagina Indeling

st.set_page_config( 
            page_title=":genie:Berend-Botje Skills",
            page_icon=" :genie: ",
            layout="wide",
            initial_sidebar_state="collapsed",
            menu_items={
                'Get Help': 'https://mboscrum.com/mbowoordle',
                'Report a bug':'https://mboscrum.com/mbowoordle',
                'About': "# Berend in development -  een *extremely* cool app!"
                }
            )

# In twee kolommen

col1, col2 = st.columns(2)
with col1:
    st.header(":genie: Welkom bij Berend-Botje")     
    st.markdown("""
    ##### Berend-Botje is een slimme AI assistent met skills die perfect aansluiten bij het principe van **Smart Working** ##### """)
    st.markdown("""
    ##### Berend-Botje Basis:male_mage:, een ChatGPT kloon, staat altijd voor je klaar om snel je vragen te beantwoorden. Heb je hulp nodig bij een specifieke taak, dan vraag je Berend om bijpassende Skills in de Basis in te pluggen. 
    **Jij kiest dus op basis van je klus de bijpassende skills voor Berend**  
    :rotating_light: Belangrijk voordeel van Berend-Botje ten opzichte van andere aanbieders is dat niet alleen jouw persoonlijke informatie veilig is, maar ook de informatie van je werk, binnen jouw eigen omgeving blijft!  *Nadat een sessie wordt afgesloren blijft er geen data achter die wij of derden kunnen gebruiken!*
    >> Onze AI Skills zijn allen **Powered By OpenAI**
    ------------------------------------
    """ 
    )

with col2:
    st.image(image, caption=None, use_column_width=True, clamp=True, channels="RGB", output_format="auto")
    
    # st.sidebar.success("Kies één van Berend's skills")
    # st.markdown(""" ##### Voorbeelden
    # **1. [De Lesplanner](Lesplan_Demo)**
    # **2. [De Notulist](Mapping_Demo)**
    # **3. [De Dataanalist](DataFrame_Demo)**
    # **4. [De Datavormgever](Plotting_Demo)**
    # **5. [De Chatbot](Chat_Demo)**
    # **6. [De Samenvatter](Samenvatter_Demo)**
    # **9. [De Broodjesbakker](Broodje_Berend_Demo)**
    # """
    # ) 

    
def maakLesplan( ):
    
    # Enable caching for expensive functions
    bootstrap_caching()
    
    # sidebar()
    
     # openai_api_key  
    
    # openai_api_key = st.session_state.get("OPENAI_API_KEY")
    
    
    if not openai_api_key:
        st.warning(
            "Enter your OpenAI API key in the sidebar. You can get a key at"
            " https://platform.openai.com/account/api-keys."
        )
    
    
    uploaded_file = st.file_uploader(
        " **:red[Upload een pdf, docx, of txt bestand]** ",
        type=["pdf", "docx", "txt"],
        help="Scanned documents are not supported yet!",
    )
    
    model: str = st.selectbox("Model", options=MODEL_LIST)  # type: ignore
    
    with st.expander("Advanced Options"):
        return_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
        show_full_doc = st.checkbox("Show parsed contents of the document")
    
    
    if not uploaded_file:
        st.stop()
    
    try:
        file = read_file(uploaded_file)
    except Exception as e:
        display_file_read_error(e, file_name=uploaded_file.name)
    
    chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)
    
    if not is_file_valid(file):
        st.stop()
    
    
    if not is_open_ai_key_valid(openai_api_key, model):
        st.stop()
    
    
    with st.spinner("Indexing document... This may take a while⏳"):
        folder_index = embed_files(
            files=[chunked_file],
            embedding=EMBEDDING if model != "debug" else "debug",
            vector_store=VECTOR_STORE if model != "debug" else "debug",
            openai_api_key=openai_api_key,
        )
    
    with st.form(key="qa_form"):
        query = st.text_area("Geef hier het onderwerp van de les, en wat je wilt dat de studenten na de les kunnen/weten. ")
        submit = st.form_submit_button("Submit")
    
    
    if show_full_doc:
        with st.expander("Document"):
            # Hack to get around st.markdown rendering LaTeX
            st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)
    
    
    if submit:
        if not is_query_valid(query):
            st.stop()
    
        # Output Columns
        query = "Dit is de vraag van de docent: " + str(query) + """ Maak nu een lesplan over het onderwerp en lesdoel die de docent in de vraag heeft genoemd, en gebruik  hier ook gerelateerde inhoud uit het ingelezen document voor.  Als de docent geen onderwerp heeft geformuleerd in de vraag,  dan vraag je daar om.  Ha niet zelf het onderwerp verzinnen. Als het lesdoel ontbreekt gebruik je een algemeen doel van elke les, en dat  is dat studenten de les begrepen moeten hebben, en eventueel het geleerde ook praktisch kunnen toepassen. Gebruik voor het lesplan een verscheidenheid aan lestechnieken en -modaliteiten, waaronder directe instructie, controleren op begrip (inclusief het verzamelen van bewijs met behulp van quizjes, formatieve toetsjes, rubricks, enz, discussies, een boeiende activiteit in de klas of een opdracht. Leg uit waarom je specifiek voor elk kiest.  Publiceer het lesplan in het  Markdown formaat, met duidelijke koppem, en bullets.  GEEF ALTIJD ANTWOORD IN HET NEDERLANDS! """
        
        answer_col, sources_col = st.columns(2)
        
        llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0)
        result = query_folder(
            folder_index=folder_index,
            query = "Jij bent een slimme Assistent Bot en je helpt docenten bij het maken van een lesplan voor 1 les.  " +  str(query),
            return_all=return_all_chunks,
            llm=llm,
        )
    
        with answer_col:
            st.markdown("#### Lesplan ")
            st.markdown(result.answer)
    
        with sources_col:
            st.markdown("#### Bronnen")
            for source in result.sources:
                st.markdown(source.page_content)
                st.markdown(source.metadata["source"])
                st.markdown("---")      

def geefRecept():
    response = ""
    st.markdown(" #### :bread: :male-cook: Het broodje van Berend :baguette_bread: :\n*waarom zou je moeilijk doen ....?* ")
    st.markdown(""" ##### Heb je rond deze tijd ook zo'n trek in een lekker broodje :sandwich: maar je hebt geen zin om de deur uit te gaan  :house: ? 
        **Dan heeft Berend's Broodje de oplossing.**
        - Stuur een foto van wat je in huis hebt: brood, beleg, sla, sausjes, ... wat je maar wilt 
        - Berend maakt dan een recept voor je om snel een heerlijk broodje te maken :cooking:  
        - Hij stuurt zelfs een foto mee, om je alvast lekker te maken
        **Eet smakelijk!!** 
        """ 
        )
       
    
    uploaded_file = st.file_uploader(
            "**:notebook: Hier je foto uploaden!**",
            type=["jpg"],
            help="Gescande documenten worden nog niet ondersteund! ",
    )
    
    
    # openai.api_key = st.secrets["OPENAI_API_KEY"]
    
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "system", "content": "Geef altijd antwoord in het Nederlands"})
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] != "system":
                st.markdown(message["content"])
    
    
    full_response =""
    
    if prompt := st.chat_input("Hoe gaat het?"):
        st.session_state.messages.append({"role": "user", "content": "Geef een recept voor een lekker broodje als ik deze spullen in huis heb:  " + prompt})
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
        response ==" " 
        
        print(full_response)
        
        
        if full_response == "":
            st.stop()
        
    
        try:
            with st.spinner("Bezig met het maken van de afbeelding... "):
    
                aprompt = """ Maak een foto van een broodje volgens dit recept """ + ' """ ' + str(full_response[0:700]) + ' """ '        
                myresponse = openai.Moderation.create(
                        input = aprompt,
                     )
                print(myresponse)
                
                for i in "  ", "-", "1-9", "\n":
                    aprompt = aprompt.replace(i," ")
    
                aprompt = aprompt.replace("  ", " ")
                print(aprompt)
    
    
                response = openai.Image.create( prompt=str(aprompt), n=1, size="1024x1024")        
                image_url = response['data'][0]['url']
            # image = Image.open(image_url)
            # st.image(image, caption="Heerlijk broodje met jouw ingredienten", width=256, use_column_width=False, clamp=True, channels="RGB", output_format="auto")
            # st.markdown("[Heerlijk broodje](" + str(image_url) + ")")
            
            st.image(image_url, caption=" ### Het heerlijke broodje is tot stand gekomen dankzij **powered by OpenAi, ChatGPT en DALE**", width=340 )
            # print(response['data'][0]['url'])
        except openai.error.OpenAIError as e:
            print(e.http_status)
            print(e.error)
        
    
    
    


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["###### De Lesplanner  ", " ###### De Notulist  ", " ###### De Dataanalist ######  ", "###### De Datavormgever ###### ", " ###### De Chatbot ###### ", " ###### De Samenvatter ", " ###### De Broodjesbakker "])
st.markdown("--------------------------------------------------- ")

with tab1:
    st.header("De Lesplanner :male-student: \n*waarom zou je moeilijk doen ....?*")
    st.markdown(""" ##### De Lesplanner :male-student:  helpt bij het plannen van een les. Geef Berend het onderwerp en doel van de les en hij maakt een lesplan.  Wil je ook content gebruiken? Voeg dan een document toe door het te slepen in onderstaand vak,  en Berend  neemt mee in het lesplan. """)
        
    st.markdown(
        """ 
            ##### Hoe werkt de :male-student: Lesplanner?  
            1. **:notebook: Upload een pdf, docx, of txt file📄**
            2. **:writing_hand: Vraag Berend om een lesplan te maken en geef daarbij duidelijk aan wat het *Onderwerp*,  en *Lesdoel* is. 
                    Zodat Berend weet wat de studenten na de les moeten weten/kunnen.** 
            3. **:golf: Klik dan op versturen, en Berend gaat aan de slag**            
        """
        )
        
    # if st.button( "**:blue[ :student: De lesplanner]** ", key="1" ):
    maakLesplan()

with tab2:
    
    geefRecept()
    
    




st.markdown("""
    :angel: :gray[ *Disclaimer Aan het gebruik, of resulaten van Berend-Botje Skills kunnen geen rechten worden verleend. Noch zijn wij aansprakelijk voor enig gevolg van dit gebruik. Bedenk dat de voorbeelden die hier getoond worden nog in een premature fase verkeren: het is werk onder constructie...* ]
    """
    )
