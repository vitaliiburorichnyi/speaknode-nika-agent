# First agent

<!-- source: https://docs.speaknode.com/en/features/agents -->
## AI Agents
Core AI agent configuration and capabilities in Speaknode
AI agents are the core of Speaknode. Each agent is a configurable voice assistant that can hold real-time conversations with users.

## Agent Configuration
## Basic Settings
Title — agent name (up to 50 characters)
System Prompt — instructions that define agent behavior, personality, and knowledge. Supports dynamic variables with {{variable_name}} syntax
Temperature — controls randomness of LLM responses (0 = deterministic, 1 = creative)
Token Limit — maximum token usage per conversation

## Language & Localization
Each agent supports multiple languages. Per language you configure:
First Message — greeting the agent says when the conversation starts
TTS Voice — text-to-speech voice and provider
Speech Speed — playback speed multiplier
Background Sound — ambient sound during conversation (silence, office, coffee shop, etc.)
The agent can automatically detect the user's language and switch to the appropriate locale.

## LLM Model
Select the large language model that powers the agent's reasoning:
LLM provider and model version
Temperature and additional model-specific properties
Recommended Models for Voice Sales
The table below ranks the best LLM options for outbound voice sales scenarios — optimised for low latency, Russian language quality, and agent/tool-call reliability.
Loading models…
Key factors for voice:
Latency (TTFT) — time-to-first-token directly affects perceived responsiveness; reasoning models (chain-of-thought) add 300–800 ms
Russian quality — Qwen3 and GLM-4.7 are trained on large Cyrillic corpora
Controllability — how well the model follows persona, objection-handling scripts, and tool-call schemas without hallucinating extra steps
Per-model breakdown
🥇 Qwen3-30B-A3B (DeepInfra) — Alibaba's mid-tier MoE flagship: 30.5B total parameters with 3.3B active per token (8 of 128 experts routed), unified thinking / non-thinking modes (we use non-thinking for voice). In short turns it stays composed, avoids drifting into marketing tone, follows system-prompt rules tightly (independent IFEval ≈ 84.7%), and reliably calls tools per schema (BFCL v3 ≈ 65.1). Strong Russian — trained on substantial Cyrillic corpora, doesn't "slip" into English when the caller code-switches. Holds a sales-manager persona well: short replies, one question per turn, few digressions. The optimal baseline for Voice Sales by quality-vs-predictability.
Sources: Qwen3 technical report (arXiv 2505.09388), HuggingFace model card, BFCL v3 leaderboard.
🥈 GLM-4.7 non-reasoning (Cerebras) — Zhipu AI / Z.ai's agentic flagship, hosted on Cerebras chip-inference. On τ-bench (multi-turn agentic tasks — booking, retail scenarios) it scores ≈ 87.4%, one of the best results among open-weight models at this size. Conversationally it's "engineering-polite": closes steps cleanly, acknowledges what it heard, and dispatches tool calls eagerly (parallel + single tool-calling out of the box). Must be used strictly in non-reasoning mode — thinking blocks balloon illogically on short turns and wreck latency. Russian is weaker than Qwen3 (more visible English-construction calques), but if the dialog is scripted it copes.
Sources: Cerebras GLM-4.7 announcement, Cerebras inference docs, τ-bench paper (arXiv 2406.12045).
🥉 Gemini 3.1 Flash Lite (Google AI Studio) — Google's managed model with a 1M-token context and multimodal support (text/image/audio/video). The selling point is predictability: fewer open-weight surprises, stable Russian grammar, even tone-of-voice. Tool-calling works through structured outputs (no dedicated BFCL listing). We use it as a managed fallback — when an SLO needs to hold without our own infra it delivers a smooth result, but vs Qwen3/GLM-4.7 it loses on fine persona-following and complex agentic behaviour.
Sources: Google model card, Google Cloud blog.
4. Nemotron Super 49B (DeepInfra) — dense 49B model (NAS-compressed from Llama-3.3-70B via NVIDIA's "Puzzle" algorithm), 128K context, post-trained for reasoning, tool-calling, and RAG. In conversation it sounds "academic-expansive": likes to verbalise its chain of thought, takes explicit reasoning steps, which contradicts the "one short reply" Voice Sales instruction. Good fit for agents where output quality matters more than speed (long-call analysis, end-of-call summarisation, complex tool-result filtering). Overkill for a short sales-manager turn.
Sources: NVIDIA Nemotron model card, NVIDIA build page.
Fallback LLM models
Below the primary LLM picker in agent settings you can add up to two fallback models. Each row carries its own model + version, and the list is ordered: the runtime walks it top-to-bottom and uses the first model that responds successfully.
When the chain kicks in. A fallback is tried only when the previous model fails — provider outage, rate-limit / quota error, network timeout, an invalid-API-key response. A successful answer (even a slow one) does not trigger a fallback; we hand the response back to the user as soon as the active model produces one.
Why order matters.
The primary model runs on every turn. Pick the one whose voice quality and tool-calling behaviour you actually want callers to hear.
Fallback #1 is for the most likely failure mode of your primary. If the primary is hosted on Cerebras, fallback #1 might be a DeepInfra Qwen3 — different inference provider, similar persona behaviour, so the conversation stays close in tone.
Fallback #2 is the "no matter what" net. A managed Google / OpenAI model is a good pick here — different vendor entirely, predictable Russian, less risk of a multi-provider outage taking the agent down.
We don't change personas or system prompts between attempts — the same conversation history is replayed against the next model. Pick fallbacks whose answer style is close enough to the primary that a caller won't notice the swap mid-turn.
UI behaviour.
The picker on each row shows only LLMs that aren't already selected on this agent (primary or any other fallback), so you can't accidentally duplicate the chain.
Drag the handle on the left of a row (☰) to change priority. The order in the UI is the order the runtime tries them.
A "Select this version" action inside the model tester drawer assigns the version directly into the row you clicked from.
The trash icon on the right removes a fallback row. Removing all rows is fine — the agent simply has no fallback and fails the turn if the primary fails.
Caveats.
Each fallback adds latency on the failure path (we wait for the primary to fail before attempting the next), so don't pile them on hoping they'll mask flaky behaviour — fix the primary instead.
Token usage and pricing are billed against whichever model actually responded, not the primary.
A fallback that's been retired by the provider stays in the row with an orange ⚠️ warning until you swap it out.

## Speech-to-Text (STT)
Configure how the agent transcribes user speech:
STT model and provider
Model-specific properties

## Voice Activity Detection (VAD)
Controls how the agent detects when the user is speaking:
VAD model selection
Sensitivity and timing parameters
Option to disable interruptions during the first message

## Voice (TTS)
Configure the agent's speaking voice per language:
TTS provider
Voice selection and voice-specific settings
Speed adjustment
Background sound type and volume

## Dynamic Variables
Agents support dynamic variables in system prompts and first messages. Variables are defined using OpenAPI schema and substituted at dispatch time.
Example system prompt:
You are a customer support agent for {{company_name}}.
The customer's name is {{customer_name}} and their order ID is {{order_id}}.
Variables can be passed via:
API dispatch call
URL parameters (for widget)
Campaign item data (for outbound calls)
Each variable has:
Name
Type (string, number, boolean, integer)
Description
Default/fallback value
Nullable flag

## Agent Tools
Agents can call external APIs during a conversation. See Tools & Integrations for details.

## Publishing
Agents can be published to make them accessible:
Published agent — accessible via public URL for testing
Widget — embeddable on any website
Phone number — linked to inbound/outbound telephony
API — dispatched programmatically

## Agent Duplication
Any agent can be duplicated to create a copy with all settings preserved. Useful for creating variations or templates.

<!-- source: https://docs.speaknode.com/en/guide/agents -->
## Creating and Configuring Agents
Step-by-step guide to creating and configuring voice AI agents in Speaknode
An agent is the core building block of Speaknode. It defines the personality, behavior, voice, and capabilities of your voice AI assistant.

## Creating a New Agent
Navigate to Agents in the sidebar.
Click + Create Agent.
Enter a name for your agent (e.g., "Customer Support", "Appointment Scheduler").
Click Create.
You will be taken to the agent configuration page.

## Selecting Agent Mode
Before configuring anything else, choose how the agent handles the voice pipeline. The mode determines which sections of the configuration will be visible and how the agent processes speech during a conversation.
Open the Agent Mode switcher at the top of the agent configuration page. Two modes are available:

## Classic
Traditional pipeline: STT → LLM → TTS. Speech is transcribed, the LLM generates a text reply, then a TTS voice speaks it back.
You configure LLM, STT, VAD, and TTS voice per language separately.
Mix and match providers (e.g., Deepgram STT + GPT-4o + ElevenLabs TTS).
More flexibility, more moving parts.
Default mode for newly created agents.

## Realtime (voice-to-voice)
A single audio-native model handles listening, reasoning, and speaking within one WebSocket session — no separate STT/LLM/TTS stages.
You pick one Realtime model and one voice per language — that's it.
STT, VAD, and TTS sections are hidden — the model does all three internally.
Fewer components, lower latency, more natural intonation.
Fallback chain is temporarily hidden for Realtime models (fallback semantics for voice-to-voice are still being finalized).
Available Realtime providers:
| Provider | Models | Notes
| OpenAI | gpt-realtime, gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview | Includes exclusive voices marin and cedar available only through the Realtime API
| Google AI Studio | gemini-2.5-native-audio-dialog | Supports affective dialog for more emotional expression
When to choose Realtime
Pick Realtime when latency and natural conversation flow matter more than fine-grained control over each pipeline stage. Pick Classic when you need to mix best-of-breed providers (e.g., a specialised STT for a specific language) or when you want fallback across LLMs.
Switching modes
Switching an agent from Classic to Realtime (or back) resets the pipeline-specific configuration for the sections that change visibility. Publish a fresh version after the switch.

## Configuring the System Prompt
The system prompt defines your agent's personality, goals, and behavior rules. This is the most important configuration for your agent.
In the System Prompt field, write instructions for your agent.
Use markdown headings to structure your prompt (e.g., # Personality, # Goal, # Guardrails).
Keep it concise
Voice agents work best with focused prompts under 2000 tokens. See the Prompting Guide for detailed advice.
Dynamic variables
You can use {{variable_name}} syntax in your system prompt. These variables are resolved at runtime. See Dynamic Variables for details.

## Selecting the LLM Model
The LLM model powers the reasoning and response generation of your agent.
Open the LLM section.
Select a model from the dropdown (e.g., GPT-4o, GPT-4o Mini, Claude Sonnet).
Adjust the Temperature slider:
Lower values (0.0 - 0.3): More deterministic, consistent responses. Good for data collection and structured tasks.
Medium values (0.3 - 0.7): Balanced creativity and consistency. Good for customer support.
Higher values (0.7 - 1.0): More creative, varied responses. Good for casual conversation.
Model selection
Refer to Best Practices for a comparison table of models and their recommended use cases.

## Adding Languages and First Messages
Each agent can support multiple languages. For each language, you configure a greeting message and a TTS voice.
Open the Languages section.
Click + Add Language.
Select a language from the dropdown (e.g., English, Spanish, German).
Enter the First Message -- this is what the agent says when a conversation starts.
Repeat for each language you want to support.
The first language in the list is used as the default. You can reorder languages by dragging them.

## Configuring TTS Voice per Language
For each language, you select a text-to-speech voice and configure its settings.
Click on a language entry to expand its settings.
Select a Voice from the available voices for that language.
Adjust Speed (0.5x - 2.0x). A speed of 0.9x - 1.1x is recommended for natural conversation.
Optionally select a Background Sound (e.g., office ambience, call center) to make the conversation feel more natural.
Preview voices before selecting them. Different voices suit different agent personalities -- a warm voice for customer support, a professional voice for scheduling.

## Configuring the STT Model
The Speech-to-Text (STT) model determines how your agent transcribes the caller's speech.
Open the STT section.
Select an STT model from the dropdown.
Configure language detection settings if your agent supports multiple languages.

## Configuring Voice Activity Detection (VAD)
VAD controls how the agent detects when the caller starts and stops speaking.
Open the VAD section.
Adjust the settings:
Turn Timeout: How long to wait after the caller stops speaking before the agent responds. Use 5-10 seconds for support, 10-15 seconds for data collection.
Silence Threshold: The silence duration that signals the end of a turn.
Setting the turn timeout too low can cause the agent to interrupt the caller. Setting it too high can make the agent feel unresponsive.

## Adding Tools
Tools let your agent perform actions during a conversation, such as looking up data or booking appointments.
Open the Tools section.
Click + Add Tool to attach an existing tool, or create a new one.
Toggle System Tools on or off as needed (e.g., end call, transfer).
Configure Transfer Rules if you want the agent to transfer calls to another agent under certain conditions.
See Tools & Webhook Tools for a full guide on creating and configuring tools.

## Publishing the Agent
Once your agent is fully configured, you need to publish it to make it available for phone calls, the web widget, and the API.
Review all your configuration sections.
Click the Publish button in the top-right corner.
The agent is now live and can receive calls or be embedded on your website.
Unpublished changes are saved as a draft. Callers and widget users will continue to interact with the last published version until you publish again.
After publishing, you can access the agent's test page, embed code, and public test URL. See Testing Your Agent and Embedding the Widget.

## Summary
| Step | Section | Description | Realtime mode
| 1 | Agent Mode | Choose Classic (STT→LLM→TTS pipeline) or Realtime (voice-to-voice) | —
| 2 | System Prompt | Define personality, goals, and rules | ✅
| 3 | LLM / Realtime model | Select the model that powers the agent | ✅
| 4 | Languages | Add languages with first messages | ✅
| 5 | TTS voice | Configure voice, speed, and background sound per language | ✅ (voice only)
| 6 | STT | Select speech-to-text model | ❌ hidden in Realtime
| 7 | VAD | Configure turn detection settings | ❌ hidden in Realtime
| 8 | Tools | Attach tools and transfer rules | ✅
| 9 | Publish | Make the agent live | ✅

<!-- source: https://docs.speaknode.com/en/guide/variables -->
## Dynamic Variables
Personalize conversations with runtime data using dynamic variables in Speaknode
Dynamic variables let you personalize each conversation with runtime data. Use them to inject caller names, order IDs, account details, or any other information into your agent's system prompt, first messages, and tool configurations.

## Syntax
Variables use double curly braces:
{{variable_name}}
For example:
Hello {{customer_name}}, how can I help you with order {{order_id}} today?

## Where to Use Variables
Variables can be used in the following places:
| Location | Example
| System Prompt | You are assisting {{customer_name}} who is a {{customer_tier}} customer.
| First Messages | Hello {{customer_name}}, welcome to our support line.
| Tool URLs | https://api.example.com/orders/{{order_id}}
| Tool Request Bodies | { "customer_id": "{{customer_id}}" }

## How Variables Are Defined
Variables are auto-detected from your system prompt. When you type {{variable_name}} in the system prompt, Speaknode automatically recognizes it and adds it to the agent's variable list.
You can also manually manage variables in the Variables section of the agent configuration.

## Variable Properties
Each variable has the following properties:
| Property | Description
| Name | The variable name as used in {{name}} syntax.
| Type | The data type: string, number, boolean, or integer.
| Description | A human-readable explanation of what this variable represents.
| Default Value | The value used if the variable is not provided at runtime.
| Nullable | Whether the variable can be null (omitted).
Always set a sensible default value or mark variables as nullable. If a required variable is missing at runtime and has no default, the raw {{variable_name}} text may appear in the agent's speech.

## Passing Variables at Runtime
There are three ways to supply variable values when starting a conversation:

## 1. API Dispatch
When starting a conversation via the API, include variables in the request body:
curl -X POST https://api.speaknode.com/api/v1/conversations/dispatch \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
"agentId": "your-agent-id",
"phoneNumber": "+1234567890",
"variables": {
"customer_name": "Alice",
"order_id": "ORD-12345"
}
}'

## 2. URL Parameters (Widget)
When using the embedded widget, pass variables as URL query parameters:
https://your-site.com/support?customer_name=Alice&order_id=ORD-12345
The widget reads these parameters and passes them to the agent session.

## 3. Campaign Items
When running an outbound campaign, variables are mapped from Excel columns. Each row in the contact list provides variable values for that specific call.
Variable names are case-sensitive. {{customer_name}} and {{Customer_Name}} are treated as different variables.

## Example: Personalized Support Agent
System Prompt:
# Personality
You are a friendly customer support agent for Acme Corp.
# Context
You are speaking with {{customer_name}}, a {{customer_tier}} tier customer.
Their account ID is {{account_id}}.
# Goal
Help the customer with their inquiry. If they ask about an order,
use the check_order tool with their account ID.
# Guardrails
- Never share information about other customers.
- If you cannot help, offer to transfer to a human agent.
First Message:
Hello {{customer_name}}, thank you for calling Acme Corp. How can I assist you today?
When a call comes in with customer_name=Alice, customer_tier=Gold, and account_id=AC-789, the agent will greet Alice by name and have full context about her account.
