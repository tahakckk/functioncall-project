import streamlit as st
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
import openai

# Sayfa yapılandırması
st.set_page_config(
    page_title="AI Asistan",
    page_icon="🤖",
    layout="centered"
)

# Özel CSS
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 18px;
    }
    .stButton > button {
        width: 100%;
        font-size: 18px;
        background-color: #4CAF50;
        color: white;
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
    }
    .chat-message.assistant {
        background-color: #475063;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_openai():
    """OpenAI istemcisini başlatır ve API anahtarını kontrol eder."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        st.error("OPENAI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")
        st.stop()
    
    openai.api_key = api_key
    return openai

def get_weather(city: str) -> Dict[str, Any]:
    """Belirtilen şehirdeki güncel hava durumunu döner."""
    weather_data = {
        "Ankara": {"description": "Güneşli", "temp": 25},
        "İstanbul": {"description": "Parçalı Bulutlu", "temp": 22},
        "İzmir": {"description": "Açık", "temp": 28}
    }
    return weather_data.get(city, {"description": "Bilinmiyor", "temp": 0})

def get_exchange_rate(base: str, target: str) -> float:
    """İki para birimi arasındaki güncel döviz kurunu döner."""
    rates = {
        "USD": {"EUR": 0.92, "TRY": 32.5},
        "EUR": {"USD": 1.09, "TRY": 35.3},
        "TRY": {"USD": 0.031, "EUR": 0.028}
    }
    return rates.get(base, {}).get(target, 1.0)

# Function schemas
function_schemas = [
    {
        "name": "get_weather",
        "description": "Belirtilen şehirdeki güncel hava durumunu döner.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Hava durumu öğrenilmek istenen şehir (örn: Ankara, İstanbul, İzmir)"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_exchange_rate",
        "description": "İki para birimi arasındaki güncel döviz kurunu döner.",
        "parameters": {
            "type": "object",
            "properties": {
                "base": {
                    "type": "string",
                    "description": "Kaynak para birimi (örn: USD, EUR, TRY)"
                },
                "target": {
                    "type": "string",
                    "description": "Hedef para birimi (örn: USD, EUR, TRY)"
                }
            },
            "required": ["base", "target"]
        }
    }
]

def process_user_query(client: openai, user_query: str) -> str:
    """Kullanıcı sorgusunu işler ve uygun fonksiyonu çağırır."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "Sen bir yardımcı asistansın. Kullanıcının sorularına yanıt vermek için verilen fonksiyonları kullanabilirsin."},
                {"role": "user", "content": user_query}
            ],
            functions=function_schemas,
            function_call="auto",
            temperature=0.7
        )

        message = response.choices[0].message

        if hasattr(message, 'function_call') and message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)

            if function_name == "get_weather":
                result = get_weather(**function_args)
                return f"{function_args['city']} şehrinde hava {result['description']} ve sıcaklık {result['temp']}°C."
            
            elif function_name == "get_exchange_rate":
                result = get_exchange_rate(**function_args)
                return f"1 {function_args['base']}, {result} {function_args['target']} değerindedir."

        return message.content if hasattr(message, 'content') else "Üzgünüm, bir yanıt oluşturulamadı."

    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"

def main():
    # Başlık
    st.title("🤖 AI Asistan")
    st.markdown("---")

    # OpenAI istemcisini başlat
    client = initialize_openai()

    # Sohbet geçmişini saklamak için session state kullan
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Örnek sorular
    st.markdown("### Örnek Sorular:")
    col1, col2 = st.columns(2)
    
    # Buton tıklamalarını işle
    if col1.button("Ankara'da hava nasıl?"):
        prompt = "Ankara'da hava nasıl?"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Düşünüyorum..."):
            response = process_user_query(client, prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    if col2.button("Dolar'ın Euro karşısındaki değeri nedir?"):
        prompt = "Dolar'ın Euro karşısındaki değeri nedir?"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Düşünüyorum..."):
            response = process_user_query(client, prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Sohbet geçmişini göster
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(message["content"])

    # Kullanıcı girişi
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0

    user_input = st.text_input("Mesajınızı yazın...", key=f"input_{st.session_state.input_key}")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Düşünüyorum..."):
            response = process_user_query(client, user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.input_key += 1
        st.rerun()

if __name__ == "__main__":
    main() 