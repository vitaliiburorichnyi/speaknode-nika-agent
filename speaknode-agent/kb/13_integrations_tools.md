# Integrations tools

<!-- source: https://docs.speaknode.com/en/features/tools -->
## Tools & Integrations
External API integrations and webhook tools for Speaknode agents
Speaknode agents can call external APIs during conversations, enabling them to look up data, perform actions, and integrate with your systems.

## Overview
Tools are HTTP-based integrations that the LLM can invoke during a conversation. When the agent decides it needs external data or needs to perform an action, it calls the configured tool and uses the result in its response.

## Tool Types
## Webhook Tools
Custom HTTP endpoints that the agent can call:
Method — GET, POST, PUT, DELETE
URL — endpoint address (supports variable substitution)
Headers — custom headers defined via OpenAPI schema
Body — request body defined via OpenAPI schema
Description — explains to the LLM when and how to use the tool

## System Tools
Built-in tools provided by the platform -- nothing to create, just enable them on an agent:
| Tool | Function
| End call | The agent ends the conversation itself once the goal is met
| Transfer to a human operator | The call is transferred to a live operator's phone over SIP: cold transfer, a fixed briefing message, or an auto-generated summary of the conversation
| Transfer to another agent | The dialogue is handed to another AI agent within the same session
| Detect language | The conversation switches to the caller's language, among those configured on the agent
| Skip turn | The agent stays silent and waits when the caller asks for a moment
| Ask for clarification | Records what information the agent was missing to complete the task
Configuration is described in System Tools in the user guide.

## Tool Configuration
Each tool is defined with an OpenAPI schema for its parameters:
Body schema — defines the JSON body structure the LLM should construct
Header schema — defines custom headers to send
Code — unique identifier used by the LLM to reference the tool

## Speech During Tool Execution
Tools support configurable speech while executing:
Pre-tool speech — what the agent says before calling the tool (e.g., "Let me look that up...")
Progress speech — what the agent says while waiting for the response

## Transfer Rules
The transfer tools carry rules that redirect the conversation:
Transfer to another agent — hand off to a different AI agent inside the same session
Transfer to a human operator — an outbound call to the operator's number, with a configurable ringing timeout and briefing mode
Condition — when the transfer should happen; the model picks the rule by it
This enables multi-agent workflows where specialized agents handle specific topics, and anything beyond automation reaches a live operator.

## How It Works
The LLM decides to call a tool based on the conversation context
The Python worker constructs the HTTP request from the OpenAPI schema
The request is sent to the configured endpoint
The response is passed back to the LLM
The LLM incorporates the result into its response

## Webhook Management
The platform also provides a separate webhook system for receiving events:
Configure webhook endpoints to receive session events
View webhook request history and payloads
Manage allowed paths and routing via the Webhook Receiver Client

## Examples
CRM Lookup:
Tool: get_customer_info
Method: GET
URL: https://crm.example.com/api/customers/{{customer_id}}
Description: Look up customer information by their ID
Order Status:
Tool: check_order_status
Method: POST
URL: https://api.example.com/orders/status
Body: { "order_id": "string" }
Description: Check the current status of a customer order

<!-- source: https://docs.speaknode.com/en/guide/tools -->
## Tools & Webhook Tools
Guide to creating and configuring tools for voice AI agents in Speaknode
Tools extend your agent's capabilities beyond conversation. With tools, your agent can look up information, submit forms, book appointments, or perform any action accessible via an HTTP API.

## Types of Tools
Speaknode supports three types of tools:
| Type | Description
| Webhook Tools | Custom HTTP endpoints that your agent can call during a conversation.
| System Tools | Built-in tools provided by the platform -- end call, transfer to an operator or to another agent, detect language, skip turn, ask for clarification. See System Tools.
| Transfer Rules | Conditions configured inside the two transfer system tools that decide where the conversation goes.

## Creating a Webhook Tool
Navigate to Tools in the sidebar.
Click + Create Tool.
Fill in the tool configuration:

## Basic Settings
Name: A short, descriptive name (e.g., check_order_status). The LLM uses this name to decide when to call the tool.
Description: Explain what the tool does and when to use it. This is included in the LLM context, so be precise.
Write the description from the agent's perspective. For example: "Use this tool to check the status of a customer's order when they provide an order ID."

