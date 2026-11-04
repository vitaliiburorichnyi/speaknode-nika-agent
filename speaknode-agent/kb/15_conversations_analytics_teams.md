# Conversations analytics teams

<!-- source: https://docs.speaknode.com/en/features/analytics -->
## Analytics
Conversation analytics, telemetry, and data storage in Speaknode
Speaknode captures detailed data about every conversation for analysis and monitoring.

## Conversation History
Every agent session is recorded with:
Session metadata — agent, caller, start/end time, duration, status
Audio recording — full session audio stored in object storage
Transcription — text transcript of the conversation
Telemetry spans — detailed OpenTelemetry traces of every step

## Session List
Browse all conversations with filters:
By agent
By status (completed, failed, active)
By date range
By caller information

## Session Detail
For each session you can view:
Full conversation transcript with turn-by-turn breakdown
Audio playback with waveform visualization
Timing metrics per turn (latency, duration)
Tool calls made during the session
Error details (if failed)

## Live sales analysis
The same machinery applies to recordings of human sales calls: an uploaded
recording becomes a dialogue with roles and is scored against a set of
characteristics — talk share, script compliance, objection handling, whether a
next step was agreed.
Upload — audio, audio with a ready transcript, or a transcript alone;
in batches or as a ZIP archive from your telephony provider
Transcription with diarization — an external service splits the recording
into utterances with roles and timecodes
Characteristics — computed metrics come from the backend, judged ones from
a language model, every score carrying a justification and a quote
Reports — aggregations by rep, by date, by company; saved views and a
team dashboard
Agent conversations and human recordings live in the same entity and are
measured by the same metrics — a bot and a live rep compare directly.
See Call Analytics for details.

## Telemetry & Tracing
The platform uses OpenTelemetry for end-to-end tracing:
User speaks → STT span → LLM span → Tool call span → TTS span → User hears
Each conversation is a trace containing spans for every operation:
Span name — operation type (STT, LLM inference, tool call, TTS)
Duration — how long each step took
Status — success or error
Attributes — tags and metadata
Events — detailed events within the span

## Telemetry Pipeline
Python Worker → OTEL Collector → Kafka → ASP.NET Consumer → Database
→ Langfuse (internal observability)

## Data Storage
| Data | Storage
| Session metadata | PostgreSQL
| Audio recordings | S3-compatible object storage
| Telemetry spans | PostgreSQL (via Kafka)
| Analytics aggregations | ClickHouse
| LLM traces | Langfuse

<!-- source: https://docs.speaknode.com/en/guide/conversations -->
## Viewing Conversations
Review call history, recordings, transcripts, and performance metrics in Speaknode
The Conversations page provides a complete history of all calls handled by your agents. You can listen to recordings, read transcripts, and analyze performance metrics for each conversation.

## Call History
Navigate to Conversations in the sidebar to see a list of all past conversations.

## Filtering
Use the filters at the top of the page to narrow down the list:
Date Range: Select a start and end date.
Status: Filter by call status (e.g., completed, failed, in progress).
Agent: Filter by the agent that handled the call.

## Conversation Detail
Click on any conversation to open its detail view. The detail page contains an audio player and two tabs: Transcript and Overview.

## Audio Player
The audio player is displayed at the top of the conversation detail page.
Waveform Visualization: Shows the audio waveform so you can visually scan the conversation.
Playback Speed: Adjust playback speed between 1x and 2x to review calls faster.
Skip Controls: Jump forward or backward through the recording.
Play / Pause: Standard playback controls.
Use 1.5x or 2x playback speed to review calls more quickly during quality assurance.

## Transcript Tab
The transcript tab shows the conversation turn by turn, with the agent and user messages displayed in sequence.
Each turn includes detailed performance metrics:
| Metric | Description
| Latency | End-to-end response time from user speech end to agent speech start.
| Confidence | STT confidence score for the user's transcribed speech.
| LLM TTFT | Time to First Token -- how quickly the LLM began generating a response.
| TTS TTFB | Time to First Byte -- how quickly the TTS engine began producing audio.
Click on any turn in the transcript to jump to that point in the audio player.

