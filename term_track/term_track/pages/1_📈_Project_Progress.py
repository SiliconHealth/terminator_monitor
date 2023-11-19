import streamlit as st
import time
import numpy as np
from db.database import get_db

from bson.objectid import ObjectId
import json
from pathlib import Path
import pandas as pd
import altair as alt
from urllib.parse import quote_plus

st.set_page_config(page_title="Project Progress", page_icon="📈")

st.markdown("# Project Progress")
st.sidebar.header("Project Progress")
st.write(
    """This is NLP progress for our project. We are currently working on the following tasks:
    annotate 2499 notes."""
)

db, _ = get_db()

projs = list(db["project"].find({}, {"id": 1}))
options = [a["id"] for a in projs] 
proj_name = st.selectbox(label="Choose a Project :briefcase:",options=options)

proj_id = str([p['_id'] for p in projs if p["id"] == proj_name][0])

# anno = db["annotation"].find_one({"_id": ObjectId(proj_id)})
proj = db["project"].find_one({"_id": ObjectId(proj_id)})
st.write("Report on project: " + proj['name'])

docs = proj['docs']
doing = sum([1 if v['wip']>0 else 0 for k,v in docs.items()])
done = sum([1 if v['complete']>0 else 0 for k,v in docs.items()])

doing_sum_df = pd.DataFrame({'type': ["doing", "done", "waiting"], 
                             "value": [doing, done, len(list(docs.keys()))-doing-done],
                             "progress": ['1','1','1']})
st.table(doing_sum_df[['type', 'value']])
chart = alt.Chart(doing_sum_df).mark_bar().encode(
    x='value',
    y='progress',
    color='type'
)
st.altair_chart(chart)

annots = db["annotation"].find({"proj_oid": quote_plus(proj_id)})
annot_list = list(annots)

chart_type = st.selectbox(label="type of progress: ",options=["ALL", "DOING", "DONE"])
if chart_type == "ALL":
    annot_list = annot_list
elif chart_type == "DOING":
    annot_list = [a for a in annot_list if a['approver_oid'] is None]
elif chart_type == "DONE":
    annot_list = [a for a in annot_list if a['approver_oid'] is not None]

dt = [a['updated_at'].date() for a in annot_list]
dt_df = pd.DataFrame(dt).groupby([0]).size().cumsum()
ind = list(dt_df.index)
dt_df = dt_df.reset_index(drop=True)
dt_df = pd.DataFrame({'date': ind, 'count': dt_df.values})

st.line_chart(dt_df, x='date', y='count')


# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")