## HTTP Configuration
Method: Select the HTTP method (GET, POST, PUT, PATCH, DELETE).
URL: The endpoint URL. You can use dynamic variables here (e.g., https://api.example.com/orders/{{order_id}}).

## Headers
Define request headers using an OpenAPI schema format. Click + Add Header and specify:
Name: The header name (e.g., Authorization).
Schema: The OpenAPI property definition for the header value.
Do not hardcode secrets directly in header values. Use environment-level configuration or a proxy for sensitive credentials.

## Body
For methods that accept a request body (POST, PUT, PATCH), define the body schema using OpenAPI schema format.
The schema describes the JSON structure that the agent will send. Each property should have:
Name: The field name.
Type: The data type (string, number, boolean, integer, object, array).
Description: What this field represents. The LLM uses this to fill in values from the conversation.
Required: Whether this field must be present.

## Attaching Tools to an Agent
Open the agent you want to configure.
Go to the Tools section.
Click + Add Tool.
Select the tool from the list of available tools in your workspace.
Click Save.
The agent can now use this tool during conversations.

## System Tools
System tools are built-in tools that come with Speaknode. You do not need to create them -- just enable or disable them on your agent.
In the agent's Tools section, find the System Tools area.
Toggle each system tool on or off.
Optionally, customize the Description of each system tool to change how the LLM understands when to use it.
For a tool that needs more than a description -- the two transfer tools -- click the gear icon next to its switch to open its settings.
The catalogue:
| Tool | What it does
| End call | The agent hangs up when the conversation is over.
| Transfer to a human operator | The agent calls a live operator's phone number and hands the call over.
| Transfer to another agent | The agent hands the dialogue to another AI agent.
| Detect language | The agent switches the conversation to the caller's language.
| Skip turn | The agent stays silent when the caller asks for a moment.
| Ask for clarification | The agent logs what information it was missing.
See System Tools for what each one is for, how to configure it, and how transfers to an operator behave on a live call.

## Transfer Rules
Transfer rules live inside the two transfer system tools -- open Transfer to another agent or Transfer to a human operator on the agent and add rules there.
A rule pairs a condition in plain language ("Transfer when the caller asks about billing issues") with a destination: another agent, or an operator's phone number. The model reads the conditions to decide whether to transfer and, when there are several rules, which one applies.
Transferring to another agent keeps the same session and the same recording -- the target agent's own prompt, voice and language take over, and its greeting plays only if Enable First Message is on. Transferring to an operator places a real outbound phone call; see System Tools for the modes, timeouts and failure behaviour.

## Pre-Tool Speech and Progress Speech
You can configure what the agent says before and during tool execution to keep the conversation natural.

## Pre-Tool Speech
A phrase the agent speaks before calling the tool. Use this to set expectations.
Example: "Let me look that up for you."

## Progress Speech
A phrase the agent speaks while the tool is running, if the tool takes more than a few seconds. This prevents awkward silence.
Example: "I'm still checking on that, one moment please."
Always configure pre-tool speech for tools that take more than a second to respond. Silence during a voice call feels longer than it actually is.

## Summary
| Tool Type | Created By | Configured On
| Webhook Tool | You, in the Tools page | Attached to agents in the Tools section
| System Tool | Platform (built-in) | Enabled/disabled per agent
| Transfer Rule | You, inside a transfer system tool | Per agent, per tool

<!-- source: https://docs.speaknode.com/en/guide/system-tools -->
## System Tools
Built-in agent tools in Speaknode: end call, transfer to a human operator, transfer to another agent, detect language, skip turn, request info
System tools are capabilities that ship with Speaknode. Unlike webhook tools, you do not create them — they already exist in every workspace. You enable the ones an agent needs, and optionally tune how they behave.
Technically they are ordinary LLM tools: the model sees their name and description, and calls them when the conversation matches. The difference is that the platform executes them internally — hanging up, dialling an operator, switching the agent, changing the language — instead of sending an HTTP request somewhere.

## Where to configure them
## Open the agent
Go to Agents in https://app.speaknode.com, open the agent and scroll to the Tools section.

## Enable the tool
System Tools lists every built-in tool. Flip the switch to give the tool to the agent.

## Configure it
Once a tool is enabled, a gear icon appears next to the switch. It opens the tool's settings for this agent: the description, interruption behaviour and — for the two transfer tools — the transfer rules.
Settings are stored per agent. Enabling Transfer to a human operator on one agent and pointing it at a support number does not affect any other agent.

## Settings every system tool has
| Field | What it does
| Name | Read-only. The tool's name in the catalogue.
| Description (optional) | The text the LLM reads to decide when to call the tool. Leave it blank to use the platform's default prompt, which is already tuned. Show Default fills the field with that default so you can edit it instead of writing from scratch.
| Disable interruptions | While the tool is running, the caller cannot interrupt the agent. Useful when the tool speaks a phrase that must be heard in full.
Careful with custom descriptions
The default descriptions are the result of a lot of tuning — a rewritten description is the most common reason a tool stops firing (or starts firing when it should not). If you do override it, keep the runtime placeholders: [languages will be populated at runtime] for Detect language, and the instruction to pass exactly one rule id for the transfer tools. The platform appends the actual list of languages / transfer rules to the description at call time.

## The catalogue
| Tool | What it gives the agent | Needs configuration
| End call | Hang up when the conversation is over | No
| Transfer to a human operator | Put the caller through to a live person over the phone | Yes — transfer rules
| Transfer to another agent | Hand the dialogue to another AI agent | Yes — transfer rules
| Detect language | Switch the conversation to the caller's language | No (uses the agent's languages)
| Skip turn | Stay silent when the caller asks for a moment | No
| Ask for clarification | Log what information the agent was missing | No

