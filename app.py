# Import required libraries
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to scrape product details dynamically
def scrape_product_details(url, selectors):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {'URL': url}

        for detail, selector in selectors.items():
            if not selector:  # Skip empty selectors
                data[detail] = 'N/A'
                continue

            tag, class_name = selector.split(',')
            tag, class_name = tag.strip(), class_name.strip()

            if detail == 'Single Image':
                img = soup.find(tag, class_=class_name)
                data['Single Image'] = img['src'] if img and img.has_attr('src') else 'N/A'
            
            elif detail == 'All Images':
                images = soup.find_all(tag, class_=class_name)
                img_srcs = [img['src'] for img in images if img.has_attr('src')]
                data['All Images'] = img_srcs if img_srcs else 'N/A'
            
            else:
                element = soup.find(tag, class_=class_name)
                data[detail] = element.text.strip() if element else 'N/A'

        return data

    except requests.exceptions.RequestException as e:
        return {'Error': str(e)}

# Streamlit UI
def main():
    st.title("Customizable Web Scraping App")

    # File uploader to upload .txt file containing product URLs
    uploaded_file = st.file_uploader("Upload a .txt file containing product URLs", type=["txt"])

    if uploaded_file is not None:
        urls = uploaded_file.read().decode('utf-8').splitlines()

        st.write("Specify the details you want to scrape and their HTML tags/classes:")

        # Let users define custom selectors for details
        detail_options = ['Title', 'Price', 'SKU', 'Description', 'Single Image', 'All Images']
        selectors = {}

        for detail in detail_options:
            selector_input = st.text_input(f"Enter the tag and class for {detail} (format: tag, class):", "")
            selectors[detail] = selector_input

        if st.button("Scrape Data"):
            results = []
            for url in urls:
                result = scrape_product_details(url.strip(), selectors)
                results.append(result)

            # Convert results to DataFrame for better display and export
            df = pd.DataFrame(results)
            st.write(df)

            # Provide download option for the results
            st.download_button("Download Results as CSV", df.to_csv(index=False).encode('utf-8'), "scraped_data.csv", "text/csv")

            # Display images for each URL
            for result in results:
                st.subheader(f"Images for URL: {result['URL']}")

                # Display single image if valid
                if result['Single Image'] != 'N/A':
                    st.image(result['Single Image'], caption="Single Image", use_column_width=True)
                else:
                    st.write("No single image found.")

                # Display all images if valid
                if result['All Images'] != 'N/A' and isinstance(result['All Images'], list):
                    st.write("All Images:")
                    img_urls = result['All Images']
                    cols = st.columns(2)  # Display images in two columns
                    for idx, img_url in enumerate(img_urls):
                        with cols[idx % 2]:  # Arrange images in two columns
                            st.image(img_url, caption=f"Image {idx+1}", use_column_width=True)
                else:
                    st.write("No additional images found.")

if __name__ == "__main__":
    main()
