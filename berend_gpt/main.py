import os
import streamlit as st
from PIL import Image
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

# print(str(__name__))

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
except:
    openai_api_key = st.secrets["OPENAI_API_KEY"]

# st.session_state.get("OPENAI_API_KEY")

image = Image.open("berend_gpt/images/producttoer.jpeg")

# from berend_gpt.components.sidebar import sidebar

EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL_LIST = ["gpt-3.5-turbo", "gpt-4"]

# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")


########### Pagina Indeling  ################

st.set_page_config( 
            page_title=" :genie: Berend-Botje Skills",
            page_icon=":genie:",
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
    ###### Berend-Botje is een slimme AI assistent met skills die perfect aansluiten bij het principe van **Smart Working** ###### """)
    st.markdown(
        """ Berend-Botje Basis:male_mage:, is een ChatGPT kloon en staat altijd voor je klaar om snel je vragen te beantwoorden. """)
    # st.link_button("Naar Berend-Botje Basis", 'https://berendgpt.streamlit.app/Chat_Demo/' )
    st.markdown(
        """**[De Chatbot](Chat_Demo)**
        >> Alle skills van Berend zijn **Powered By OpenAI**
        """ 
    )
with col2:
    st.image(image, caption=None, use_column_width=True, clamp=True, channels="RGB", output_format="auto")
    st.markdown(""" :question: Heb je hulp nodig bij een specifieke taak, dan vraag je Berend om een bijpassende skill bij de Basis te pluggen. 
    **Jij kiest op basis van je klus de bijpassende skills voor Berend.** [^1] """) 
    
st.markdown(""" :[^1]:rotating_light: *Belangrijk voordeel van Berend-Botje ten opzichte van andere aanbieders is dat jouw persoonlijke informatie, 
binnen jouw persoonlijke, eigen omgeving blijft!  Nadat een sessie wordt afgesloren blijft er dus geen data achter die wij of derden kunnen gebruiken!* 
""")
st.markdown("------------------------") 


 
def maakLesplan():
    uploaded_file = False
    chunked_file = ""
    file = ""
    files = ""
    folder_index = ""
    query = ""
    submit = ""
    llm = ""
    return_all = ""
    return_all_chunks = ""

        
    # Enable caching for expensive functions
    bootstrap_caching()
    
    # sidebar()
    
    # openai_api_key  
    
    # openai_api_key = st.session_state.get("OPENAI_API_KEY")
    
    
    uploaded_file = st.file_uploader(
        " **:red[Upload een pdf, docx, of txt bestand]** ",
        type=["pdf", "docx", "txt"],
        help="Scanned documents are not supported yet!",
    )
    
    model: str = st.selectbox("Model", options=MODEL_LIST)  # type: ignore
    
    with st.expander("Advanced Options"):
        return_all_chunks = st.checkbox("Toon alle chunks die tijdens het zoeken zijn opgehaald")
        show_full_doc = st.checkbox("Toon de volledige gepaseerde inhoud van het document")
    
    
    if not uploaded_file:
        st.stop()
        
    ############ Er is een bestand up geloaded ########
    
    try:
        file = read_file(uploaded_file)
    except Exception as e:
        display_file_read_error(e, file_name=uploaded_file.name)
    
    chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)
    
    if not is_file_valid(file):
        st.warning('Bestand is niet correct', icon="⚠️")
        st.stop()
    
    
    if not is_open_ai_key_valid(openai_api_key, model):
        st.stop()
    
    
    with st.spinner("Bezig met indexeren document... Dit kan even duren ⏳"):
        folder_index = embed_files(
            files=[chunked_file],
            embedding=EMBEDDING if model != "debug" else "debug",
            vector_store=VECTOR_STORE if model != "debug" else "debug",
            openai_api_key=openai_api_key,
        )
    
    with st.form(key="qa_form"):
        query = st.text_area("**Geef hier het onderwerp, en het doel van de les**")
        submit = st.form_submit_button("Maak het Lesplan")
    
    
    if show_full_doc:
        with st.expander("Document"):
            # Hack to get around st.markdown rendering LaTeX
            st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)
    
    
    if submit:
        if not is_query_valid(query):
            st.stop()
    
        # Output Columns
        query = "Jij bent een slimme Assistent Bot en je helpt docenten die willen dat je voor 1 les een lesplan maakt. Dit is de vraag van de docent: " + str(query)
        
        llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0.3)
        result = query_folder(
            folder_index=folder_index,
            query = query + """ Maak nu een lesplan voor 1 les over het onderwerp en lesdoel die de docent in de vraag heeft genoemd, 
                en gebruik ook wat er in het ingelezen document over dit onderwerp staat. Als de docent geen onderwerp heeft geformuleerd in de vraag stop je.
                En is je antwoord: 'Geef een onderwerp van de les op'. Je zerzint nooit zelf het onderwerp!!!  
                Als er geen lesdoel is genoemd gebruik je het een algemene doel van elke les, en dat  is dat studenten de les begrepen moeten hebben, en eventueel het geleerde ook praktisch kunnen toepassen. 
                Gebruik voor het lesplan een verscheidenheid aan lestechnieken en -modaliteiten, waaronder directe instructie, 
                controleren op begrip (inclusief het verzamelen van bewijs met behulp van quizjes, 
                formatieve toetsen, rubricks, discussies, een boeiende activiteit in de klas of een opdracht. 
                Leg uit waarom je specifiek voor elk kiest.  
                Publiceer het lesplan in Markdown formaat, met duidelijke koppen en bullets. GEEF ALTIJD ANTWOORD IN HET NEDERLANDS!"   """,
                return_all=return_all_chunks,
                llm=llm,
        )
        
        answer_col, sources_col = st.columns(2)
        with answer_col:
            st.markdown("#### Lesplan ")
            st.markdown(result.answer)
    
        with sources_col:
            if result.sources:
                st.markdown("#### Bronnen")
                for source in result.sources:
                    st.markdown(source.page_content)
                    st.markdown(source.metadata["source"])
                    st.markdown("---")
    


