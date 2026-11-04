# Prompts testing

<!-- source: https://docs.speaknode.com/en/guide/prompting -->
## Prompting Guide
How to write effective system prompts for voice AI agents in Speaknode
Writing effective system prompts for voice AI agents is different from prompting text-based chatbots. Voice conversations are real-time, sequential, and leave no room for the caller to "re-read" a response. This guide covers everything you need to write great prompts for Speaknode agents.

## Prompt Structure
Use markdown headings to organize your system prompt into clear sections. This helps the LLM follow your instructions consistently.
# Personality
You are a warm, professional customer support agent for Acme Corp.
You speak in a conversational, friendly tone.
# Goal
Help the caller resolve their issue in one call. If you cannot resolve it,
offer to transfer them to a human agent.
# Guardrails
- Never make up information. If you do not know, say so.
- Never share information about other customers.
- Do not discuss topics unrelated to Acme Corp products.
# Tone
- Conversational and warm, not robotic.
- Use short sentences.
- Avoid jargon unless the caller uses it first.
Keep your system prompt under 2000 tokens. Longer prompts increase latency and can dilute the model's focus on your most important instructions.

## Voice-Specific Prompting Rules
## Keep Responses Short
In a voice conversation, long responses sound like monologues. Callers lose track after about 3 sentences.
Less effective:
Provide comprehensive answers that cover all aspects of the topic.
Include relevant background information, step-by-step instructions,
and any caveats or exceptions the user should be aware of.
Recommended:
Keep responses under 2-3 sentences. If a topic needs a longer
explanation, break it into steps. After each step, pause and ask
if the caller is ready to continue.

## Use Natural Speech Patterns
Written text and spoken language are different. Prompt your agent to speak naturally.
Less effective:
Respond formally and use complete grammatical sentences at all times.
Recommended:
Speak naturally, as if you are a real person on the phone.
It is OK to use contractions (e.g., "I'll", "we're", "that's").
Use filler phrases sparingly to sound human (e.g., "Let me see...",
"Sure thing.").

## Confirm Understanding
Voice conversations cannot be scrolled back. Build confirmation into the flow.
Less effective:
Collect the customer's name, email, and order number.
Recommended:
Collect the customer's name, email, and order number one at a time.
After each piece of information, repeat it back to confirm.
For example: "Got it, your email is [email protected]. Is that correct?"
This step is important.

## Emphasis Techniques
LLMs can occasionally skip or de-prioritize instructions. Use these techniques to reinforce critical rules:

## Repetition
Repeat your most important rules at the end of the prompt.
# Guardrails
- Never make up information. If you do not know the answer, say "I'm not sure,
let me transfer you to someone who can help."
# Final Reminders
Remember: NEVER guess or make up information. Always acknowledge when you
do not know something. This is critically important.

## Emphasis Markers
Use phrases like "This step is important." or "Always do this." immediately after critical instructions.
After collecting the caller's email, repeat it back to confirm.
This step is important.

## Explicit Prohibitions
State what the agent must NOT do, not just what it should do.
Less effective:
Be helpful and answer questions about our products.
Recommended:
Answer questions about Acme Corp products only.
Do NOT discuss competitors, politics, or unrelated topics.
If asked about something outside your scope, say:
"I'm only able to help with Acme Corp product questions. Is there
anything else I can help you with?"

## Tool Error Handling
When a tool call fails (e.g., API timeout), the agent needs clear instructions on how to respond.
Less effective:
Use the check_order tool to look up orders.
Recommended:
Use the check_order tool to look up orders. If the tool returns an
error or times out:
1. Acknowledge the issue: "I'm having trouble looking that up right now."
2. Never guess or make up order details.
3. Offer an alternative: "Can I take your email and have someone
follow up with you?"
This step is important.

## Complete Example Prompts
## Customer Support Agent
# Personality
You are Alex, a friendly and professional support agent for CloudStore,
an online electronics retailer.
# Goal
Help the caller with their order, return, or product question.
Resolve the issue in one call whenever possible.
# Process
1. Greet the caller and ask how you can help.
2. Identify their issue. Ask for their order number if relevant.
3. Use the check_order tool to look up order details.
4. Provide a clear answer or next steps.
5. Ask if there is anything else you can help with.
6. End the call politely.
# Guardrails
- Keep responses under 2-3 sentences.
- Never make up order details. If the tool fails, acknowledge the issue
and offer to have someone follow up.
- Never discuss competitors or unrelated topics.
- If the caller is angry, stay calm and empathetic. Do not argue.
# Tone
- Warm and conversational.
- Use contractions naturally.
- Address the caller by name if they provide it.
# Final Reminders
NEVER guess order information. Always use the check_order tool.
Keep responses short. This is a phone call, not an email.

