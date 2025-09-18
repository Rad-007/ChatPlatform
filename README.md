# Chatbot Platform (Django)

A mini multi-tenant chatbot platform where users can register, create multiple chatbots, customize design and AI settings, and embed them on any website with a JavaScript snippet. Includes basic analytics and mock plan-gating. AI is powered by Pydantic AI using the Groq LLM.

## Features
- User accounts: register, login, logout
- Create multiple chatbots per user
- Customizable design: primary color, position, welcome message
- AI settings per bot: system prompt, model, temperature
- Embed snippet: a single `<script>` tag to include on any site
- Conversations API: send messages, optional SSE streaming endpoint
- Basic analytics on dashboard (conversation/message counts)
- Multi-user isolation on queries
- Mock plan gate: Free plan limited to 1 bot (upgrade flow is mocked)

## Tech Stack
- Django 4
- Django REST Framework (lightweight usage)
- Pydantic AI + Groq SDK
- Channels (configured), SSE Streaming via `StreamingHttpResponse`

## Setup
1. Python 3.10+
2. (Optional but recommended) Create and activate a virtual environment
3. Install dependencies
4. Configure environment variables
5. Run migrations
6. Start the server

### 1) Virtual environment (Windows PowerShell)
```powershell
python -m venv env
./env/Scripts/Activate.ps1
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Environment variables
Create a `.env` file in the root directory of the project and add the following variables:
```
GROQ_API_KEY=your_groq_api_key_here
DJANGO_DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
RAZORPAY_KEY_ID=your_razorpay_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
```

### 4) Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5) Create superuser (optional)
```powershell
python manage.py createsuperuser
```

### 6) Run the dev server
```powershell
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Usage
- Register a new account
- Go to Dashboard
- Create a Bot (configure appearance and AI settings)
- Click “Embed” and copy the script tag snippet to your website

### Endpoints
- Dashboard: `/dashboard/`
- Accounts: `/accounts/login/`, `/accounts/register/`, `/accounts/logout/`
- Widget script: `/widget/embed/<token>.js`
- Widget page (iframe): `/widget/b/<token>/`
- API send message (POST JSON): `/api/send/<token>/`
  - Body: `{ "message": "Hi", "session_id": "<client_session_id>" }`
- API stream response (SSE): `/api/stream/<token>/?session_id=<id>`

## Notes
- For development, CORS is wide open in `chatbot_platform/settings.py`.
- SSE streaming is a simple chunked approach. For production-grade streaming, consider using Channels consumers or ASGI-native streaming and robust retry logic on the client.
- The Plan gate is mocked with a profile `plan` field; upgrade UI is not implemented.

## Troubleshooting
- If you see "GROQ_API_KEY not configured.", set the environment variable in `.env`.
- Ensure your Groq key has access to the selected model (default: `llama3-8b-8192`).
- If `pydantic_ai` import fails, we fall back to a dev echo response.
