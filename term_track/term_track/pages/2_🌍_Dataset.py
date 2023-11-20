import streamlit as st
import streamlit_ext as ste 
import time
import numpy as np
from db.database import get_db

from bson.objectid import ObjectId
import json
from pathlib import Path
import pandas as pd
import altair as alt
from urllib.parse import quote_plus

import pickle
import datetime

import os 
import json 

st.set_page_config(page_title="Dataset", page_icon="🌍")

st.markdown("# Dataset")
st.sidebar.header("Dataset")
st.write(
    """This is a updated dataset for NLP model training."""
)

data_path = Path(os.getenv('DATA_PATH'))

db, _ = get_db()


def build_term_type_dict(terms_list, type_list):
    term_type_dict = {}
    for i, terms in enumerate(terms_list):
        for term in terms:
            term_type_dict[str(term['id'])] = type_list[i]
    term_type_dict['0'] = 'other'
    term_type_dict['1'] = 'other'
    return term_type_dict

data_path = Path(os.getenv('DATA_PATH'))

core_dis_terms = json.load(open(data_path / "finding_core.json"))
sdoh_terms = json.load(open(data_path / "sdoh_value_set.json"))

term_type_dict = build_term_type_dict([core_dis_terms, sdoh_terms], ["disease", "sdoh"])

# example of dataset
def build_json(proj_id, db):

    annots = db["annotation"].find({"proj_oid": quote_plus(proj_id)})
    annot_list = list(annots)

    annot_doc_ids = [a['doc_id'] for a in annot_list]
    window_size = 20 # number of characters to include before and after annotation

    # no annotation
    no_anno_list = []

    # get time for getting document and annotation
    whole_time_list = []

    # list of dataframes for each document
    token_df_list = []
    raw_text_list = []

    progress_bar = st.progress(0)
    status_text = st.empty()
    # try:
    for i, annot_name in enumerate(annot_doc_ids):
        st_whole = time.time()
        # print(annot_name)
        # get annotations for a doc
        annot = [a for a in annot_list if a['doc_id'] == annot_name]
        # return index of max length annotation
        anno_length = [len(a['anno']) for a in annot]
        anno = annot[anno_length.index(max(anno_length))]

        # get document content
        aa = db.document.find_one({"id": quote_plus(anno['doc_id'])})

        # get annotation content
        aa_content = aa['content']
        if aa_content['type'] == "text":
            aa_value = aa_content['value']

        raw_text_list.append(aa_value)

        ann = anno["anno"]

        slice_text_list = []
        start_list = []
        end_list = []
        concept_list = []
        concept_id_list = []
        concept_type_list = []
        context_list = []

        if len(ann) > 0:
            for a in ann: 
                # print(a['label']['concept'],a['infor_type'], "+++++", aa_value[a['start_offset']: a['end_offset']], aa_value[a['start_offset']-10: a['end_offset']+10])
                slice_text_list.append(aa_value[a['start_offset']: a['end_offset']])
                start_list.append(a['start_offset'])
                end_list.append(a['end_offset'])
                concept_type_list.append(term_type_dict[a['label']['concept_id']])
                concept_list.append(a['label']['concept'])
                concept_id_list.append(a['label']['concept_id'])
                context_list.append(aa_value[a['start_offset']-window_size: a['end_offset']+window_size])
            dd = pd.DataFrame({"slice_text": slice_text_list, 
                "start": start_list, 
                "end": end_list, 
                "concept": concept_list, 
                "concept_id": concept_id_list, 
                "type": concept_type_list,
                "context": context_list}, 
                )  
        else:
            print("no annotations")
            no_anno_list.append(aa_value)
            dd = pd.DataFrame(columns = ["slice_text", "start", "end", 
                            "concept", "concept_id", "type", "context"])
            
        progress_bar.progress(i/len(annot_doc_ids))
        status_text.text("{:.0f}% Complete".format( i*100/len(annot_doc_ids)))

        token_df_list.append(dd)
        whole_time_list.append(time.time() - st_whole)
    
    progress_bar.empty()
    status_text.empty()
    st.write("Completed. Elapsed time: {:.2f}s".format(np.sum(whole_time_list)))

    token_list = [j.to_dict(orient='list') for j in token_df_list]
    
    return [raw_text_list, token_list]


# download dataset
projs = list(db["project"].find({}, {"id": 1}))
options = [a["id"] for a in projs] 
proj_name = st.selectbox(label="Choose a Project :briefcase:",options=options)

proj_id = str([p['_id'] for p in projs if p["id"] == proj_name][0])

if st.button('Generate', type="primary"):
    st.write("We are generating {} datasets...".format(proj_name))
    # get annotations for a doc
    result = build_json(proj_id, db)
    raw_text_list = result[0]
    token_list = result[1]
    text_path = "text_{}_{}.json".format(proj_name, datetime.datetime.now().strftime("%Y%m%d"))
    token_path = "token_{}_{}.json".format(proj_name, datetime.datetime.now().strftime("%Y%m%d"))
    
    # text_json = json.JSONEncoder(ensure_ascii=False).encode(raw_text_list)

    # token_json = json.JSONEncoder(ensure_ascii=False).encode(token_list)

    with open(data_path / text_path, 'w', encoding='utf-8') as f:
        json.dump(raw_text_list, f, ensure_ascii=False)

    with open(data_path / token_path, 'w', encoding='utf-8') as f:
        json.dump(token_list, f, ensure_ascii=False)

    num_text = len(raw_text_list)
    num_token = np.sum([len(j['start']) for j in token_list])
    
    st.write("We have generated {} documents and {} tokens.".format(num_text, num_token))
  
    if Path.exists(data_path/text_path) and Path.exists(data_path/token_path):
        with open(data_path / text_path, 'r', encoding='utf-8') as f:
            ste.download_button(label= "download raw texts", data=f, file_name=text_path)       
        with open(data_path / token_path, 'r', encoding='utf-8') as f:
            ste.download_button(label= "download tokens", data=f, file_name=token_path)
       


