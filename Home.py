import streamlit as st
from PIL import Image
import os

st.set_page_config(
    page_title="Home", layout='wide'
)

image_path = ('OIP.jpg')
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.write("# Curry Company Growth Dashboard")
