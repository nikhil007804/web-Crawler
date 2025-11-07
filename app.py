import streamlit as st
import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
import time

# Load environment variables
load_dotenv()

# Initialize Firecrawl
@st.cache_resource
def init_firecrawl():
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        st.error("Please set FIRECRAWL_API_KEY in your .env file")
        return None
    return FirecrawlApp(api_key=api_key)

def main():
    st.title("🔥 Web Crawler")
    st.write("Simple web crawling using Firecrawl")
    
    # Initialize Firecrawl
    app = init_firecrawl()
    if not app:
        return
    
    # URL input
    url = st.text_input("Enter URL to crawl:", placeholder="https://example.com")
    
    # Crawl options
    col1, col2 = st.columns(2)
    with col1:
        include_links = st.checkbox("Include links", value=True)
    with col2:
        max_pages = st.number_input("Max pages", min_value=1, max_value=10, value=1)
    
    if st.button("🚀 Start Crawling", type="primary"):
        if not url:
            st.error("Please enter a URL")
            return
            
        # Show loading spinner
        with st.spinner("Crawling website... This may take a few minutes."):
            try:
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Update progress
                for i in range(3):
                    status_text.text(f"Crawling... Step {i+1}/3")
                    progress_bar.progress((i + 1) * 33)
                    time.sleep(0.5)
                
                # Perform the crawl
                crawl_params = {
                    'crawlerOptions': {
                        'includes': [],
                        'excludes': [],
                        'generateImgAltText': True,
                        'returnOnlyUrls': False,
                        'maxDepth': 2,
                        'limit': max_pages
                    },
                    'pageOptions': {
                        'onlyMainContent': True,
                        'includeHtml': False,
                        'screenshot': False
                    }
                }
                
                if include_links:
                    result = app.crawl_url(url, crawl_params)
                else:
                    result = app.scrape_url(url, crawl_params['pageOptions'])
                
                progress_bar.progress(100)
                status_text.text("Crawling completed!")
                
                # Display results
                st.success("✅ Crawling completed!")
                
                if include_links and isinstance(result, dict) and 'data' in result:
                    st.subheader(f"Found {len(result['data'])} pages")
                    
                    for i, page in enumerate(result['data']):
                        with st.expander(f"Page {i+1}: {page.get('metadata', {}).get('title', 'No title')}"):
                            st.write(f"**URL:** {page.get('metadata', {}).get('sourceURL', 'N/A')}")
                            st.write(f"**Content:**")
                            content = page.get('markdown', page.get('content', 'No content available'))
                            st.text_area("", content[:1000] + "..." if len(content) > 1000 else content, height=200)
                else:
                    # Single page result
                    if isinstance(result, dict):
                        st.subheader("Scraped Content")
                        content = result.get('markdown', result.get('content', 'No content available'))
                        st.text_area("Content", content, height=400)
                        
                        if 'metadata' in result:
                            st.subheader("Metadata")
                            st.json(result['metadata'])
                    else:
                        st.write(result)
                        
            except Exception as e:
                st.error(f"Error during crawling: {str(e)}")
                progress_bar.empty()
                status_text.empty()

if __name__ == "__main__":
    main()
