import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
import requests
import json

def get_openai_client():
    """Get OpenAI client using user-provided API key from environment"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not provided by user")
    return ChatOpenAI(api_key=api_key, model="gpt-4")

def get_exchange_api_key():
    """Get Exchange Rate API key provided by user"""
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        raise ValueError("Exchange Rate API key not provided by user")
    return api_key

@tool
def get_conversion_factor(from_currency: str, to_currency: str) -> str:
    """Get the conversion factor between two currencies."""
    try:
        api_key = get_exchange_api_key()
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency.upper()}/{to_currency.upper()}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("result") == "success":
            rate = data.get("conversion_rate")
            return f"1 {from_currency.upper()} = {rate} {to_currency.upper()}"
        else:
            return f"Error: {data.get('error-type', 'Unknown error')}"
    except Exception as e:
        return f"Error fetching conversion rate: {str(e)}"

@tool
def convert(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another."""
    try:
        api_key = get_exchange_api_key()
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency.upper()}/{to_currency.upper()}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("result") == "success":
            rate = data.get("conversion_rate")
            converted_amount = amount * rate
            return f"{amount} {from_currency.upper()} = {converted_amount:.2f} {to_currency.upper()}"
        else:
            return f"Error: {data.get('error-type', 'Unknown error')}"
    except Exception as e:
        return f"Error converting currency: {str(e)}"

@tool
def get_crypto_rate(base_currency: str, target_currency: str) -> str:
    """Get cryptocurrency exchange rate using CoinGecko API (free, no key required)."""
    try:
        # Map common crypto symbols to CoinGecko IDs
        crypto_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'LTC': 'litecoin',
            'BCH': 'bitcoin-cash',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'XRP': 'ripple',
            'USDT': 'tether',
            'USDC': 'usd-coin',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2'
        }
        
        crypto_id = crypto_map.get(base_currency.upper())
        if not crypto_id:
            return f"Error: Cryptocurrency {base_currency} not supported. Supported: {', '.join(crypto_map.keys())}"
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={target_currency.lower()}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if crypto_id in data and target_currency.lower() in data[crypto_id]:
            rate = data[crypto_id][target_currency.lower()]
            return f"1 {base_currency.upper()} = {rate:,.2f} {target_currency.upper()}"
        else:
            return f"Error: Could not fetch rate for {base_currency} to {target_currency}"
    except Exception as e:
        return f"Error fetching crypto rate: {str(e)}"

@tool
def convert_fiat_to_btc(amount: float, fiat_currency: str, base_currency: str = "BTC") -> str:
    """Convert fiat currency to Bitcoin."""
    try:
        # First get fiat to USD rate if not USD
        if fiat_currency.upper() != "USD":
            api_key = get_exchange_api_key()
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{fiat_currency.upper()}/USD"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("result") == "success":
                usd_amount = amount * data.get("conversion_rate")
            else:
                return f"Error: {data.get('error-type', 'Unknown error')}"
        else:
            usd_amount = amount
        
        # Get BTC price in USD using CoinGecko (free API)
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'bitcoin' in data and 'usd' in data['bitcoin']:
            btc_price = data['bitcoin']['usd']
            btc_amount = usd_amount / btc_price
            return f"{amount} {fiat_currency.upper()} = {btc_amount:.8f} BTC"
        else:
            return "Error: Could not fetch Bitcoin price"
    except Exception as e:
        return f"Error converting to Bitcoin: {str(e)}"

# Initialize tools list
tools = [get_conversion_factor, convert, get_crypto_rate, convert_fiat_to_btc]

# Lazy-loaded LLM class that only initializes when API keys are available
class LazyLLM:
    def __init__(self):
        self._llm = None
    
    def _ensure_llm(self):
        """Ensure LLM is initialized with current API keys"""
        try:
            # Always create fresh instance to use current environment variables
            llm = get_openai_client()
            self._llm = llm.bind_tools(tools)
        except ValueError as e:
            raise ValueError(f"Please provide valid API keys: {str(e)}")
    
    def invoke(self, *args, **kwargs):
        """Invoke the LLM, ensuring it's initialized first"""
        self._ensure_llm()
        return self._llm.invoke(*args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate all other attributes to the LLM instance"""
        self._ensure_llm()
        return getattr(self._llm, name)

# Create the lazy LLM instance
llm_with_tools = LazyLLM()

# Export everything needed by Streamlit
__all__ = [
    'llm_with_tools',
    'HumanMessage', 
    'ToolMessage',
    'get_conversion_factor',
    'convert',
    'get_crypto_rate',
    'convert_fiat_to_btc'
]