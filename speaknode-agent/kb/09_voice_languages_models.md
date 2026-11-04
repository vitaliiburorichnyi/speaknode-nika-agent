# Voice languages models

<!-- source: https://docs.speaknode.com/en/features/voice -->
## Voice & Communication
WebRTC-based real-time voice communication in Speaknode
Speaknode uses WebRTC for real-time voice communication between users and AI agents.

## How It Works
A LiveKit room is created when an agent is dispatched
The AI agent (Python worker) joins the room and starts listening
The user connects via browser (widget or client) or phone
Audio streams in both directions in real time
The session is recorded automatically (audio egress)

## Voice Pipeline
User speaks → WebRTC audio → STT (speech-to-text) →
LLM processes text → generates response →
TTS (text-to-speech) → WebRTC audio → User hears

## Speech-to-Text (STT)
Converts user speech to text for the LLM. STT provider is configurable
per agent.

## Large Language Model (LLM)
Processes the conversation and generates responses. LLM provider and
model are configurable per agent (direct vendor API or aggregator).

## Text-to-Speech (TTS)
Converts agent responses to speech. TTS provider is configurable per
agent.

## Voice Activity Detection (VAD)
Detects when the user starts and stops speaking. Controls turn-taking behavior — when the agent should start or stop talking.

## Audio Recording
Every conversation is automatically recorded via LiveKit Egress. Recordings include:
Full audio of the session (composite recording)
Individual participant tracks
Stored in S3-compatible object storage

## Real-Time Notifications
The platform uses SignalR to notify the frontend about session events:
Agent Ready — agent has joined the room
Session Completed — conversation ended, audio available

## Session Lifecycle
| Status | Description
| Pending | Session created, room not yet ready
| Dispatching | LiveKit room created, waiting for agent to join
| Active | Agent joined, conversation in progress
| Completed | Conversation ended normally
| Failed | Error occurred during session
