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

# import tiktoken


EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL_LIST = ["gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k"]

image = Image.open("berend_gpt/images/achtergrond_samenvatter.png")
# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")

st.set_page_config(
    page_title="Berend-Botje Skills",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


col1, col2 = st.columns(2)

with col1:
    st.header("Berend-Botje Skills")
    st.subheader(" :bookmark_tabs: De Samenvatter\n*waarom zou je moeilijk doen ....?*")
    st.markdown(""" ##### De Samenvatter kan diverse omvangrijke documenten voor u samen vatten.""")
    st.markdown("""
                ##### Hoe werkt het ? 
                1. **Upload een pdf, docx, of txt file📄**
                2. **Vraag of Berend een samenvatting voor je wilt maken.  💬**
                3. **En Berend gaat aan de slag**"""
                )
with col2:
    st.image(
        image,
        caption=None,
        use_column_width=True,
        clamp=True,
        channels="RGB",
        output_format="png",
    )


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
        llm2 = get_llm(
            model=model, 
            openai_api_key=openai_api_key, 
            temperature=0
            )
        result = query_folder(
            folder_index=folder_index,
            query="""Jij ben een slimme Assistent Bot, en je kan heel goed samenvattingen maken van omvangrijke documenten.
        Maak nu een goede uitgebreide samenvatting van het document dat net is ingelezen. De samenvatting moet alle  belangrijke thema's bevatten die in het document worden genoemd. Maak de samenvatting in het Markdown formaat, en gebruik koppen en subkoppen om meer overzicht te geven, en om zo de belangrijke thema's te benadrukken.
        Nogmaals de samenvatting mag best uitgebreid zijn, maar moet altijd in HET NEDERLANDS!!""",
            return_all=return_all_chunks,
            llm=llm2,
        )
        st.markdown(result.answer)


# st.button("Onderwerp", key="Onderwerp")
# st.button("Lesdoel", key="Lesdoel")


with st.form(key="qa_form"):
    query = """ 
            Maak gebruik van het ingelezen document om de vragen 
            van de gebruiker goed te kunnen beantwoorden.
            Je toon is zakelijk, en je doet je best om de vragen te beantwoorden. 
                Als je iets niet weet dan ga je niets verzinnen, 
                maar zeg je: 'Deze vraag kan ik niet beantwoorden'.
                Gebruik het markdown formaat. GEEF ANTWOORD IN HET NEDERLANDS!"""

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
            query=query,
            return_all=return_all_chunks,
            llm=llm,
        )
        # answer_col, sources_col = st.columns(2)

        # with answer_col:
        st.markdown(
            "#### Samenvatting \n['Berend-Botje Skills']('https://berend-botje.online')"
        )
        st.markdown(result.answer)

        # with sources_col:
        # st.markdown("#### Bronnen")
        # for source in result.sources:
        # st.markdown(source.page_content)
        # st.markdown(source.metadata["source"])
        # st.markdown("---")
