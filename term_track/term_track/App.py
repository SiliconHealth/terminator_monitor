import streamlit as st

# from components.test_lib import id 
# from components.dev_db import db
# from components.track import track_component
from db.database import get_db

import pandas as pd
import numpy as np

from PIL import Image
import streamlit as st

im = Image.open("./data/siliconhealthicon.ico")

db, title = get_db()

st.set_page_config(
    page_title="Terminator Tracker",
    page_icon=im,
)

st.sidebar.success("Success! Select a page above.")
st.title(title)

if db is not None:
    pass 