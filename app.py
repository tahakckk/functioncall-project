import os
import json
import openai
from typing import Dict, Any
from dotenv import load_dotenv

def initialize_openai():
    """OpenAI istemcisini başlatır ve API anahtarını kontrol eder."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")
    
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
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen bir yardımcı asistansın. Kullanıcının sorularına yanıt vermek için verilen fonksiyonları kullanabilirsin."},
                {"role": "user", "content": user_query}
            ],
            functions=function_schemas,
            function_call="auto"
        )

        message = response.choices[0].message

        if message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)

            if function_name == "get_weather":
                result = get_weather(**function_args)
                return f"{function_args['city']} şehrinde hava {result['description']} ve sıcaklık {result['temp']}°C."
            
            elif function_name == "get_exchange_rate":
                result = get_exchange_rate(**function_args)
                return f"1 {function_args['base']}, {result} {function_args['target']} değerindedir."

        return message.content

    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"

def main():
    try:
        print("OpenAI API bağlantısı kuruluyor...")
        client = initialize_openai()
        print("Bağlantı başarılı!")
        
        print("\nMerhaba! Size nasıl yardımcı olabilirim? (Çıkmak için 'q' yazın)")
        print("Örnek sorular:")
        print("- Ankara'da hava nasıl?")
        print("- Dolar'ın Euro karşısındaki değeri nedir?")
        print("- İstanbul'da sıcaklık kaç derece?")
        
        while True:
            user_input = input("\nSoru: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() == 'q':
                print("\nGörüşmek üzere!")
                break
                
            response = process_user_query(client, user_input)
            print(f"\nYanıt: {response}")
            
    except Exception as e:
        print(f"\nKritik bir hata oluştu: {str(e)}")
        print(f"Hata türü: {type(e).__name__}")
        print("Lütfen .env dosyasını ve internet bağlantınızı kontrol edin.")
        print("\n.env dosyası içeriği kontrol ediliyor...")
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                print("API Key uzunluğu:", len(content.split('=')[1].strip()))
        except Exception as env_error:
            print(f".env dosyası okunamadı: {str(env_error)}")

if __name__ == "__main__":
    main() 