## Overview Tab
The overview tab shows metadata about the conversation:
Agent: The agent that handled the call.
Phone Number: The phone number used (if applicable).
Duration: Total call duration.
Start / End Time: When the conversation started and ended.
Status: Final status of the call.
Campaign: The campaign this call belongs to (if applicable).
Variables: Any dynamic variables passed to the agent for this call.

## Troubleshooting Conversations
Use the transcript metrics to diagnose issues:
| Symptom | Possible Cause | What to Check
| High latency | Slow LLM response | Check LLM TTFT. Consider using a faster model.
| Garbled transcription | STT accuracy | Check confidence scores. Consider a different STT model.
| Agent sounds slow | TTS processing | Check TTS TTFB. Consider a different voice or provider.
| Agent interrupts user | VAD too sensitive | Adjust turn timeout and silence threshold in agent settings.

<!-- source: https://docs.speaknode.com/en/guide/call-analytics -->
## Call Analytics
Uploading recordings, scoring conversations, and building reports in Speaknode
The analytics module treats recordings of live sales calls exactly the way Speaknode treats AI agent conversations: a recording becomes a dialogue with roles, the dialogue is scored against a set of characteristics, and the scores roll up into reports for the whole team.
Agent conversations and human recordings live in the same entity and are measured by the same metrics — you can compare a bot against a live rep directly, without stitching two reports together by hand.

## How it works
Upload → Transcription with diarization → Scoring against characteristics → Reports
| Step | What happens
| Upload | Audio goes straight to storage, bypassing the backend; a conversation appears in the system
| Transcription | An external service splits the recording into utterances with roles and timecodes
| Scoring | Computed metrics are calculated by the backend, judged ones by a language model
| Reports | Values are aggregated by rep, by date, by company
Bring your own transcript
If you already have the text, the transcription step is skipped. This is the only way to score recordings from a system that gives you the text but not the audio.

## Uploading recordings
Go to Analytics → Calls and press Upload recordings. Three combinations are supported:
audio only — the usual case, the service transcribes it for you;
audio and transcript — your own transcript, with the audio kept for playback and timecodes;
transcript only — no recording, scored from the text.
Audio and transcript are matched by file name without the extension: call-12.mp3 and call-12.json are one conversation.
The upload dialog asks for the staff member and the client — both from the directory of the space, and both can be created right there with the button next to the picker. The analyse right away checkbox queues the recordings immediately; without it they land in the list as "queued" and wait for a batch run.
The same dialog takes a name for the upload and a date of the recordings. The name is how you find your own import in the filter later; leave it empty and the upload names itself after the moment it happened: "Upload 21.09.2026 18:20, 3 files". The date applies only to files that carry none of their own — it never overrides what is known about the file itself.

## Transcript format
{
"language": "en",
"duration_ms": 356000,
"segments": [
{ "start_ms": 2000, "end_ms": 4100, "role": "Operator", "text": "Good afternoon, my name is…" },
{ "start_ms": 4300, "end_ms": 7200, "role": "Client", "text": "Yes, I'm listening." }
]
}
Roles are mandatory: without them there is no way to tell whose talk share to count and whose work to score. Timecodes are optional — the conversation will still be scored, but the time-based metrics (talk share, interruptions, speech rate) will not be computed and show up as a dash in the card rather than a zero.

## From an archive
A ZIP is convenient when the export comes from your telephony provider. Metadata is taken from the file name:
<id>_<in|out>_<phone>_<YYYY_MM_DD-HH_MM_SS>_<suffix>.mp3
For example 883140777409555_out_79251154445_2026_09_10-14_42_50_akww.mp3 is an outbound call to 79251154445 on 10 September 2026 at 14:42:50.
Dry run first
Archive import runs as a check by default: the system reports how many recordings it accepted, how many it considers duplicates, and what it rejected and why — without importing anything. Clear the checkbox once the result looks right.
Uploading the same file twice does not create a duplicate: recordings are matched by content. macOS service files — the __MACOSX folder, the shadow ._name twins and .DS_Store — are skipped: they are resource forks, not recordings, and they have no business becoming conversations.

