# LiveKit Voice Agent - Laura SDR

Direct migration from Pipecat to LiveKit Cloud maintaining **EXACT** same configuration, speed, and functionality.

## 🚀 Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Local Development
```bash
pip install -r requirements.txt
python src/main.py
```

### 3. Deploy to Render
```bash
# Push to GitHub and connect to Render
# render.yaml is pre-configured
```

## ⚙️ Configuration

### Ultra-Fast VAD (IDENTICAL to Pipecat)
- **Start**: 0.2s (immediate response)
- **Stop**: 0.8s (ultra-fast)
- **Confidence**: 0.8
- **Min Volume**: 0.6

### TTS Configuration (IDENTICAL to Pipecat)
- **Primary**: ElevenLabs Flash V2.5 (ANDREA MEDELLIN voice)
- **Fallback**: OpenAI TTS Nova
- **Latency**: Optimized for streaming (level 4)

### LLM Configuration (IDENTICAL to Pipecat)
- **Model**: Groq Llama 3.3-70B Versatile
- **Prompt**: Laura SDR (exact same)
- **Temperature**: 0.7, Max tokens: 150

## 📞 Usage

### Inbound Calls (Auto-answer)
- Calls to `+18632190153` automatically connect to agent
- Creates room: `call-{participant.identity}`
- Laura starts conversation immediately

### Outbound Calls (API)
```bash
curl -X POST "http://localhost:8080/make-call" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

## 🏗️ Architecture

```
src/
├── agent/
│   ├── voice_agent.py        # Main LiveKit agent
│   ├── speech_handler.py     # STT→LLM→TTS pipeline
│   └── conversation.py       # Laura SDR logic
├── services/
│   ├── groq_service.py       # STT/LLM (identical config)
│   ├── tts_service.py        # ElevenLabs + OpenAI
│   └── outbound_service.py   # Outbound calling
└── utils/
    ├── config.py            # Environment configuration
    └── logger.py            # Structured logging
```

## 🎯 Laura SDR Behavior

**Objective**: Identify tech pain → Propose TDX solution → Schedule 25min meeting

**Conversation Flow**:
1. **Greeting**: "Hola, soy Laura de TDX"
2. **Pain ID**: Ask about slow service, overload, innovation needs
3. **Solution**: Connect pain to TDX AI/automation
4. **Close**: Schedule meeting to show results

## 🔧 Environment Variables

```env
# LiveKit
LIVEKIT_URL=wss://6jf4gz4gbna.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret

# API Keys
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENAI_API_KEY=your_openai_key

# SIP Trunks
OUTBOUND_TRUNK_ID=ST_GZ4Bo8JH4ly7
INBOUND_TRUNK_ID=ST_62xofSEmFyRe
```

## 📊 Performance

- **Latency**: <2s (same as Pipecat)
- **VAD Response**: 0.8s stop maximum
- **TTS Streaming**: Immediate with ElevenLabs Flash
- **Interruptions**: Natural and instant

## 🚨 Production Ready

- ✅ Health checks included
- ✅ Structured logging
- ✅ Error handling & fallbacks
- ✅ Auto-scaling configured
- ✅ Zero downtime deployment

## 📞 Contact

- **Inbound Number**: +18632190153
- **SIP URI**: 6jf4gz4gbna.sip.livekit.cloud
- **API Endpoint**: `/make-call` for outbound calls# Force redeploy Thu Jun 26 19:59:48 UTC 2025
