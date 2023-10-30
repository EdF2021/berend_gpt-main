import os
import streamlit as st
from PIL import Image

# from streamlit import sidebar
from berend_gpt.ui import (
    # wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from berend_gpt.core.caching import bootstrap_caching
from berend_gpt.core.parsing import read_file
from berend_gpt.core.chunking import chunk_file
from berend_gpt.core.embedding import embed_files
from berend_gpt.core.utils import get_llm
from berend_gpt.core.qa import query_folder

import tiktoken


EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL_LIST = ["gpt-3.5-turbo", "gpt-4","gpt-4-0613"]

image = Image.open("berend_gpt/images/achtergrond_samenvatter.png")
# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")

st.set_page_config(
    page_title="Berend Skills",
    page_icon=":genie:",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)


col1, col2 = st.columns(2)

with col1:
    st.header(":genie: Berend Skills")
    st.subheader(" :bookmark_tabs: De Samenvatter\n*waarom zou je moeilijk doen ....?*")
    st.markdown(""" ##### De Samenvatter kan diverse omvangrijke documenten voor j samenvatten.""")
    st.markdown("""
                ##### Hoe werkt het ? 
                1. **Upload een pdf, docx, of txt file📄**
                2. **Geef aan waar je een samenvatting van wilt ( bijv. het hele document, of een bepaald thema, onderdeel, hoofdstuk ) 💬**
                3. **Klik op de *Maak samenvatting* button** """
                )
with col2:
    st.image(
        image,
        caption=None,
        use_column_width=True,
        clamp=True,
        channels="RGB",
        output_format="auto",
    )


# Enable caching for expensive functions
bootstrap_caching()

# sidebar()

# sleutel = os.getenv("OPENAI_API_KEY")
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
except:
    openai_api_key = os.secrets["OPENAI_API_KEY"]

st.session_state.get("OPENAI_API_KEY")


if not openai_api_key:
    st.warning(
        "Je hebt een geldig OpenAI API key nodig!"
        " https://platform.openai.com/account/api-keys."
    )


uploaded_file = st.file_uploader(
    "**:point_down: UPLOAD HIER JE PDF, DOCX, OF TXT BESTAND!**",
    type=["pdf", "docx", "txt"],
    help="Gescande documenten worden nog niet ondersteund! ",
)

model: str = st.selectbox("Model", options=MODEL_LIST)  # type: ignore

return_all_chunks = True
show_full_doc = False


if not uploaded_file:
    st.stop()

try:
    file = read_file(uploaded_file)
except Exception as e:
    display_file_read_error(e, file_name=uploaded_file.name)

if uploaded_file:
    with st.spinner("Indexeren van het document... Dit kan even duren⏳"):
    
        if not is_file_valid(file):
            st.stop()
        
        chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)

        folder_index = embed_files(
            files=[chunked_file],
            embedding=EMBEDDING if model != "debug" else "debug",
            vector_store=VECTOR_STORE if model != "debug" else "debug",
            openai_api_key=openai_api_key,
        )
         
    with st.form(key="qa_form"):
        query="""Jij ben een slimme Assistent Bot, en je kan heel goed samenvattingen maken van omvangrijke documenten.
                Je maakt een samenvatting van een ingelezen document op basis van wat de gebruiker vraagt. 
                Als je iets niet weet dan ga je niets verzinnen, maar zeg je: 'Deze vraag kan ik niet beantwoorden'.
                Dit is de vraag van de gebruiker:\n 
                """
        query += st.text_input("Type hier je vraag ") + """\n 
                                Maak nu een goede uitgebreide samenvatting, in het Nederlands, op basis van de gestelde vraag van de gebruiker, 
                                en gebruik hierbij het ingelezen document als bron. 
                                Presenteer de samenvatting in het Markdown formaat, en gebruik koppen, subkoppen, bullits om structuur aan te brengen.  
                                """ 
        submit = st.form_submit_button("Maak samenvatting")


    if submit:
        with st.spinner("Bezig met de samenvatting ... ⏳"):
            if not is_query_valid(query):
                st.stop()

            # Output Columns
            llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0.3)
            result = query_folder(
                folder_index=folder_index,
                query=query,
                return_all=return_all_chunks,
                llm=llm,
            )
        
            answer_col, sources_col = st.columns(2)

            with answer_col:
                st.markdown(" #### Samenvatting \n")
                st.markdown(result.answer)

            with sources_col:
                st.markdown("#### Bronnen")
                for source in result.sources:
                    st.markdown(source.page_content)
                st.markdown(source.metadata["source"])
                st.markdown("---")
