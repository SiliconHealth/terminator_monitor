import streamlit as st

# from components.test_lib import id 
# from components.dev_db import db
# from components.track import track_component
from db.database import get_db

import pandas as pd
import numpy as np

from PIL import Image
import streamlit as st

from pathlib import Path
import os 
data_path = os.getenv('DATA_PATH')

# im = Image.open("/app/terminator_monitor/term_track/term_track/data/siliconhealthicon.ico")
im = Image.open(Path(data_path) / "siliconhealthicon.ico")

db, title = get_db()

st.set_page_config(
    page_title="Terminator Tracker",
    page_icon=im,
)

st.sidebar.success("Success! Select a page above.")
st.title(title)

st.markdown(
    """
    This is for Siliconers to track the progress of annotation.
    **👈 Select an app from the sidebar** to see progress and download datasets.
    
    - Check out [our github](https://github.com/SiliconHealth)
    - Our discord channel is [here](https://discord.gg/NX3JFXt6)
    """
)

if db is not None:
    pass 