## Appointment Scheduler
# Personality
You are a polite and efficient scheduling assistant for Dr. Smith's
dental practice.
# Goal
Help the caller book, reschedule, or cancel a dental appointment.
# Process
1. Ask the caller what they need: book a new appointment, reschedule,
or cancel.
2. For new appointments:
a. Ask for their full name.
b. Ask for their preferred date and time.
c. Use the check_availability tool to see open slots.
d. Confirm the appointment details and use the book_appointment tool.
3. For rescheduling:
a. Ask for their name and current appointment date.
b. Use the find_appointment tool to locate it.
c. Ask for their new preferred date and time.
d. Use the reschedule_appointment tool.
4. For cancellations:
a. Ask for their name and appointment date.
b. Use the cancel_appointment tool.
c. Confirm the cancellation.
# Guardrails
- Repeat all details back to the caller before confirming. This step
is important.
- If no slots are available for the requested time, suggest the two
nearest alternatives.
- Do not provide medical advice of any kind.
# Tone
- Professional but friendly.
- Speak concisely. Each response should be 1-2 sentences.

## Data Collection Agent
# Personality
You are a polite and patient survey agent collecting feedback for
National Insurance Company.
# Goal
Collect the following information from the caller:
1. Full name
2. Policy number
3. Satisfaction rating (1-5)
4. One thing we could improve
# Process
- Ask for each piece of information one at a time.
- After each answer, repeat it back to confirm. This step is important.
- If the caller gives an invalid answer (e.g., rating of 7), politely
ask them to choose a number between 1 and 5.
- After collecting all information, use the submit_survey tool to
save the results.
- Thank the caller and end the call.
# Guardrails
- Do not skip any field. All four pieces of information are required.
- If the caller wants to skip a question, gently explain that all
fields are needed to process their feedback.
- Never discuss policy details or pricing. If asked, say: "I'm only
collecting feedback today, but I can transfer you to an agent who
can help with that."
- Keep responses to 1-2 sentences maximum.
# Tone
- Patient and encouraging.
- Thank the caller after each answer.