tab1, tab2, tab3, tab4, tab5 = st.tabs(["###### De Lesplanner", " ###### De Notulist", " ###### De Dataanalist", " ###### De Samenvatter", " ###### De Broodjesbakker"])
st.markdown("--------------------------------------------------- ")    
with tab2:
    st.header("De Notulist :male-student: \n*waarom zou je moeilijk doen ....?*")
    st.markdown(""" ##### De Notulist :male-student:  helpt bij je het maken van notulen. Geef Berend een audioopname van een overleg, of een ruwe transcript van een overleg, hij maakt de notulen voor je. Voeg je bestand toe door het te slepen in onderstaand vak.  """)
        
    st.markdown(
        """ 
            ##### Hoe werkt de :male-student: Notulist?  
            1. **:notebook: Upload een audio, docx, of txt file📄**
            2. **:writing_hand: Vraag Berend om notulen te maken en geef indien gewenst extra informatie zoals soort overleg, doel,  agendapunten, aanwezigen, tijdstip, locatie, enz. ** 
            3. **:golf: Klik dan op versturen, en Berend gaat aan de slag**            
        """
        )
    
    st.markdown("**2. [De Notulist](Mapping_Demo)**")
    
 
with tab3: 
    st.markdown("**3. [De Dataanalist](DataFrame_Demo)**")

with tab4:
    st.markdown("**6. [De Samenvatter](Samenvatter_Demo)**")
    # st.markdown("**4. [De Datavormgever](Plotting_Demo)**")
 
 # with tab5:
#    st.markdown("**5. [De Chatbot](Chat_Demo)**")
    
# with tab6:
 #   st.markdown("**6. [De Samenvatter](Samenvatter_Demo)**")

with tab5:
    st.markdown("**7. [De Broodjesbakker](Broodje_Berend_Demo)**")

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
    # st.markdown("**1. [De Lesplanner](Lesplan_Demo)**")
    maakLesplan(True)
    

st.markdown(""":angel: :gray[ *Disclaimer Aan het gebruik, of resulaten van Berend-Botje Skills kunnen geen rechten worden verleend. Noch zijn wij aansprakelijk voor enig gevolg van dit gebruik. Bedenk dat de voorbeelden die hier getoond worden nog in een premature fase verkeren: het is werk onder constructie...* ]""")