## End call
Why you need it. Without this tool the agent can never hang up on its own: the call only ends when the caller does, or when the session times out. That costs money on every call and leaves the caller listening to an agent that has nothing left to say.
How to use it. Enable the switch — there is nothing else to configure. The agent will call it when the dialogue is genuinely finished: the goal is reached, the caller says goodbye, or the caller explicitly asks to end the call.
The agent generates its own farewell (there is no fixed "goodbye" phrase to configure), waits for it to finish playing, and only then terminates the session. The recording and the transcript are finalised normally.
If the agent hangs up too eagerly, tighten the description rather than turning the tool off — e.g. add "Never end the call while the customer's question is unanswered".

## Transfer to a human operator
Why you need it. Some calls should not be handled by a bot: the caller insists on a human, the request is outside what the agent can resolve, or the deal is large enough that a person should close it. This tool dials a live operator's phone number and hands the call over — the caller stays on the same call the whole time.
Phone calls only
This tool works only when the conversation is happening over the phone. In a web-widget session the platform does not even give the tool to the model, so the agent cannot promise a transfer it is unable to perform. Connect a number under Phone Numbers first — see Phone Numbers and Custom SIP.
The operator is dialled from the same phone number and telephony account the caller reached the agent on. It is a second outbound leg, billed by your telephony provider like any other outbound call.

## Setting up a transfer rule
## Enable the tool and open its settings
In the agent's Tools section, enable Transfer to a human operator and click the gear icon.

## Add a rule
In Transfer Rules, click Add Rule and fill it in:
| Field | Required | What to put there
| Transfer mode | Yes | Cold, Warm — custom message or Warm — auto summary. See below.
| Phone number | Yes | The operator's number in international format, e.g. +15551234567.
| Condition | Yes | Plain-language description of when this rule applies, e.g. "The caller explicitly asks to speak with a human, or the request is outside the agent's scope". The model reads it to decide whether to transfer and, with several rules, which one to use.
| Transfer message (to caller) | No | What the caller should be told just before the handover. See the note below.
| Operator briefing (to operator) | For Warm — custom message | What is spoken to the operator when they pick up. Ignored by the other two modes.
| Ringing timeout (seconds) | No | How long the operator's phone rings before we give up. A new rule starts at 60; the allowed range is 5–120; left empty it falls back to 30.

## Add more rules if you route by topic
One rule per destination. For example: billing questions → the finance line, technical failures → the support line, everything else → the front desk. Write the conditions so they do not overlap — the model picks by condition alone.

## Save the agent
Click Save Changes in the drawer, then save the agent.
What the caller actually hears before the handover
The agent announces the transfer in its own words, generated from the conversation — the default tool description explicitly tells it to warn the caller and keep them company while the operator is being dialled. Transfer message is not played verbatim on an operator transfer today; treat it as documentation of the intended phrasing, and put the wording you want into the agent's prompt or the tool description instead. (On transfer to another agent, by contrast, the transfer message is spoken verbatim.)
Do not mix Warm — auto summary with the other modes in one agent
Warm — auto summary requires the model to produce a summary; the other two modes do not. If one agent has rules of both kinds under this tool, the platform cannot build a single consistent tool and drops it entirely — the agent will silently have no way to transfer. Use Warm — auto summary for every rule, or for none of them.