## An upload as a unit
Every upload is remembered as a whole: its name, its kind (files or an archive), who made it and when, how many recordings were taken and how many were refused. Calls can then be filtered by it — "show me what I loaded on Tuesday" — and reports can use it as a filter or as a dimension, so two imports can be compared against each other. A dry run creates nothing, so it leaves no record of itself either.

## The date of a conversation
The date in the list and in reports is when the call happened, not when it was uploaded. It comes from the first source that knows it:
the date given at upload, or the started_at column of the archive manifest;
the file name, when it matches the telephony pattern above;
the timestamp the archive keeps for the file itself;
nothing of the above — then there is no date.
In that last case the list shows the moment of upload, marked as a date that is not known. Quietly substituting today would be the worst of all: a year of archive would turn into one busy afternoon, with nothing to tell the invention from the fact.
The moment of the upload itself lives separately and is always honest — it is when the file reached the system.

## Which one is the operator
Diarization tells voices apart, not people. It hears that two people spoke and labels them from indirect signs — and when it gets that wrong, it gets it wrong silently: the talk share of "the operator" is really the client's, the script stages are scored against the wrong person, and the card looks perfectly normal all the while.
So for every uploaded recording the analysis first asks the model a question of its own: are the two sides the other way round? The model answers yes or no and says in one sentence what made it decide — both are kept with the conversation. Agent calls skip this step: there it is known who spoke.
The recording is then measured twice — as diarization labelled it and with the sides swapped. The arithmetic for the second reading the platform works out itself: swapping the roles is looking at the same utterances from the other side. The judged characteristics, though, have to be asked again: "the operator did not handle the objection", said about a different person, is a different verdict, not the same one with the labels moved.
The conversation card has Swap the roles next to the transcript heading. Since both readings are measured in advance this is a switch, not a re-analysis: the transcript and every score change at once. Next to it you can see where the current reading came from — the model's reason, or a note that a human chose it.
A human decision is not overwritten
Once the roles have been swapped by hand, the next analysis does not argue: it recomputes the scores but keeps the side you chose. The model got it wrong once; there is no reason to let it do so twice.
Reports, the call list and the filter values always read the version the conversation is currently shown in. The other set lies beside it, waiting for the switch — averaging the two together would produce a number that measures nothing.
The utterances themselves are never rewritten: the transcript stays what diarization produced, and the roles are swapped on reading.

## What gets measured
The default set ships with every space and falls into two groups.

## Computed metrics
Calculated by the backend from the timecodes, with no model involved.
| Metric | Norm | Why
| Operator talk share | up to 43% | Selling is asking questions, not monologuing
| Client talk share | from 57% | The other side of the same norm
| Interruptions | — | How often the rep started talking over the customer
| Overlap share | — | How much of the call was simultaneous speech
| Operator speech rate | — | Words per minute
| Silence share | — | Pauses between utterances
| Conversation duration, min | — | From the start of the session to its end; for an upload, the length of the file

## Judged characteristics
Scored by a language model. Every score comes with a justification and a link to the utterance it follows from — in the conversation card that link is clickable and seeks the recording to that moment.
This covers the script stages (opening, qualification, discovery, presentation, objection handling, budget, decision makers, closing), sentiment, politeness, slang and profanity, call type, and whether a next step was agreed.
Script compliance is a weighted sum of the stages, normalised to 0–100. Overall score is the same arithmetic over everything that carries a weight, not the stages alone. The weights are visible and editable in the characteristics catalogue; while only the stages carry one, the two numbers agree.
"Not measured" is not zero
When a characteristic could not be computed, the card shows a dash and the reason. A zero talk share reads as "the rep never spoke" and drags the team averages down — so unmeasured values stay out of aggregates entirely.

