# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
from urllib.error import URLError

import altair as alt
import pandas as pd
from PIL import Image
import streamlit as st
from streamlit.hello.utils import show_code
import openpyxl

image = Image.open('berend_gpt/images/producttoer.jpeg')

MIJNDATA = "pages/mbo2018-2022.xlsx"

def data_frame_demo():
    @st.cache_data
    def get_UN_data():
        MIJNDATA = "pages/mbo2018-2022.xlsx"
        # AWS_BUCKET_URL = "https://streamlit-demo-data.s3-us-west-2.amazonaws.com"
        df = pd.read_excel(MIJNDATA)
        # print(df.head())


        # df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
        # df=df.set_index("PROVINCIE")
        return df.set_index("INSTELLINGSCODE")

    try:
        df = get_UN_data()

        keuze = set(list(df["INSTELLINGSNAAM"]))
        keuze = sorted(keuze)
        countries = st.multiselect("INSTELLINGSNAAM", keuze, [])
        
        if not countries:
            st.error("Selecteer een Instelling")
        else:
            # print("GEKOZEN")
            # print(countries[0])
            # countries = countries # {{$B}}
            
            # print(df[df["INSTELLINGSNAAM"].isin(countries)]) 
            
            # print(df[df["INSTELLINGSNAAM" == c] for c in countries])

            # st.stop()

            # data = df[df["INSTELLINGSNAAM"] in countries]
            data = df[df["INSTELLINGSNAAM"].isin(countries)]
            data = data[["INSTELLINGSNAAM","GEMEENTENAAM", "PEILJAAR", "TOTAAL"]]
            # print(data)
            data = data.astype({"PEILJAAR": int})
            # print(data)

            st.write("### Studenten per Instelling", data.sort_values(by="INSTELLINGSNAAM"))
            # data = data.T.reset_index()
            
            ## st.bar_chart(data=data, x=["PEILJAAR"], y=["TOTAAL"],use_container_width=True)
            st.stop()
            chart = (
                alt.Chart(data)
                .mark_area(opacity=0.3)
                .encode(
                    x="PEILJAAR",
                    y=["TOTAAL"], 
                    color="INSTELLINGSNAAM:N",
                )
            )
            st.altair_chart(chart, use_container_width=True)
            

    except URLError as e:
        st.error( "**This demo requires internet access.** Connection error: %s, % e.reason")

st.set_page_config(page_title="DataFrame Demo", page_icon="📊")
st.markdown("# DataFrame Demo")
st.image(image, caption=None, width=140, use_column_width=None, clamp=True, channels="RGB", output_format="png")

st.sidebar.header("DataFrame Demo")
st.write(
    """Hier laat Berend zien hoe excel bestanden in een DataFrame worden geplaatst."""
)

data_frame_demo()

# show_code(data_frame_demo)
