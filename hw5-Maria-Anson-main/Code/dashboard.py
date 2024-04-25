from urllib.parse import urlparse
import streamlit as st
from elasticsearch7 import Elasticsearch
import re
import pandas as pd

# Initialize Elasticsearch connection
es = Elasticsearch(cloud_id= "6200:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRiZTllZjE5NDRkNTg0MDE3YTU0NDg0MzcwYjk5MjQzMSQ2Zjg1ODJhNWRjMGY0NDBhODU1Njk1MDQ4NzMyNmU2Yg==",
                        http_auth=("elastic", "fwOhKti7myB3PKFHQavQBhcr"))

# Function to retrieve domain from URL
def domain_retrieval(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

# Function to highlight text hits with reduced opacity
def highlight_text(text, query):
    highlighted_text = re.sub(f'({query})', r'<span style="background-color: rgba(255, 255, 0, 0.5);">\1</span>', text, flags=re.IGNORECASE)
    return highlighted_text

# Function to perform search and display results for a given query
def search_and_display_results(query, query_id):
    st.write(f"## Query: {query}")
    
    # Perform search
    INDEX = 'crawler'
    response = es.search(
        index=INDEX,
        body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content"]
                }
            }
        },
        size=200  # Number of documents to retrieve
    )
    
    # Display search results
    display_list = {}
    for hit in response['hits']['hits']:
        display_list[hit["_id"]] = {
            "content": hit["_source"]["content"],
            "author": hit["_source"]["author"],
            "title": hit["_source"]["title"]
        }
    
    if display_list:
        # Display documents with input fields for relevance grade and assessor's name
        for idx, (article_id, article_info) in enumerate(display_list.items(), 1):
            domain = domain_retrieval(article_id)
            with st.expander(f"**Domain:** {domain} ----- Article ID: {article_id}"):
                st.markdown(f"# {article_info['title'].strip()}")
                st.markdown(f"**Author:** {','.join(article_info['author'])}")
                highlighted_content = highlight_text(article_info['content'], query)
                st.markdown(highlighted_content, unsafe_allow_html=True)
                
                # Input fields for relevance grade and assessor's name
                relevance_grade = st.selectbox(f"Relevance Grade for Document {idx} (Query: {query}):",
                                                ['Very relevant', 'Relevant', 'Non-relevant'], 
                                                key=f"grade_{query_id}_{idx}")
                assessor_name = "Anson"
                
                # Save assessment when submit button is clicked
                if st.button(f"Submit for Document {idx} (Query: {query})"):
                    save_to_qrel(query_id, assessor_name, article_id, relevance_grade)
                    st.write(f"Assessment for Document {idx} (Query: {query}) saved successfully.")
                    st.experimental_rerun()  # Rerun the app to clear input fields

    else:
        st.write("No results found.")

# Function to save assessment to QREL file
def save_to_qrel(query_id, assessor_id, doc_id, grade):
    with open("qrel.txt", "a") as f:
        f.write(f"{query_id} {assessor_id.replace(' ', '_')} {doc_id} {grade}\n")

# Streamlit app
def main():
    st.title("Document Search and Labeling")

    queries = {
        'West African Ebola epidemic': '152901',
        'H1N1 Swine Flu pandemic': '152902',
        'COVID 19': '152903',
    }

    for query, query_id in queries.items():
        search_and_display_results(query, query_id)

    st.sidebar.write("Total Documents Assessed:")
    st.sidebar.write(len(open("qrel.txt").readlines()))

if __name__ == "__main__":
    main()