## Transfer modes
| Mode | What the operator hears once the answering-machine check clears | Use it when
| Cold (no briefing) | Nothing — they are connected straight to the caller. | The operator has the context elsewhere (a CRM screen pop), or speed matters more than context.
| Warm — custom message | The fixed text from Operator briefing. | The context is always the same: "Incoming transfer from the website line, the customer wants to discuss a refund."
| Warm — auto summary | A short recap of the conversation, generated by the model for this specific call. | Conversations differ every time and the operator should not have to ask the caller to repeat themselves.
In all three modes the operator first hears music for a few seconds after picking up, while the platform makes sure a live person answered rather than an answering machine (see When the operator does not answer). They cannot hear the caller yet, and the caller cannot hear them.

## What happens during the transfer
While the operator's phone is ringing the caller hears hold music and cannot hear the agent. The operator, in turn, does not hear the caller until the answering-machine check has cleared and the briefing has been played — so the caller never overhears what is said about them, and a voicemail greeting never gets to record a live customer.
Once the operator is connected, the agent leaves the call silently — there is no farewell phrase. The caller and the operator keep talking on the same call; the platform stops taking part in it.
The operator's leg is recorded as a separate audio stem, so a transferred call can still be reviewed end to end under Conversations.

## When the operator does not answer
The transfer is treated as failed when the operator does not pick up within the ringing timeout, the line is busy or rejects the call, the provider cannot place the call at all, or the call is answered by voicemail (the platform detects answering machines and refuses to hand a live customer to a recording).
In every one of those cases the call is not lost: the hold music stops, the agent comes back, apologises in one sentence, says the request will be picked up later, and carries on with the conversation. The caller is never dropped.

## Tips
Write conditions from the caller's perspective. "The caller asks for a manager or says they want to talk to a person" beats "escalation".
Match the ringing timeout to the team. A call centre that answers in five seconds does not need 60 seconds of hold music; a single person on a mobile might.
Keep the operator briefing short. The caller is on hold while it plays.
Test it end to end before publishing — with a real inbound call, not from the web widget, since the tool is not available there. See Testing.

## Troubleshooting
| Symptom | Likely cause
| The agent never offers a transfer | The tool is disabled, has no rules at all, or the session is a widget session rather than a phone call.
| The agent talks about transferring but nothing happens | The rules mix Warm — auto summary with the other modes, so the tool was dropped.
| The transfer always fails immediately | The number is unreachable from your telephony account, or the inbound number has no telephony account bound to it.
| The operator picks up and hears music for a few seconds | Expected — the answering-machine check is running; the caller is connected right after it (in Cold mode with no briefing at all).
| Saving the agent fails with a validation error | Warm — custom message without an operator briefing, a rule without a phone number, or a ringing timeout outside 5–120 seconds.

## Transfer to another agent
Why you need it. One prompt that covers sales, support and billing is worse at all three than three focused agents. This tool lets a front-line agent route the dialogue to a specialised one — including its own voice, language, prompt and tools — without dropping the conversation.
How to use it. Enable the tool, open its settings and add a rule per destination agent:
| Field | Required | What to put there
| Agent | Yes | The agent to hand the conversation to.
| Condition | Yes | When this rule applies, e.g. "The caller asks about an invoice or a payment".
| Delay before transfer (milliseconds) | No | A pause before the switch. Useful to let a transfer message land before the new agent starts.
| Transfer Message | No | Spoken by the current agent right before the switch, e.g. "I will transfer you to a specialist." It is played in full and cannot be interrupted.
| Enable First Message | No | What the target agent says first. See How the handover runs below.
The transfer happens inside the same session: the same conversation record, the same recording, no second call. It works on phone calls and in the web widget alike.

