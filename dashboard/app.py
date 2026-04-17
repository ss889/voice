import streamlit as st
import requests
import json
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Document Intelligence Pipeline",
    page_icon="📄",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

st.title("📄 Document Intelligence Pipeline")
st.markdown("A production RAG system with semantic search and evaluation")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "🔍 Search", "⭐ Evaluate", "📊 Analytics"])

# TAB 1: UPLOAD
with tab1:
    st.header("Upload Documents")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a document (PDF or TXT)",
            type=["pdf", "txt"],
            help="Supported formats: PDF, TXT"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("📤 Ingest", use_container_width=True):
            if uploaded_file is not None:
                with st.spinner("Processing document..."):
                    # Save temp file
                    temp_dir = Path("./temp_uploads")
                    temp_dir.mkdir(exist_ok=True)
                    temp_path = temp_dir / uploaded_file.name
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Send to API
                    try:
                        with open(temp_path, "rb") as f:
                            files = {"file": f}
                            response = requests.post(f"{API_URL}/ingest", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Success! Indexed {result.get('chunks_indexed', 0)} chunks")
                            st.json(result)
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {e}")
                    finally:
                        # Clean up
                        if temp_path.exists():
                            temp_path.unlink()
            else:
                st.warning("Please select a file first")

# TAB 2: SEARCH
with tab2:
    st.header("Search Documents")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Enter your search query", placeholder="e.g., 'What are vector databases?'")
    
    with col2:
        k = st.number_input("Top K results", min_value=1, max_value=20, value=5)
    
    if st.button("🔍 Search", use_container_width=True):
        if query:
            with st.spinner("Searching..."):
                try:
                    response = requests.post(f"{API_URL}/query", json={"query": query, "k": k})
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.info(f"Found {result.get('num_results', 0)} results in {result.get('retrieval_time_ms', 0):.1f}ms")
                        
                        for i, result_item in enumerate(result.get("results", []), 1):
                            with st.expander(f"Result {i} - {result_item.get('source', 'Unknown')} (Score: {result_item.get('score', 0):.3f})"):
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(result_item.get("text", ""))
                                with col2:
                                    st.metric("Score", f"{result_item.get('score', 0):.3f}")
                                    st.caption(f"Page {result_item.get('page_num')}, Chunk {result_item.get('chunk_index')}")
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")
        else:
            st.warning("Please enter a search query")

# TAB 3: EVALUATE
with tab3:
    st.header("Evaluate Retrieval Quality")
    
    query = st.text_input("Query for evaluation", placeholder="e.g., 'How does semantic search work?'")
    k = st.number_input("Chunks to evaluate", min_value=1, max_value=20, value=3, key="eval_k")
    
    if st.button("⭐ Evaluate Retrieval", use_container_width=True):
        if query:
            with st.spinner("Evaluating..."):
                try:
                    response = requests.post(f"{API_URL}/evaluate", json={"query": query, "k": k})
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Show average score
                        avg_score = result.get("average_relevance_score", 0)
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Average Relevance Score", f"{avg_score:.1f}/5")
                        with col2:
                            st.metric("Retrieval Time", f"{result.get('retrieval_time_ms', 0):.0f}ms")
                        
                        # Show detailed results
                        st.subheader("Detailed Evaluations")
                        for i, result_item in enumerate(result.get("results", []), 1):
                            with st.expander(f"Chunk {i} - Score: {result_item.get('evaluation', {}).get('score', 'N/A')}/5"):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.write("**Text:**")
                                    st.write(result_item.get("text", ""))
                                    
                                    eval_data = result_item.get("evaluation", {})
                                    st.write("**Reasoning:**")
                                    st.write(eval_data.get("reasoning", "N/A"))
                                    
                                    st.write("**Key Matches:**")
                                    for match in eval_data.get("key_matches", []):
                                        st.caption(f"• {match}")
                                
                                with col2:
                                    score = eval_data.get("score", 0)
                                    st.metric("Score", f"{score}/5")
                                    st.caption(f"Source: {result_item.get('source')}")
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")
        else:
            st.warning("Please enter a query")

# TAB 4: ANALYTICS
with tab4:
    st.header("Collection Analytics")
    
    if st.button("🔄 Refresh Stats"):
        try:
            response = requests.get(f"{API_URL}/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Vectors", stats.get("vectors_count", 0))
                with col2:
                    st.metric("Vector Dimension", stats.get("vector_size", 0))
                with col3:
                    st.metric("Collection", stats.get("collection_name", "N/A"))
                
                st.json(stats)
            else:
                st.error(f"❌ Error: {response.text}")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
    
    # Clear collection
    if st.button("🗑️ Clear Collection", help="Delete all documents"):
        if st.checkbox("Confirm: Clear all documents"):
            try:
                response = requests.delete(f"{API_URL}/clear")
                if response.status_code == 200:
                    st.success("✅ Collection cleared")
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")

# Footer
st.markdown("---")
st.markdown(
    """
    **Document Intelligence Pipeline** • Production RAG System  
    Built with FastAPI, Qdrant, OpenAI, and Streamlit  
    For Forward Deployed Engineer roles at top companies
    """
)
