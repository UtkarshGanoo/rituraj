from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import os
import re

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Get site URLs from .env
SITE1_URL = os.getenv('SITE1_URL')
SITE2_URL = os.getenv('SITE2_URL')
SITE3_URL = os.getenv('SITE3_URL')

def extract_price(price_str):
    """Extract numeric price from string"""
    return int(re.sub(r'[^\d]', '', price_str))

def scrape_site(url, product_name_selector, price_selector, site_name):
    """Scrape products from a single site"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        products = []
        for name, price in zip(soup.select(product_name_selector), soup.select(price_selector)):
            product = {
                'name': name.text.strip(),
                'price': extract_price(price.text.strip()),
                'site': site_name,
                'url': url
            }
            products.append(product)
        return products
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').lower()
        
        # Define scraping rules for each site
        sites = [
            {
                'url': SITE1_URL,
                'name_selector': '.product h2',
                'price_selector': '.product .price',
                'site_name': 'ElectroShop'
            },
            {
                'url': SITE2_URL,
                'name_selector': '.item h2',
                'price_selector': '.item .cost',
                'site_name': 'GadgetWorld'
            },
            {
                'url': SITE3_URL,
                'name_selector': '.product-card h2',
                'price_selector': '.product-card .product-price',
                'site_name': 'TechBazaar'
            }
        ]
        
        all_products = []
        for site in sites:
            products = scrape_site(site['url'], site['name_selector'], site['price_selector'], site['site_name'])
            all_products.extend(products)
        
        # Filter products based on search query
        if search_query:
            all_products = [p for p in all_products if search_query in p['name'].lower()]
        
        # Sort by price (cheapest first)
        all_products.sort(key=lambda x: x['price'])
        
        return render_template('index.html', products=all_products, search_query=search_query)
    
    return render_template('index.html', products=None)

if __name__ == '__main__':
    app.run(debug=True)