## How the handover runs
When the rule fires:
The current agent stops speaking (any inline TTS is interrupted).
The optional Transfer Message is played in full.
Delay before transfer waits, if set.
The target agent replaces the current one. It inherits the full prior chat history — everything the caller already told the previous agent is visible to the new one.
What the target agent says first depends on Enable First Message:
| Enable First Message | Target has a first message | What the caller hears
| ON | yes | The target's own first message is played (e.g., "Hi, I'm the sales specialist").
| ON | no / empty | The target continues the conversation from the last user message — no greeting.
| OFF | (either) | The target continues the conversation from the last user message — no greeting.
"Continue the conversation" means the target's LLM sees the full history and responds directly to the caller's last message, as if it had been listening the whole time. It will not reintroduce itself or ask a generic "How can I help you?".
Turn Enable First Message off for a seamless handover — the second agent picks up the thread instead of starting with a greeting ritual. Turn it on only when the target must explicitly announce itself (e.g., a legal disclosure that a different specialist is now on the line).
Transfer to an agent or to an operator?
Transfer to another agent keeps the caller with the AI and costs nothing extra. Transfer to a human operator places a real outbound call and takes a person's time. Route by topic with the first; escalate out of automation with the second.

## Detect language
Why you need it. A caller who starts speaking a language the agent did not expect otherwise gets answered in the wrong one for the rest of the call. This tool lets the agent notice and switch — voice, prompt and greeting — mid-conversation.
How to use it. Enable it on an agent that has more than one language configured (see Agents). No further setup: the platform passes the agent's language list into the tool at call time, and the agent may switch to those languages only. If the caller asks for a language that is not configured, the agent says so instead of switching.
The switch is triggered by an explicit request — "Can we speak in Spanish?", "Do you speak Portuguese?" — not by the caller merely mentioning a language.
If you override this tool's description, keep the [languages will be populated at runtime] placeholder: it is where the platform injects the agent's actual languages.

## Skip turn
Why you need it. When a caller says "hold on, let me find my order number", a voice agent normally treats the pause as its turn and starts talking over them. This tool gives the agent a way to deliberately say nothing.
How to use it. Enable it — no configuration. The agent stays silent and waits for the caller to speak again when they explicitly ask for a moment ("give me a second", "let me think", "hold on, let me check").
It does not fire on plain silence, and it does not fire on a direct question. It is worth enabling on any agent that asks callers for numbers, addresses or documents.

## Ask for clarification
Why you need it. It is a diagnostic tool: it records what the agent was missing to finish the job — an account number the caller never gave, context that was not in the prompt, an ambiguous instruction. Reviewing those records shows you what to add to the prompt, the variables or the webhook tools.
How to use it. Enable it and review the tool calls under Conversations.
Placeholder tool
This one is marked Placeholder in the tools list: it performs no action and changes nothing in the conversation — it only logs the request for analysis. The agent keeps talking to the caller as usual after calling it.

## Summary
| Tool | Effect on the call | Configuration
| End call | Ends the session after the agent's farewell | Description only
| Transfer to a human operator | Outbound call to a person, then the agent leaves | Transfer rules; phone sessions only
| Transfer to another agent | Another AI agent continues in the same session | Transfer rules
| Detect language | Voice, prompt and greeting switch language | Agent's languages
| Skip turn | The agent stays silent for one turn | Description only
| Ask for clarification | None — logged for analysis | Description only

<!-- source: https://docs.speaknode.com/en/guide/webhooks -->
## Webhooks
Receive real-time event notifications from Speaknode via webhooks
Webhooks let you receive real-time notifications when events occur in Speaknode. When an event triggers, the platform sends an HTTP POST request to your specified URL with the event payload.

