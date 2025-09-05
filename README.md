# AI Call Assistant - Production Ready System

A complete AI-powered call assistant system that can handle incoming calls, answer questions using RAG (Retrieval-Augmented Generation), and book appointments automatically.

## Features

- **Multi-tenant Support**: Each client gets their own AI assistant
- **RAG-based Responses**: AI answers using client-specific knowledge base
- **Voice Integration**: Custom voices using ElevenLabs
- **Appointment Booking**: Automatic appointment booking via N8N webhooks
- **Call Analytics**: Detailed call tracking and analytics
- **File Upload**: Support for PDF, DOCX, and text files
- **Production Ready**: Docker deployment, monitoring, logging

## Quick Start

1. **Environment Setup**
```bash
cp .env.example .env
# Fill in your API keys and configuration
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Start Services**
```bash
docker-compose up -d
```

4. **Create Your First Client**
```bash
python scripts/example_client_setup.py
```

## API Endpoints

### Client Management
- `POST /clients` - Create new client
- `GET /clients` - List all clients
- `GET /clients/{client_id}` - Get specific client
- `PUT /clients/{client_id}` - Update client

### Knowledge Management
- `POST /clients/{client_id}/knowledge/text` - Add text knowledge
- `POST /clients/{client_id}/knowledge/upload` - Upload file knowledge

### Call Handling
- `POST /call/incoming` - Handle incoming Twilio calls
- `POST /call/process-speech` - Process speech input

### Analytics
- `GET /clients/{client_id}/analytics` - Client analytics
- `GET /clients/{client_id}/calls` - Call history

## Twilio Setup

1. Purchase a phone number in Twilio
2. Configure webhook URL: `https://yourdomain.com/call/incoming`
3. Set HTTP method to POST
4. Add the phone number to your client record

## N8N Integration

Create a workflow in N8N with a webhook trigger to handle appointment bookings:

1. Webhook Trigger
2. Data processing (validate appointment details)
3. Calendar integration (Google Calendar, Outlook, etc.)
4. Confirmation email/SMS
5. Response back to the system

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY` - OpenAI API key for LLM
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `ELEVENLABS_API_KEY` - ElevenLabs API key
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key

## Production Deployment

1. **Docker Deployment**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

2. **Environment Configuration**
```bash
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

3. **SSL Certificate**
Configure SSL certificate for HTTPS (required for Twilio webhooks)

## Monitoring

- Health check: `GET /health`
- System metrics: `GET /monitoring/system/health`
- Call metrics: `GET /monitoring/metrics/calls`

## Security Features

- JWT authentication for API access
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure webhook verification

## Scalability

- Horizontal scaling with multiple app instances
- Redis for session management
- Celery for background task processing
- Database connection pooling

## Testing

```bash
pytest tests/ -v
```

## License

This project is proprietary software designed for commercial use.