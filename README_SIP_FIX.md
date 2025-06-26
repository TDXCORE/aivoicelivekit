# Twilio-LiveKit SIP Integration - Fixes Applied

## 🔧 Issues Fixed

### 1. **LiveKit Agents Compatibility Issue**
**Problem**: `AttributeError: 'str' object has no attribute 'value'`
**Solution**: Updated `src/main.py` to use string value `"room"` instead of `WorkerType.ROOM` enum.

### 2. **Incorrect Service Type**
**Problem**: Service configured as "worker" instead of "web"
**Solution**: Updated `render.yaml` to use `type: web` for proper SIP handling.

### 3. **Wrong Call Approach**
**Problem**: Using HTTP webhooks instead of SIP direct connection
**Solution**: Updated `simple_test_call.py` to use SIP dialing with TwiML.

### 4. **Version Compatibility**
**Problem**: Loose version constraints causing compatibility issues
**Solution**: Pinned `livekit-agents==1.1.4` in `requirements.txt`.

## 🏗️ Correct Architecture

```
Phone Call → Twilio PSTN → Twilio SIP Trunk → LiveKit SIP → LiveKit Room → Voice Agent
```

## 📋 SIP Configuration

Your current SIP setup should be:

- **Twilio SIP Trunk URI**: `aivoicetdx.pstn.twilio.com`
- **LiveKit SIP URI**: `6jf4gz4gbna.sip.livekit.cloud`
- **Dispatch Rule**: `SDR_43NLS8ztrysm → Room: call-{participant.identity}`
- **Inbound Trunk**: `ST_62xofSEmFyRe`
- **Outbound Trunk**: `ST_G24Bo8JH4iy7`

## 🚀 How to Test

### 1. Run Diagnostics
```bash
python diagnose_sip_setup.py
```

This will check:
- Environment variables
- Twilio connection
- LiveKit connection
- SIP configuration

### 2. Make a Test Call
```bash
python simple_test_call.py --to +1234567890
```

### 3. Monitor Logs
Check Render logs for:
- Agent startup
- SIP call detection
- Participant connections

## 🔍 Expected Log Flow

### Successful Call Flow:
1. **Agent Startup**:
   ```
   INFO:__main__:Starting LiveKit Voice Agent for Laura SDR...
   INFO:livekit.agents:registered worker
   ```

2. **SIP Call Detection**:
   ```
   INFO:__main__:Detected SIP call room: call-caller-1234567890
   INFO:__main__:Participant connected to room call-caller-1234567890: caller-1234567890
   ```

3. **Audio Processing**:
   ```
   INFO:__main__:Audio track subscribed from caller-1234567890
   INFO:__main__:Starting audio stream handling
   ```

## 🛠️ Key Changes Made

### `src/main.py`
- Changed `worker_type=WorkerType.ROOM` to `worker_type="room"`

### `render.yaml`
- Changed `type: worker` to `type: web`

### `simple_test_call.py`
- Removed HTTP webhook approach
- Added SIP dialing with TwiML
- Uses correct SIP trunk URI

### `requirements.txt`
- Pinned LiveKit agents version to `1.1.4`

### `src/agent/voice_agent.py`
- Added SIP call room detection
- Enhanced logging for debugging

## 🔧 Troubleshooting

### If calls still fail:

1. **Check SIP Trunk Configuration**:
   - Verify dispatch rule points to correct LiveKit SIP endpoint
   - Ensure trunk is active and properly configured

2. **Check LiveKit SIP Settings**:
   - Verify SIP endpoint is enabled
   - Check room creation permissions

3. **Network Connectivity**:
   - Ensure Twilio can reach LiveKit SIP endpoint
   - Check firewall/security group settings

4. **Agent Status**:
   - Verify agent is running and registered
   - Check for any startup errors

## 📞 Call Flow Explanation

1. **Outbound Call**: `simple_test_call.py` creates a Twilio call with TwiML that dials the SIP trunk
2. **SIP Routing**: Twilio routes the call to LiveKit via SIP trunk `aivoicetdx.pstn.twilio.com`
3. **Room Creation**: LiveKit dispatch rule creates room `call-{participant.identity}`
4. **Agent Assignment**: LiveKit agent joins the room and handles the conversation
5. **Audio Processing**: Agent processes audio using Groq STT, LLM, and TTS services

## 🎯 Next Steps

1. Deploy the updated code to Render
2. Run the diagnostic script to verify setup
3. Test with a real phone call
4. Monitor logs for any remaining issues

The main issue was the architectural mismatch - you were trying to use HTTP webhooks when the SIP trunk should connect directly to LiveKit. Now the flow is correct: Twilio SIP → LiveKit SIP → Voice Agent.
