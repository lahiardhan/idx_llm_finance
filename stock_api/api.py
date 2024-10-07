import os
import requests
from dotenv import load_dotenv
from .utils import retrieve_from_endpoint
from langchain_core.tools import tool

# Memuat variabel lingkungan dari file .env
load_dotenv()

# Your keys setup (you can replace this with secure storage methods for deployment)
SECTORS_API_KEY = os.getenv('SECTORS_API_KEY')

@tool
def get_top_companies_by_tx_volume(start_date: str, end_date: str, top_n: int = 5) -> str:
    """Get top companies by transaction volume"""
    url = f"https://api.sectors.app/v1/most-traded/?start={start_date}&end={end_date}&n_stock={top_n}"
    return retrieve_from_endpoint(url, SECTORS_API_KEY)

@tool
def get_company_overview(stock: str) -> str:
    """Get the overview of a stock, including email, address, phone number, market cap information, listing date etc"""
    url = f"https://api.sectors.app/v1/company/report/{stock}/?sections=overview"
    print(url)
    return retrieve_from_endpoint(url, SECTORS_API_KEY)

@tool
def get_daily_tx(stock: str, start_date: str, end_date: str) -> str:
    """Get daily transaction for a stock"""
    url = f"https://api.sectors.app/v1/daily/{stock}/?start={start_date}&end={end_date}"
    print(url)
    return retrieve_from_endpoint(url, SECTORS_API_KEY)

@tool
def get_performance_since_ipo(stock: str) -> str:
    """Get stock performance after IPO listing"""
    url = f"https://api.sectors.app/v1/listing-performance/{stock}/"
    print(url)
    return retrieve_from_endpoint(url, SECTORS_API_KEY)