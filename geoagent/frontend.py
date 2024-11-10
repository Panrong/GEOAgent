import streamlit as st
import pandas as pd

from geoagent.utils.front_helpers import search_records, parse_metadata, download_data


st.title("GeoAgent")


st.header(":green[Step 1: Search a topic]")
keywords = st.text_input("What keywords to search on GEO database?", placeholder="Enter a topic")
search_instruct = st.text_area("Specify your search instructions:", placeholder="What rules to filter the search results?", height=80)

col1, col2 = st.columns(2, vertical_alignment="bottom")
with col1:
    max_records = st.number_input("Specify max records:", min_value=5, max_value=1000, value=5)
with col2:
    st.write("")
    search_button = st.button("Search", type="primary", use_container_width=True)
    

# Search button
if search_button:
    if keywords.strip():
        # the actual search
        search_df = search_records(keywords, max_records)
        # Store search_df in session state
        st.session_state['search_df'] = search_df
        
    else:
        st.warning("Please enter keywords to search")

# Display results
if 'search_df' in st.session_state:
    st.write("### Retrieved records")
    st.dataframe(st.session_state.search_df, use_container_width=False)


st.header(":green[Step 2: Parse metadata & Download data]")
col1, col2 = st.columns(2, vertical_alignment="bottom")
with col1:
    is_parse_subsamples = st.checkbox("Parse GSMs within each GSE", value=False)
with col2:
    parse_btn = st.button("Parse Metadata", type="primary", use_container_width=True) 

# Parse metadata
if parse_btn:
    if "search_df" in st.session_state:
        metadata_df = parse_metadata(list(st.session_state['search_df'].index.values), is_parse_subsamples)
        st.session_state['metadata_df'] = metadata_df
    else:
        st.warning("Please perform a search first") 
# Display metadata
if 'metadata_df' in st.session_state:
    st.write("### Metadata of retrieved records")
    st.dataframe(st.session_state.metadata_df, use_container_width=False)


download_instruct = st.text_area("Specify your download instructions:", placeholder="What rules to select records to download based on their metadata?", height=80)
col1, col2 = st.columns(2, vertical_alignment="bottom")
with col1:
    target_file_types = st.multiselect("Select file types to download:", options=["ALL", "h5ad", "txt"], default=["ALL"])
with col2:
    download_btn = st.button("Download", type="primary", use_container_width=True)


# Download
if download_btn:
    if 'metadata_df' in st.session_state:
        download_data(list(st.session_state.metadata_df.index.values),
                      target_file_types)
    else:
        st.warning("Please parse metadata first")

st.header(":green[Step 3: Output]")
organize_instruct = st.text_area("Specify your output instructions:", placeholder="What data to select for the final output?", height=80)
if st.button("Output", type="primary", use_container_width=True):
    st.write("Outputting results...")