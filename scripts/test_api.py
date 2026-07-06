import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import settings
from langchain_openai import ChatOpenAI

def test_api():
    print("=" * 60)
    print("API DIAGNOSTIC UTILITY")
    print("=" * 60)
    
    # Check Env File Loading
    print(f"Loaded .env file: {os.path.exists('.env')}")
    print(f"OS Env OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY') is not None}")
    print(f"Settings LLM fields: {settings.llm}")
    
    # 2. Check OpenAI API Key
    api_key = settings.llm.openai_api_key
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("[-] Error: OPENAI_API_KEY is not defined in settings or os.environ!")
            return
        else:
            print("[!] Found OPENAI_API_KEY in os.environ but not in settings!")
        
    print(f"[+] API Key detected.")
    print(f"[+] Key preview: {api_key[:6]}...{api_key[-6:] if len(api_key) > 12 else ''}")
    
    # Identify provider
    if api_key.startswith("gsk_"):
        print("[!] Note: This key starts with 'gsk_', which is a GROQ API key.")
        provider = "groq"
        model_name = "llama-3.1-8b-instant"  # Default Groq model
        base_url = "https://api.groq.com/openai/v1"
    elif api_key.startswith("sk-"):
        print("[+] This key starts with 'sk-', which matches an OpenAI API key format.")
        provider = "openai"
        model_name = settings.llm.default_chat_model
        base_url = None
    else:
        print("[-] Warning: Unknown key format.")
        provider = "unknown"
        model_name = settings.llm.default_chat_model
        base_url = None

    print(f"[+] Selected Provider: {provider.upper()}")
    print(f"[+] Target Model: {model_name}")
    if base_url:
        print(f"[+] Base URL: {base_url}")
        
    # 3. Test Connection
    print("\n[~] Sending test completion request...")
    try:
        kwargs = {
            "model": model_name,
            "api_key": api_key,
            "temperature": 0.0,
            "max_retries": 1
        }
        if base_url:
            kwargs["base_url"] = base_url
            
        llm = ChatOpenAI(**kwargs)
        
        response = llm.invoke("Say 'Connection Successful' and nothing else.")
        content = response.content.strip()
        print(f"[+] Success! Response: {content}")
        print("\n[+] Verification PASSED. Your API configuration is working correctly!")
    except Exception as e:
        print(f"\n[-] Verification FAILED: {e}")
        print("\nSuggestions:")
        if provider == "groq":
            print("1. Set DEFAULT_LLM_PROVIDER=openai in .env (if you want to use the OpenAI compatible endpoint).")
            print("2. Ensure you have the correct model name. Groq does not support OpenAI models like 'gpt-4o'.")
            print("   You should set DEFAULT_CHAT_MODEL=llama-3.1-8b-instant in .env.")
        else:
            print("1. Check that your API key is correct and active.")
            print("2. Make sure your internet connection is stable and has access to api.openai.com.")

if __name__ == "__main__":
    test_api()
