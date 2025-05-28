# Function Calling Demo

Bu proje, OpenAI ChatGPT API'sini kullanarak function calling özelliğini gösteren bir demo uygulamasıdır.

## Özellikler

- Doğal dil ile fonksiyon çağırma
- Hava durumu sorgulama
- Döviz kuru sorgulama
- Türkçe dil desteği

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyası oluşturun ve OpenAI API anahtarınızı ekleyin:
```
OPENAI_API_KEY=your-api-key-here
```

## Kullanım

Uygulamayı başlatmak için:
```bash
python app.py
```

Örnek sorular:
- "Ankara'da hava nasıl?"
- "Dolar'ın Euro karşısındaki değeri nedir?"
- "İstanbul'da sıcaklık kaç derece?"

## Notlar

- Bu demo uygulaması, gerçek API'ler yerine sabit değerler kullanmaktadır.
- Gerçek bir uygulamada, hava durumu ve döviz kuru verilerini gerçek API'lerden almanız gerekecektir. 