# CyberPal '95 — Retro Chatbot

1990'lar temalı eğitim chatbot'u. Backend: FastAPI + Google Gemini. Frontend: Vanilla HTML/CSS/JS (Windows 95/98 estetiği).

## Kurulum (Windows / PowerShell)

Proje klasörüne girin:

```powershell
cd C:\Users\ozgee\PycharmProjects\RetroChatbot
```

Sanal ortamı etkinleştirin (yoksa oluşturun):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Bağımlılıkları kurun:

```powershell
pip install -r requirements.txt
```

`.env` dosyasını oluşturup Gemini anahtarınızı yazın ([Google AI Studio](https://aistudio.google.com/apikey)):

```powershell
copy .env.example .env
notepad .env
```

`.env` içinde:

```
GEMINI_API_KEY=gerçek_anahtarınız
GEMINI_MODEL=gemini-2.5-flash
```

Sunucuyu başlatın:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Tarayıcıda açın: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Notlar

- Projeyi hemen tarayıcıda görüntülemek isterseniz [Retro Chatbot Canlı Demo](https://retro-chatbot-eyxb.onrender.com) bağlantısını ziyaret edebilirsiniz.
- Chatbot bir yapay zeka olduğunu unutmaz, takvim yılı olarak ~1998'de yaşar.
- Model adını `.env` içindeki `GEMINI_MODEL` ile değiştirebilirsiniz.

---

> Bu proje, **Atıl Samancıoğlu** eğitimi referans alınarak eğitim amaçlı geliştirilmiştir.