## Creating a Webhook Subscription
Navigate to Webhooks in the sidebar.
Click + Create Webhook.
Fill in the configuration:
URL: The endpoint where Speaknode will send event payloads (e.g., https://your-server.com/webhooks/speaknode).
Description: A note describing the purpose of this webhook (e.g., "CRM sync for completed conversations").
Event Types: Select which events should trigger this webhook.
Enabled: Toggle the webhook on or off.
Click Save.

## Event Types
| Event | Description
| ConversationComplete | Fired when a conversation ends. Includes the full transcript and metadata.
| SessionStarted | Fired when a new voice session begins. Includes the agent ID and session metadata.
More event types may be added in future updates. Check your Speaknode dashboard for the latest list.

## Webhook Secret and Signature Verification
Each webhook subscription is assigned a Webhook Secret. Use this secret to verify that incoming requests genuinely originate from Speaknode.

## How Verification Works
Speaknode signs each webhook request using HMAC-SHA256:
The platform computes an HMAC-SHA256 hash of the request body using your webhook secret as the key.
The resulting signature is included in the request header.
Your server should compute the same hash and compare it to the header value.

## Verification Example
import hmac
import hashlib
def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
expected = hmac.new(
secret.encode("utf-8"),
payload,
hashlib.sha256
).hexdigest()
return hmac.compare_digest(expected, signature)
Always verify the webhook signature before processing the payload. This prevents spoofed requests from being accepted by your server.

## Viewing Request History
Speaknode logs every webhook delivery attempt so you can debug issues.
Open a webhook subscription from the Webhooks list.
Scroll down to the Request History section.
Each entry shows:
Timestamp: When the request was sent.
HTTP Status: The response status code from your server (e.g., 200, 500, timeout).
Payload: The JSON body that was sent.
Response: The response body returned by your server.
If your server returns a non-2xx status code, Speaknode may retry the delivery. Check the request history to see all attempts.

## Troubleshooting
| Issue | Solution
| Webhook not firing | Ensure the webhook is Enabled and the correct event types are selected.
| timeout in history | Your server must respond within a few seconds. Offload heavy processing to a background job.
| 4xx or 5xx errors | Check your server logs. Ensure the URL is correct and accessible from the internet.
| Signature mismatch | Ensure you are using the raw request body (not parsed JSON) and the correct webhook secret.

<!-- source: https://docs.speaknode.com/en/guide/mcp -->
## MCP
Connect Speaknode to Claude, ChatGPT, Cursor and other AI assistants
MCP (Model Context Protocol) lets an AI assistant work inside Speaknode on your behalf: read your calls, change an agent, build an analytics report. You connect it once, and from then on you ask the assistant in plain language instead of clicking through the interface.

## What the assistant can reach
| Area | Examples
| Agents | Read the setup, change the prompt, switch the model or voice
| Calls and sessions | Find a call, read the transcript, look at how it ended
| Analytics | Run an analysis, read the scores, assemble a report
| Tools | List the agent's tools, create one, run a test call against it
| Tests | Start a test run, read the results
| Reference data | Models, languages, staff and clients
The assistant sees exactly what you see. It works under your account, inside your space, with your permissions — it cannot reach a space you have no access to, and it cannot do anything the interface would not let you do.

## What you need
The server address: https://api.speaknode.com/mcp
Your Speaknode account
There is nothing else to copy. No API key, no client ID, no secret — the address is the whole configuration.

## How the connection works
You paste the address; the rest happens by itself:
The client asks the server who is allowed in and gets pointed at Speaknode.
A browser window opens with the usual login page.
You sign in and confirm access.
The client receives a token and starts working.
The token belongs to you personally. Your colleague connecting the same address logs in as themselves and sees their own data.

## Connecting
## Claude (web and desktop)
Open Settings → Connectors
Click Add custom connector
Paste https://api.speaknode.com/mcp as the server address
Confirm — a login window opens
Sign in with your Speaknode account
The connector appears in the list and stays available in every new chat.

## Claude Code
claude mcp add --transport http speaknode https://api.speaknode.com/mcp
Then run /mcp inside Claude Code and pick Authenticate. A browser opens, you sign in, and the tools become available in the session.

## Cursor
Add the server to ~/.cursor/mcp.json:
{
"mcpServers": {
"speaknode": {
"url": "https://api.speaknode.com/mcp"
}
}
}
Restart Cursor, open Settings → MCP, and click the sign-in prompt next to the server.

## ChatGPT
Open Settings → Connectors
Click Add and choose a custom connector
Paste the server address and confirm
Sign in with your Speaknode account
Custom connectors are only available on paid ChatGPT plans. On a free plan the section will not appear.

## Codex
Add the server to ~/.codex/config.toml:
[mcp_servers.speaknode]
url = "https://api.speaknode.com/mcp"
Restart Codex and confirm the sign-in when it asks.

## Access and safety
The assistant acts as you. Every call it makes is recorded under your account, so anything it changes looks — correctly — like your change.
It can change things, not only read them. Creating an agent, editing a prompt, starting a test run cost money the same way they do from the interface. Read what the assistant proposes before you confirm it.
Revoking access — remove the connector in the client. Signing out of Speaknode in your browser does not disconnect it: the client holds its own token.

## If something goes wrong
| What you see | What it means | What to do
| Login window does not open | The client did not reach the server | Check the address ends in /mcp and opens in a browser
| Invalid parameter: redirect_uri | This client's callback address is not allowed yet | Send the full error text to support — one line has to be added on our side
| Signed in, but no tools | The client connected before authentication finished | Reconnect the server in the client
| Tools present, calls fail | Your account has no access to that space | Check in the interface that you can see the same data
