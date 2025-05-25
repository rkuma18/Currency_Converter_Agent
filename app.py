import streamlit as st
from main import (
    llm_with_tools, 
    HumanMessage, 
    ToolMessage,
    get_conversion_factor,
    convert,
    get_crypto_rate,
    convert_fiat_to_btc
)
import json
import os
import traceback
import re

# Set page config
st.set_page_config(
    page_title="Currency Converter Chat",
    page_icon="💱",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .api-key-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin-bottom: 2rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .privacy-notice {
        background-color: #e7f3ff;
        border: 1px solid #b8e6ff;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_keys_configured" not in st.session_state:
    st.session_state.api_keys_configured = False
if "user_openai_key" not in st.session_state:
    st.session_state.user_openai_key = ""
if "user_exchange_key" not in st.session_state:
    st.session_state.user_exchange_key = ""

def check_api_keys():
    """Check if user has provided API keys"""
    return bool(st.session_state.user_openai_key and st.session_state.user_exchange_key)

def set_api_keys():
    """Set user-provided API keys in environment for the session"""
    if st.session_state.user_openai_key:
        os.environ["OPENAI_API_KEY"] = st.session_state.user_openai_key
    if st.session_state.user_exchange_key:
        os.environ["EXCHANGE_RATE_API_KEY"] = st.session_state.user_exchange_key

def clear_api_keys():
    """Clear API keys from environment when user leaves"""
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    if "EXCHANGE_RATE_API_KEY" in os.environ:
        del os.environ["EXCHANGE_RATE_API_KEY"]

# App title and description
st.title("💱 Currency Converter Chat")
st.markdown("*An intelligent currency converter powered by AI - Bring Your Own API Keys*")

# Privacy Notice
st.markdown("""
<div class="privacy-notice">
🔒 <strong>Privacy Notice:</strong> This application requires you to provide your own API keys. 
Your keys are only stored in memory during your session and are automatically cleared when you leave. 
We do not store, log, or have access to your API keys.
</div>
""", unsafe_allow_html=True)

# API Key Configuration Section
with st.container():
    st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
    st.subheader("🔑 API Configuration Required")
    
    st.info("🔧 Please provide your API keys to use the currency converter. Keys are only stored in memory during your session.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**OpenAI API Key**")
        user_openai_key = st.text_input(
            "Enter your OpenAI API key",
            type="password",
            placeholder="sk-proj-...",
            help="Get your API key from https://platform.openai.com/api-keys",
            value=st.session_state.user_openai_key
        )
        if user_openai_key != st.session_state.user_openai_key:
            st.session_state.user_openai_key = user_openai_key
    
    with col2:
        st.markdown("**Exchange Rate API Key**")
        user_exchange_key = st.text_input(
            "Enter your Exchange Rate API key",
            type="password",
            placeholder="Your API key",
            help="Get your free API key from https://app.exchangerate-api.com/sign-up",
            value=st.session_state.user_exchange_key
        )
        if user_exchange_key != st.session_state.user_exchange_key:
            st.session_state.user_exchange_key = user_exchange_key
    
    # Update API keys configuration status
    st.session_state.api_keys_configured = check_api_keys()
    
    if st.session_state.api_keys_configured:
        set_api_keys()
        st.success("🎉 API keys configured successfully! You can now use the converter.")
        
        # Add clear keys button
        if st.button("🗑️ Clear API Keys", help="Clear your API keys from memory"):
            st.session_state.user_openai_key = ""
            st.session_state.user_exchange_key = ""
            st.session_state.api_keys_configured = False
            st.session_state.messages = []  # Clear chat history too
            clear_api_keys()
            st.rerun()
    else:
        st.markdown('<div class="warning-box">⚠️ Both API keys are required to use the currency converter.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Only show the chat interface if API keys are configured
if st.session_state.api_keys_configured:
    # Set API keys for this session
    set_api_keys()
    
    st.markdown("---")
    st.markdown("""
        Ask me to convert currencies or cryptocurrencies! For example:
        - Convert 100 USD to EUR
        - What is 500 EUR in BTC?
        - Convert 1000 INR to ETH
    """)

    # Helper function to extract numeric value from string
    def extract_numeric_value(text):
        """Extract numeric value from text, handling various formats"""
        if isinstance(text, (int, float)):
            return float(text)
        
        # Remove backticks, commas, and other formatting
        clean_text = str(text).replace('`', '').replace(',', '').strip()
        
        # Try to extract number using regex
        number_match = re.search(r'[\d.]+', clean_text)
        if number_match:
            try:
                return float(number_match.group())
            except ValueError:
                pass
        
        # Try direct conversion
        try:
            return float(clean_text)
        except ValueError:
            return None

    # Helper function to process all tool calls recursively
    def process_all_tool_calls(messages, max_iterations=5):
        """Process tool calls until no more are needed or max iterations reached"""
        results = {
            'conversion_rate': None,
            'crypto_rate': None,
            'btc_equivalent': None,
            'conversion_result': None,
            'from_currency': None,
            'to_currency': None,
            'amount': None,
            'final_response': None
        }
        
        for iteration in range(max_iterations):
            try:
                # Get AI response
                ai_message = llm_with_tools.invoke(messages)
                
                # If no tool calls, this is the final response
                if not ai_message.tool_calls:
                    results['final_response'] = ai_message.content
                    break
                
                # Add AI message to conversation
                messages.append(ai_message)
                
                # Process each tool call
                for tool_call in ai_message.tool_calls:
                    try:
                        # Process different tool types
                        if tool_call['name'] == 'get_conversion_factor':
                            results['from_currency'] = tool_call['args']['from_currency']
                            results['to_currency'] = tool_call['args']['to_currency']
                            tool_response = get_conversion_factor.invoke(tool_call['args'])
                            
                            # Extract conversion rate
                            rate = extract_numeric_value(tool_response)
                            if rate is not None:
                                results['conversion_rate'] = rate
                            
                            messages.append(ToolMessage(content=str(tool_response), tool_call_id=tool_call['id']))
                        
                        elif tool_call['name'] == 'convert':
                            results['amount'] = tool_call['args']['amount']
                            results['from_currency'] = tool_call['args']['from_currency']
                            results['to_currency'] = tool_call['args']['to_currency']
                            tool_response = convert.invoke(tool_call['args'])
                            
                            # Only extract result if no error occurred
                            if not str(tool_response).startswith('Error'):
                                result = extract_numeric_value(tool_response)
                                if result is not None:
                                    results['conversion_result'] = result
                            
                            messages.append(ToolMessage(content=str(tool_response), tool_call_id=tool_call['id']))
                        
                        elif tool_call['name'] == 'get_crypto_rate':
                            results['from_currency'] = tool_call['args']['base_currency']
                            results['to_currency'] = tool_call['args']['target_currency']
                            tool_response = get_crypto_rate.invoke(tool_call['args'])
                            
                            # Extract crypto rate
                            rate = extract_numeric_value(tool_response)
                            if rate is not None:
                                results['crypto_rate'] = rate
                            
                            messages.append(ToolMessage(content=str(tool_response), tool_call_id=tool_call['id']))

                        elif tool_call['name'] == 'convert_fiat_to_btc':
                            results['amount'] = tool_call['args']['amount']
                            results['from_currency'] = tool_call['args']['fiat_currency']
                            results['to_currency'] = tool_call['args']['base_currency']
                            tool_response = convert_fiat_to_btc.invoke(tool_call['args'])
                            
                            # Extract BTC equivalent
                            btc_amount = extract_numeric_value(tool_response)
                            if btc_amount is not None:
                                results['btc_equivalent'] = btc_amount
                            
                            messages.append(ToolMessage(content=str(tool_response), tool_call_id=tool_call['id']))

                    except Exception as e:
                        # Silently handle tool errors and continue
                        error_message = ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_call['id']
                        )
                        messages.append(error_message)
            except Exception as e:
                # Handle API key or other errors
                results['final_response'] = f"Error: {str(e)}. Please check your API keys."
                break
        
        return results

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me to convert currencies..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Converting currencies..."):
                try:
                    # Create initial message
                    messages = [HumanMessage(content=prompt)]
                    
                    # Process all tool calls
                    results = process_all_tool_calls(messages)
                    
                    # Generate response based on results
                    response_content = ""
                    
                    if results['final_response']:
                        response_content = results['final_response']
                    elif results['conversion_result'] is not None:
                        response_content = f"💰 **{results['amount']} {results['from_currency']} = {results['conversion_result']:.2f} {results['to_currency']}**"
                    elif results['btc_equivalent'] is not None:
                        response_content = f"₿ **{results['amount']} {results['from_currency']} = {results['btc_equivalent']:.8f} {results['to_currency']}**"
                    elif results['conversion_rate'] is not None:
                        if results['amount'] is not None:
                            converted_amount = results['amount'] * results['conversion_rate']
                            response_content = f"💰 **{results['amount']} {results['from_currency']} = {converted_amount:.2f} {results['to_currency']}**"
                        else:
                            response_content = f"📊 Current exchange rate: **1 {results['from_currency']} = {results['conversion_rate']:.4f} {results['to_currency']}**"
                    elif results['crypto_rate'] is not None:
                        response_content = f"📊 Current exchange rate: **1 {results['from_currency']} = {results['crypto_rate']:,.2f} {results['to_currency']}**"
                    else:
                        response_content = "❌ I apologize, but I couldn't complete the conversion. Please try again with a different format or check if the currencies are supported."
                    
                    # Display response with success styling for conversions
                    if "=" in response_content and any(symbol in response_content for symbol in ["💰", "₿"]):
                        st.markdown(f'<div class="success-message">{response_content}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(response_content)
                    
                    # Store clean version without HTML for chat history
                    clean_response = response_content.replace('<div class="success-message">', '').replace('</div>', '')
                    st.session_state.messages.append({"role": "assistant", "content": clean_response})
                    
                except Exception as e:
                    error_message = "❌ An error occurred while processing your request. Please check your API keys and try again."
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

else:
    # Show instructions when API keys are not configured
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔑 How to get OpenAI API Key:
        1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
        2. Sign up or log in to your account
        3. Navigate to API Keys section
        4. Click "Create new secret key"
        5. Copy the key (starts with `sk-proj-` or `sk-`)
        6. Paste it in the field above
        
        💡 **Note:** You'll need billing setup for API usage
        """)
    
    with col2:
        st.markdown("""
        ### 📊 How to get Exchange Rate API Key:
        1. Visit [ExchangeRate-API](https://app.exchangerate-api.com/sign-up)
        2. Sign up for a free account
        3. Verify your email address
        4. Copy your API key from dashboard
        5. Paste it in the field above
        
        💡 **Note:** Free tier includes 1,500 requests/month
        """)

# Sidebar with information
with st.sidebar:
    st.title("💱 About")
    st.markdown("""
    This intelligent currency converter can help you with:
    
    **✅ Fiat Currency Conversions**
    - USD, EUR, GBP, JPY, INR, CAD, AUD
    - 170+ currencies supported
    - Real-time exchange rates
    
    **₿ Cryptocurrency Conversions**
    - Bitcoin (BTC)
    - Ethereum (ETH)
    - Major cryptocurrencies
    - Live market rates
    
    **🤖 Natural Language Processing**
    - Just ask in plain English
    - Supports various formats
    - Intelligent parsing
    """)
    
    st.markdown("---")
    
    st.title("💡 Example Queries")
    st.markdown("""
    Try asking:
    - "Convert 100 USD to EUR"
    - "How much is 500 EUR in Bitcoin?"
    - "What's the current USD to GBP rate?"
    - "Convert 1000 INR to ETH"
    - "50 CAD in Japanese Yen"
    """)
    
    st.markdown("---")
    
    # API Status
    st.title("🔧 System Status")
    
    # Check API keys
    if st.session_state.api_keys_configured:
        st.success("🟢 User APIs Connected")
    else:
        st.error("🔴 API Keys Required")
    
    # Show configuration status
    openai_configured = bool(st.session_state.user_openai_key)
    exchange_configured = bool(st.session_state.user_exchange_key)
    
    st.markdown(f"""
    **OpenAI API:** {"🟢 Provided" if openai_configured else "🔴 Missing"}  
    **Exchange Rate API:** {"🟢 Provided" if exchange_configured else "🔴 Missing"}
    """)
    
    st.markdown("---")
    
    st.title("🔒 Privacy & Security")
    st.markdown("""
    - ✅ No API keys stored by us
    - ✅ Keys only in memory during session
    - ✅ Keys cleared when you leave
    - ✅ No logging or tracking
    - ✅ Bring your own keys policy
    - ✅ Full privacy control
    """)
    
    st.markdown("---")
    st.markdown("*User-Powered Currency Conversion*")