## Your own characteristics
Go to Analytics → Characteristics. Folders on the left, metrics on the right.
Create a folder for your set — "Objections" or "Onboarding", say. The Default folder always exists and cannot be deleted.
Add a characteristic. The key is latin-only and is how reports find the metric; it cannot be changed after creation. Write the instruction for the model: what exactly to assess and by what signal. Ask for a justification and a quote — without them the score is unreadable.
Set the norm. It colours deviations in the card and in reports, and for a characteristic that takes part in the overall score it is also the measure of how well the norm was met.
Computed metrics cannot be created by hand: their value comes from code, and "add one of those" would mean writing a formula that does not exist. Nor can they be deleted — only disabled: the pipeline keeps computing them by key. Everything else about a built-in judged characteristic is editable, including the instruction for the model: it is just text going into the prompt, and wanting to sharpen the wording for your own product is a normal thing to want.
Deleting a characteristic removes it from the catalogue and from the report builder entirely. Values already computed stay with the conversations and are shown in the card marked as deleted: they were measured while the characteristic existed. Such a characteristic takes no part in reports, and a saved view simply loses the column.
What happens to history
Editing a metric does not rewrite values that were already computed: each one stores the version of the metric it was computed with. A report for last month will not change retroactively because you changed a weight. To apply the new rules to old calls, re-analyse the conversations.

## Norms, scale and weight
The characteristic dialog offers only what means something for the chosen kind of value:
| Value type | What is configured
| Score | scale maximum, norms, direction, weight
| Percentage | norms, direction, weight
| Number, Duration | norms, direction, weight; duration norms are given in milliseconds
| Yes / no | "good when yes" or "good when no", weight
| Category | none of the above
The scale maximum belongs to a score alone: it is both the ceiling the model may not answer above and the denominator of the overall score.
Weight is participation in the overall score, not a rank in a list. The overall score is a weighted share of fulfilment: the sum of (share × weight) divided by the sum of the weights. Each type produces its share differently: a score divides by its scale maximum; a yes/no gives one or zero, and the direction says which answer is the good one; a number, a duration and a percentage divide by their norm — "higher is better" divides by the lower bound, "lower is better" gives full marks inside the upper one and decays as it is exceeded. A number with no norm therefore gains nothing from a weight: there is nothing to divide by, and the characteristic simply stays out of the total.
Script compliance and Overall score are two different numbers: the first counts the script stages only, the second counts everything that carries a weight. While weights sit on the stages alone, the two agree.

## The language of the names
There are two languages here
The interface language is yours alone: it labels the characteristics, the folders and the report columns. The analysis language belongs to the space: it is what the model writes its justifications in. The first is switched in the header and changes the picture at once; the second lives in the analytics settings and applies to the next analysis.
Names and descriptions of the built-in characteristics, folders and views are stored in English, with translations kept as separate rows. The interface states the chosen language in an x-lang header — what the language switch says, not what the browser is set to — and gets the text back in it. For direct API calls Accept-Language serves as the fallback; a language with no translations falls back to English, which is more honest than a blank name.
Only the text the product ships is translated. Whatever you typed yourself — your own characteristic, folder or view — stays exactly as you wrote it: translating it would mean guessing what you meant in a language you did not write in.
Renaming a built-in characteristic drops its translations, and your wording is what everyone sees — otherwise the rename would show up in one language only.
The instruction for the model is not translated. It is a prompt, not interface text: two language versions of it would mean two different analyses of the same conversation.

## Reports and views
Go to Analytics → Views. The builder is on top, saved views on the left.
A report is four answers: for what period, broken down by what, which metrics, and how to show it (table, bars, line, pie, tiles).
There can be several dimensions, added as rows just like measures: a row of the report is then a combination of values — "rep × week × call type". The breakdowns are: staff member, date (by day, week or month), company, client, source, upload, call end reason, and the value of any characteristic. The same field cannot be added twice — except date and characteristic, where repeating makes sense: months over days, different characteristics side by side.
A numeric characteristic is split into ranges: the dimension gets "from–to" rows with an optional label. Without them every distinct value would become its own row — a list rather than a report. The bounds are half-open, so a value falls into exactly one range, and anything outside all of them is collected into a row of its own.
Besides characteristics, a measure can be the number of conversations — simply the count of rows in the group.

