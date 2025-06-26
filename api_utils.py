# api_utils.py
import requests
import streamlit as st

def call_openai_api(prompt, api_key, temperature=0.7):
    """Make API calls to OpenAI with error handling"""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            }
        )
        response.raise_for_status()  # Will raise an exception for HTTP errors
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None
    except (KeyError, IndexError) as e:
        st.error(f"Error parsing API response: {str(e)}")
        return None