## Prompt Writing Checklist
Structured with markdown headings (# Personality, # Goal, # Guardrails, # Tone).
Under 2000 tokens.
Responses limited to 2-3 sentences per turn.
Natural speech patterns (contractions, conversational phrasing).
Critical rules repeated and emphasized ("This step is important.").
Explicit prohibitions (what the agent must NOT do).
Tool error handling instructions included.
Confirmation steps for collected data.
Silence and edge case handling.

<!-- source: https://docs.speaknode.com/en/guide/testing -->
## Testing Your Agent
How to test voice AI agents using the built-in testing interface in Speaknode
Speaknode provides a built-in testing interface so you can interact with your agent directly in the browser before deploying it to phone lines or your website.

## Opening the Test Page
There are two ways to access the test interface:

## From the Agent Editor
Open the agent you want to test.
Click the Test button in the top-right corner of the editor.
The test page opens in a new tab.
The test page uses the latest saved configuration, including unpublished draft changes. This lets you iterate on your agent without publishing each time.

## Public Test URL
For published agents, Speaknode provides a public test URL that anyone can use.
Open the agent and ensure it is published.
Copy the Public Test URL from the agent settings.
Share this URL with testers or stakeholders.
The public test URL uses the published version of the agent, not the draft. Make sure to publish your changes before sharing.

## Test Page Layout
The test page is divided into two panels:

## Transcript Panel
The left panel shows the conversation transcript in real-time:
Agent messages appear on one side, user messages on the other.
Each message is timestamped.
New messages appear automatically as the conversation progresses.

## Controls Panel
The right panel contains session controls:
Start / Stop Session button to begin or end the conversation.
Language Selector dropdown to choose which language to use for the session.
Microphone Controls to mute/unmute your microphone.

## Running a Test Session
## Step 1: Select a Language
If your agent supports multiple languages, choose the desired language from the Language dropdown before starting the session.

## Step 2: Start the Session
Click the Start Session button.
Grant microphone access when prompted by your browser.
The agent will speak its first message (the greeting configured for the selected language).

## Step 3: Have a Conversation
Speak naturally into your microphone.
Watch the transcript update in real-time as both you and the agent speak.
The agent responds based on its system prompt and configuration.

## Step 4: Stop the Session
Click the Stop Session button to end the conversation. The full transcript remains visible for review.
Testing tips
Test all the edge cases described in your system prompt.
Try interrupting the agent mid-sentence to verify interruption handling.
Test each language separately.
Verify that tools trigger correctly by speaking the expected phrases.
Test with background noise to check VAD sensitivity.

## Viewing the Transcript
After the session ends, the transcript is saved and can be reviewed:
Scroll through the entire conversation in the transcript panel.
Each turn shows the speaker and the transcribed text.
If the session was linked to a conversation record, you can find it in the Conversations page for deeper analysis.

## Troubleshooting
| Issue | Solution
| No audio from agent | Check your browser's audio output settings and volume.
| Microphone not detected | Ensure you granted microphone permission. Try a different browser.
| Agent not responding | Verify the agent has at least one language configured with a first message.
| Wrong language used | Select the correct language from the dropdown before starting the session.

<!-- source: https://docs.speaknode.com/en/guide/best-practices -->
## Best Practices
Practical recommendations for building effective voice AI agents on Speaknode
This page collects practical recommendations for building effective voice AI agents on Speaknode. These tips are drawn from production experience and apply to most voice agent use cases.

## Voice Settings
## Stability and Speed
The TTS voice stability and speed settings have a significant impact on how natural your agent sounds.
Speed: Keep between 0.9x and 1.1x for natural conversation. Going faster can sound rushed; going slower can feel sluggish.
Stability: A value between 0.5 and 0.75 provides a good balance of expressiveness and consistency. Lower stability sounds more emotive but less predictable.
Test your voice settings by running a few conversations and listening back. Small adjustments make a big difference in perceived quality.

## Background Sounds
Adding a subtle background sound (e.g., office ambience) can make the agent sound more realistic and reduce the "uncanny valley" effect of pure silence between turns.
Use background sounds sparingly -- they should be barely noticeable, not distracting.

## Conversation Design
## Turn Timeout
The turn timeout controls how long the agent waits after the caller stops speaking before it responds. The right value depends on your use case:
| Use Case | Recommended Timeout | Rationale
| Customer support | 5 - 10 seconds | Callers may pause to think or look up information.
| Data collection | 10 - 15 seconds | Callers need time to find account numbers, addresses, etc.
| Quick Q&A | 3 - 5 seconds | Fast-paced interactions benefit from shorter timeouts.

## Interruption Handling
In voice conversations, callers will sometimes speak while the agent is still talking. This is natural behavior. Configure your agent to handle interruptions gracefully:
Allow the agent to be interrupted during informational responses.
Use shorter sentences so the agent yields naturally.
In your system prompt, instruct the agent to acknowledge interruptions (e.g., "Sorry, go ahead.").

## Silence Handling
Extended silence can confuse callers. Add guidance in your system prompt:
Less effective:
Wait for the user to respond.
Recommended:
If the user is silent for more than 10 seconds, gently prompt them:
"Are you still there? Take your time."
If they remain silent after two prompts, say:
"It seems like you may have stepped away. I'll end the call for now.
Feel free to call back anytime."

## Model Selection
Choosing the right LLM model affects response quality, latency, and cost.
| Model Type | Latency | Best For | Trade-offs
| GPT-4o | Medium | General-purpose support, complex reasoning | Higher cost, slightly higher latency
| GPT-4o Mini | Low | High-volume, straightforward tasks | Less capable with nuanced reasoning
| Flash models | Very Low | Low-latency requirements, simple interactions | May struggle with multi-step reasoning
| Claude (Sonnet/Haiku) | Medium/Low | Complex reasoning, detailed instructions, long prompts | Availability depends on configuration
Start with a general-purpose model like GPT-4o during development. Once your agent is stable, test with faster models to see if quality remains acceptable at lower latency and cost.

## Prompt Engineering for Voice
Voice agents require different prompting strategies than text-based chatbots. See the dedicated Prompting Guide for full details. Key highlights:
Less effective:
You are a helpful assistant. Answer the user's questions thoroughly
and provide detailed explanations with examples.
Recommended:
You are a friendly phone support agent. Keep responses under 2-3
sentences. Speak naturally and conversationally. If a topic needs
a longer explanation, break it into steps and confirm understanding
after each step.

## Multi-Agent Patterns
For complex workflows, use multiple agents connected by transfer rules.

## Orchestrator + Specialists
A common pattern is to use one "front door" agent that routes callers to specialized agents:
Orchestrator Agent: Greets the caller, identifies their intent, and transfers to the right specialist.
Billing Agent: Handles billing inquiries, payment issues, and plan changes.
Technical Support Agent: Handles product questions, troubleshooting, and bug reports.
Scheduling Agent: Handles appointment booking and rescheduling.
Configure transfer rules on the orchestrator agent with clear conditions:
"Transfer to the billing agent when the caller mentions invoices, payments, charges, or subscription changes."
"Transfer to technical support when the caller describes a problem, error, or needs help using the product."
Keep each specialist agent's system prompt focused on its domain. This improves response quality compared to a single agent that tries to handle everything.

## Pre-Tool Speech
Always configure pre-tool speech for tools that involve network calls. Silence during a phone call feels much longer than it actually is.
Less effective:
Agent goes silent for 3 seconds while calling the API.
Recommended:
Agent says: "Let me check that for you, one moment."
API call happens while the caller waits with context.

## Testing Checklist
All configured languages work correctly with appropriate first messages.
The agent handles interruptions without breaking flow.
Tools trigger at the right moments and return expected results.
Transfer rules route to the correct agents.
The agent gracefully handles tool errors (e.g., API timeout).
Silence and edge cases are handled (caller goes quiet, background noise).
The agent stays within its guardrails (does not make up information, does not go off-topic).