## Filters
A dimension answers "how to show it", a filter answers "what to take at all". Filters are added as rows in the same constructor and narrow the selection by the same fields the dimensions use: staff member, client, company, source, upload, call type (agent or uploaded recording), end reason, and any characteristic.
A performer here is both a person and a voice agent: conversations of either live in the same table and are measured by the same metrics, so the list is one but split into "Staff" and "Voice agents" groups. The same filter sits above the list of calls, where it likewise takes several performers at once.
The condition follows what is being filtered: fields and text characteristics take "is one of" and "is none of", choosing among the values that actually occur in the space; a numeric characteristic takes "at least", "greater than", "at most", "less than" and a number; any characteristic also takes "is measured" and "is not measured". The list of values comes from the conversations themselves rather than from the directory: on an uploaded recording the client and the company may stay as text from the import, and such a row would otherwise be impossible to filter on.
A half-filled filter row narrows nothing: a filter is assembled one control at a time, and "chose a field — the report went empty" would read as breakage. A filter on a deleted characteristic stops being applied together with it — the same way its column disappears.
Filters are saved with the view. The period is not: the same view is read both for a week and for a month, and switching the period does not change the saved report.

## Saving
A report you built can be saved as a view — for the whole space or just for yourself. Save writes the changes into the view you have open, Save as creates a new one. Built-in views are edited only through a copy: they are the same for everyone, and an edit "for my team" would break them for everybody else — so their Save button is disabled.
The star next to a view puts it on the dashboard. Pinning is personal: everyone has their own dashboard, while the set of views is shared.

## Dashboard
Analytics → Dashboard shows pinned views as tiles. Each loads independently: a dashboard of six reports does not wait for the slowest one to show anything at all.
Four views ship built in: "Team overview" (the key numbers), "Rep comparison" (a row per rep), "Calls" (the log) and "Weekly trend".
The Edit button turns on edit mode: tiles can be dragged around, each gets a remove cross, and Save stores the order. Outside that mode the dashboard is read-only — a stray click cannot drop a tile.

## Batch analysis
When there are many recordings, analysis runs in batches: go to Analytics → Calls, select the conversations and create a run. A run reports how many are done, how many failed and on what; it can be stopped and continued from the same place. Re-running only the failed ones leaves the finished work alone.
The model used for analysis is chosen in Analytics → Settings and can be overridden for a specific run — a cheap model can chew through the archive while an expensive one re-checks the questionable calls. Until a model is chosen, judged characteristics are not produced at all: analysis gets as far as the time-based metrics and stops. The sampling of that model is set right beside it — temperature, top-p, the ceiling on the answer: analysis has to be reproducible, and the temperature that suits it is not the one that suits an agent holding a conversation.

## The language of the analysis
The same screen chooses the analysis language: the one the model reads the characteristics in and writes its justifications in.
It is a setting of the space, not of the reader. A justification is written once and stays with the conversation, and the whole team reads it — were the language taken from the request header, the same call would be explained differently depending on who opened the card, and there would be nobody to ask "why is this a 2 out of 5".
The language the conversation itself was held in has nothing to do with it: a Russian call can be analysed in English and the other way round. The model reads the transcript as it is — nobody asks it to translate.
Every conversation keeps the language it was analysed in. A month later that is the only way to answer why the justifications read the way they do: the setting could have been switched since. Switching it applies to the next analysis — scores already measured are not rewritten, and for that the conversations have to be analysed again.
The instructions of the characteristics are not translated: that is a prompt, not a label, and two versions of it would mean two different analyses of one conversation.

## The directory of parties
The same place holds the directory of conversation parties — both sides in one list.
Staff are the people whose work is scored. The telephony identifiers on a person's card are what let an uploaded recording find its own manager: without them a call has no performer, and there is nobody to compare in the reports.
Clients are the other side. A client carries a company, and that is what makes the "by company" breakdown meaningful: five calls to different people of one organisation add up into a single row. A client can be created here or right where they are assigned to a conversation.
The conversation card picks both parties and the number of that particular call; the changes go to the server with the Save button. Next to it are Refresh (analysis runs in the background and its result does not arrive instantly) and Analyse again, which asks first: it replaces the previous scores.

