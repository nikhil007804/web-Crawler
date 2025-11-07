import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

st.title("🕷️ Web Crawler with Firecrawl")
st.write("Enter a URL to crawl and extract content using Firecrawl API")

# Input for URL
url_to_crawl = st.text_input("Enter URL to crawl:", placeholder="https://example.com")

# Crawl options
col1, col2 = st.columns(2)
with col1:
    limit = st.number_input("Limit pages", min_value=1, max_value=50, value=10)
    crawl_entire_domain = st.checkbox("Crawl entire domain", value=False)

with col2:
    include_sitemap = st.checkbox("Include sitemap", value=True)
    only_main_content = st.checkbox("Only main content", value=False)

# Crawl button
if st.button("🚀 Start Crawling", type="primary"):
    if not url_to_crawl:
        st.error("Please enter a URL to crawl")
    else:
        # Get API key from environment
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            st.error("FIRECRAWL_API_KEY not found in environment variables")
            st.stop()
        
        # Prepare the payload
        payload = {
            "url": url_to_crawl,
            "sitemap": "include" if include_sitemap else "exclude",
            "crawlEntireDomain": crawl_entire_domain,
            "limit": limit,
            "scrapeOptions": {
                "onlyMainContent": only_main_content,
                "maxAge": 172800000,
                "parsers": ["pdf"],
                "formats": ["markdown"]
            }
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Show loading spinner
        with st.spinner("🔄 Starting crawl job... This may take a few minutes."):
            try:
                # Make the initial API request to start crawling
                response = requests.post(
                    "https://api.firecrawl.dev/v2/crawl",
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "id" in result:
                        crawl_id = result["id"]
                        st.info(f"🆔 Crawl job started with ID: {crawl_id}")
                        
                        # Poll for results
                        with st.spinner("🔄 Waiting for crawl to complete... This may take several minutes."):
                            max_attempts = 60  # Maximum 10 minutes (60 * 10 seconds)
                            attempt = 0
                            
                            while attempt < max_attempts:
                                # Check crawl status
                                status_response = requests.get(
                                    f"https://api.firecrawl.dev/v2/crawl/{crawl_id}",
                                    headers=headers,
                                    timeout=30
                                )
                                
                                if status_response.status_code == 200:
                                    status_result = status_response.json()
                                    
                                    # Check if crawl is completed
                                    if status_result.get("status") == "completed":
                                        st.success("✅ Crawling completed successfully!")
                                        
                                        # Display the results
                                        st.subheader("📄 Crawl Results")
                                        
                                        # Show raw JSON response in expandable section
                                        with st.expander("View Raw Response"):
                                            st.json(status_result)
                                        
                                        # Display formatted results if data is available
                                        if "data" in status_result and status_result["data"]:
                                            st.subheader("📋 Extracted Content")
                                            for i, page in enumerate(status_result["data"], 1):
                                                with st.expander(f"Page {i}: {page.get('url', 'Unknown URL')}"):
                                                    if "markdown" in page:
                                                        st.markdown(page["markdown"])
                                                    elif "content" in page:
                                                        st.text(page["content"])
                                                    else:
                                                        st.json(page)
                                        else:
                                            st.warning("No content data found in the response.")
                                        break
                                    
                                    elif status_result.get("status") == "failed":
                                        st.error("❌ Crawl job failed!")
                                        st.error(f"Error: {status_result.get('error', 'Unknown error')}")
                                        break
                                    
                                    else:
                                        # Still in progress, show status
                                        current_status = status_result.get("status", "unknown")
                                        st.info(f"⏳ Status: {current_status}")
                                        time.sleep(10)  # Wait 10 seconds before next check
                                        attempt += 1
                                
                                else:
                                    st.error(f"❌ Error checking status: {status_response.status_code}")
                                    break
                            
                            if attempt >= max_attempts:
                                st.warning("⏰ Crawl is taking longer than expected. You can check the status manually using the crawl ID above.")
                    
                    else:
                        st.error("❌ No crawl ID returned from the API")
                        st.json(result)
                    
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.error(f"Response: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. The crawling process is taking longer than expected.")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Request failed: {str(e)}")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.write("This app uses Firecrawl API to crawl websites and extract content.")
    
    st.header("⚙️ Settings")
    st.write("Configure your crawling options in the main panel.")
    
    st.header("📚 Features")
    st.write("• Extract content in Markdown format")
    st.write("• Crawl single pages or entire domains")
    st.write("• Include/exclude sitemaps")
    st.write("• Filter main content only")
    st.write("• PDF parsing support")
