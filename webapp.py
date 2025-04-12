import streamlit as st
import pandas as pd
import base64
from io import StringIO
import time

# Import functions from your app.py module
from app import get_news_data, save_to_csv

# Set page title and configuration
st.set_page_config(
    page_title="News Story Finder",
    page_icon="📰",
    layout="wide"
)

# App header
st.title("📰 News Story Finder")
st.markdown("Search for news stories by keyword and download the results as CSV.")

# Input section
st.subheader("Search Parameters")
col1, col2 = st.columns([3, 1])

with col1:
    keyword = st.text_input("Enter search keyword:", value="Bangladesh")

with col2:
    days_back = st.number_input("Days to look back:", min_value=1, max_value=30, value=1)

# Search button
if st.button("🔍 Search for News"):
    if not keyword:
        st.error("Please enter a search keyword")
    else:
        # Show loading message
        with st.spinner(f"Searching for news about '{keyword}'..."):
            # Get news data
            try:
                # Call the function from your imported module
                news_df = get_news_data(keyword, days_back)
                
                # Store dataframe in session state for later use
                st.session_state.news_df = news_df
                st.session_state.search_term = keyword
                
                # Show success message
                st.success(f"Found {len(news_df)} articles about '{keyword}'")
            except Exception as e:
                st.error(f"Error fetching news: {str(e)}")

# Display results if available
if 'news_df' in st.session_state and not st.session_state.news_df.empty:
    st.subheader("Search Results")
    
    # Display dataframe with pagination
    st.dataframe(st.session_state.news_df, use_container_width=True)
    
    # Create download button for CSV
    def get_csv_download_link(df, filename):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-link">Download CSV File</a>'
        return href
    
    # Display download button
    filename = f"{st.session_state.search_term}_news_data.csv"
    st.markdown(get_csv_download_link(st.session_state.news_df, filename), unsafe_allow_html=True)
    
    # Additional options
    if st.button("Save to disk"):
        try:
            filepath = save_to_csv(st.session_state.news_df, filename)
            st.success(f"File saved to {filepath}")
        except Exception as e:
            st.error(f"Error saving file: {str(e)}")
    
    # Show some statistics
    st.subheader("Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'media_name' in st.session_state.news_df.columns:
            st.write("Top Sources:")
            source_counts = st.session_state.news_df['media_name'].value_counts().head(10)
            st.bar_chart(source_counts)
    
    with col2:
        if 'publish_date' in st.session_state.news_df.columns:
            st.write("Publications by Date:")
            # Convert to datetime if not already
            try:
                date_df = st.session_state.news_df.copy()
                date_df['publish_date'] = pd.to_datetime(date_df['publish_date'])
                date_counts = date_df['publish_date'].dt.date.value_counts().sort_index()
                st.bar_chart(date_counts)
            except:
                st.write("Could not parse dates for visualization")

# Add footer
st.markdown("---")
st.markdown("Powered by MediaCloud API")