## API
Everything the module does is available over REST. The full description with examples is in the API reference.
| What | Request
| Register a conversation | POST /api/analytics/conversations
| Upload a batch | POST /api/analytics/conversations/batch
| Import an archive | POST /api/analytics/conversations/archive
| List of uploads | GET /api/analytics/uploads
| List conversations | POST /api/analytics/conversations/search
| Conversation card | GET /api/analytics/conversations/{id}
| Correct a conversation | PUT /api/analytics/conversations/{id}
| Start analysis | POST /api/analytics/conversations/{id}/analyze
| Run a report | POST /api/analytics/reports/run
| Characteristics catalogue | GET /api/analytics/metrics
| Filter values | GET /api/analytics/reports/filter-options
| Directory of parties | GET /api/analytics/sales-reps?kind=Manager|Client
| Dashboard tile order | PUT /api/analytics/views/pins/order
| Analysis spend | GET /api/analytics/usage
Why the list is a POST
The conversation list takes the same filters as reports, including the period and sets of values. Packing that into a query string means running into its length limit and into every client escaping it differently.

<!-- source: https://docs.speaknode.com/en/features/teams -->
## Teams & Spaces
Team collaboration through workspaces in Speaknode
Speaknode supports team collaboration through workspaces called Spaces.

## Spaces
A Space is a shared workspace where team members collaborate on agents, campaigns, and settings.

## What belongs to a Space
Agents and their configurations
Phone numbers
Tools and integrations
Campaigns
Webhooks
Billing and subscription

## Space Management
Create a new space for your team
Invite team members via email
Manage member roles and permissions

## User Roles
| Role | Capabilities
| Owner | Full access, billing management, member management
| Member | Create and manage agents, campaigns, tools
| Admin (platform) | Platform-wide settings, model management, user oversight

## Invitations
Team members are invited via email. The invitation flow:
Space owner sends an invite
Invited user receives an email with activation link
User registers or logs in via Keycloak SSO
User is added to the space

## Authentication
All users authenticate via Keycloak (OpenID Connect):
Email/password login
Google OAuth integration
SSO support
Token-based session management

<!-- source: https://docs.speaknode.com/en/guide/spaces -->
## Workspaces & Teams
Organize resources and collaborate with your team using Spaces in Speaknode
Workspaces (called Spaces in Speaknode) let you organize resources and collaborate with your team. Each space has its own set of agents, tools, phone numbers, campaigns, and members.

## Creating a Space
Click on your current space name in the top-left corner of the sidebar.
Click + Create Space.
Enter a Name for the space.
Click Create.
You are automatically assigned the Owner role in the new space.

## Inviting Members
Open Space Settings (gear icon in the sidebar or settings page).
Go to the Members tab.
Click + Invite Member.
Enter the person's email address.
Select a Role (see below).
Click Send Invite.
The invited person will receive an email with a link to join the space.
Invited users must have a Speaknode account. If they do not have one, they will be prompted to create one when they accept the invitation.

## Roles and Permissions
| Role | Description
| Owner | Full access. Can manage billing, delete the space, and manage all members. Each space has at least one owner.
| Admin | Can manage agents, tools, phone numbers, campaigns, and members. Cannot manage billing or delete the space.
| Member | Can view and use agents, tools, phone numbers, and campaigns. Cannot manage members or space settings.
Assign the Admin role to team leads who need to manage resources but should not have billing access.

## Managing Members
Open Space Settings > Members.
From the member list, you can:
Change Role: Click the role dropdown next to a member's name.
Remove Member: Click the remove button next to a member's name.
Removing a member immediately revokes their access to the space. Any resources they created remain in the space.

## Space-Scoped Resources
All resources in Speaknode belong to a space. When you switch between spaces, you see only the resources that belong to the selected space.
Scoped resources include:
Agents: Voice AI agents and their configurations.
Tools: Webhook tools and their schemas.
Phone Numbers: Imported phone numbers and their agent links.
Campaigns: Outbound call campaigns and their results.
Webhooks: Event subscriptions and delivery history.
Conversations: Call history and transcripts.
Your personal account settings (email, password, API keys) are global and not tied to any specific space.

## Switching Between Spaces
Click on the current space name in the top-left corner of the sidebar.
Select the space you want to switch to from the dropdown.
The page will reload with the selected space's resources.
