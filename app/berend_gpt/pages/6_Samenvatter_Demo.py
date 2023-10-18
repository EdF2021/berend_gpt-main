import os 
import streamlit as st
from PIL import Image

from streamlit import sidebar
from core import ui
from ui import (
    wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from core.caching import bootstrap_caching
from core.parsing import read_file
from core.chunking import chunk_file
from core.embedding import embed_files
from core.utils import get_llm
from core.qa import query_folder
import tiktoken


EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL_LIST = ["gpt-3.5-turbo", "gpt-4","gpt-3.5-turbo-16k"]

image = Image.open('images/producttoer.jpeg')
# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")

st.set_page_config(
        page_title="Berend-Botje Skills", 
        page_icon="👋",
        layout="wide",
        initial_sidebar_state="expanded" )


col1, col2 = st.columns(2)

with col1:
    st.header("Berend-Botje Skills" )
    st.subheader(":-) De Samenvatter\n*waarom zou je moeilijk doen ....?*")
with col2:
   st.image(image, caption=None, use_column_width=True, clamp=True, channels="RGB", output_format="png")


with st.sidebar:
    st.markdown("""#### De Samenvatter kan diverse omvangrijke documenten voor u samenvatten. """)
    st.markdown("""
    #### Hoe werkt de Samenvatter? 
    1. **Upload een pdf, docx, of txt file📄**
    2. **Vraag of Berend een samenvatting voor je wilt maken.  💬**
    3. **En Berend gaat aan de slag**
    """ )


# Enable caching for expensive functions
bootstrap_caching()

# sidebar()

# sleutel = os.getenv("OPENAI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

st.session_state.get("OPENAI_API_KEY")


if not openai_api_key:
    st.warning(
        "Je hebt een geldig OpenAI API key nodig!"
        " https://platform.openai.com/account/api-keys."
    )


uploaded_file = st.file_uploader(
    "**HIER KUN JE JOUW PDF, DOCX, OF TXT BESTAND UPLOADEN!!**",
    type=["pdf", "docx", "txt"],
    help="Gescande documenten worden nog niet ondersteund! ",
)

model: str = st.selectbox("Model", options=MODEL_LIST)  # type: ignore

with st.expander("Geavanceerd"):
    return_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
    show_full_doc = st.checkbox("Show parsed contents of the document")


if not uploaded_file:
    st.stop()

try:
    
    file = read_file(uploaded_file)
except Exception as e:
    display_file_read_error(e, file_name=uploaded_file.name)

with st.spinner("Indexeren van het document... Dit kan even duren⏳"):
    chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)

    if not is_file_valid(file):
        st.stop()


    if not is_open_ai_key_valid(openai_api_key, model):
        st.stop()


    
    folder_index = embed_files(
            files=[chunked_file],
            embedding=EMBEDDING if model != "debug" else "debug",
            vector_store=VECTOR_STORE if model != "debug" else "debug",
            openai_api_key=openai_api_key,

        )
    if uploaded_file:
        llm2 = get_llm(model=model, openai_api_key=openai_api_key, temperature=0)
        result = query_folder(
        folder_index=folder_index,
        query="""Maak een mooie en inhoudelijk juiste samenvatting van het document dat net is ingelezen. De samenvatting moet alle  belangrijke thema's bevatten die in het document worden genoemd. Gebruik onderstaand format coor de samenvatting.\n 
    < Voorbeeld >
        ## Samenvatting van {{Naam van het document}}
        
        ### {{Hier geef je de auteur}} en {{datum van vandaag}}.
        
        ## Waar gaat het over?
        
        Een globale beschrijving  over de inhoud van het document. Wat het onderwerp is, of het doel is, voor wie het geschreven is, en wat de conclusies zijn.
        
        ## Belangrijkste thema's

        Hier puntsgewijs de thema's of onderwerpen samenvatten.
    < Einde Voorbeeld >

        Gebruik koppen en subkoppen om meer overzicht te krijgen en om de belangrijke thema's te benadrukken. Toon de samenvatting in markdown formaat. En geef altijd antwoord in HET NEDERLANDS!!""",
            
        return_all=return_all_chunks,
            llm=llm2,
            )
        st.markdown("+++  Samenvatting  +++ ")
        st.markdown(result.answer)






# st.button("Onderwerp", key="Onderwerp")
# st.button("Lesdoel", key="Lesdoel")


with st.form(key="qa_form"):
    query = """ Maak een samenvatting van het ingelezen document.  Gebruik een helder en overtuigende stijl.Gebruik het markdown formaat. Probeer de samenvatting niet groter te maken dan 2A4-tjes.GEEF ANTWOORD IN HET NEDERLANDS!"""    
    query += st.text_input("**Maak een samenvatting") 
    
    submit = st.form_submit_button("Sturen")
    

# if show_full_doc:
    # with st.expander("Document"):
        # Hack to get around st.markdown rendering LaTeX
        # st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)


if submit:
    with st.spinner("Bezig met je vraag ... ⏳"):
        if not is_query_valid(query):
            st.stop()

        # Output Columns

        print(query),
        llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0)
        result = query_folder(
                folder_index=folder_index,
                query = query,
                return_all=return_all_chunks,
                llm=llm
                )
        # answer_col, sources_col = st.columns(2)
        
        # with answer_col:
        st.markdown("#### Samenvatting \n['Berend-Botje Skills']('https://berend-botje.online')")
        st.markdown(result.answer)
    
        # with sources_col:
            # st.markdown("#### Bronnen")
            # for source in result.sources:
                # st.markdown(source.page_content)
                # st.markdown(source.metadata["source"])
                # st.markdown("---")
