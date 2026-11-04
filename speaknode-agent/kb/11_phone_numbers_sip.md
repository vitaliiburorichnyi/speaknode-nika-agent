# Phone numbers sip

<!-- source: https://docs.speaknode.com/en/features/telephony -->
## Telephony
Phone call integration with Twilio and VoxImplant in Speaknode
Speaknode integrates with telephony providers to enable AI agents to make and receive phone calls.

## Supported Providers
| Provider | Inbound | Outbound | Notes
| Twilio | Yes | Yes | Direct SIP trunk integration
| VoxImplant | Yes | Yes | Via WebSocket Media Bridge (no direct SIP access)
| Custom SIP | Yes | Yes | Connect your own PBX / SIP trunk over standard SIP

## Inbound Calls
When a call comes in to a connected phone number:
Telephony provider sends a webhook to the platform
Webhook is received via Kafka
Backend identifies the agent linked to the phone number
LiveKit room is created with SIP participant
AI agent is dispatched to the room
Conversation begins

## Phone Number Management
Import existing numbers from Twilio or VoxImplant
Link a phone number to a specific agent
Configure per-number settings

## Outbound Calls
Outbound calls can be initiated:
Individually via the API
In bulk via Outbound Campaigns
The platform creates a LiveKit room, dispatches the agent, and initiates the outbound call via the configured telephony provider.

## Custom SIP
In addition to the Twilio and VoxImplant integrations, Speaknode lets you connect any SIP telephony — your own PBX (Mango Office, Asterisk, FreeSWITCH, PBX-as-a-Service, etc.) — over standard SIP. The LiveKit server acts as the SIP endpoint on both sides:
Inbound (PBX → LiveKit): your SIP provider sends INVITE to the public LiveKit SIP domain. Authorization is enforced by an IP allowlist and optional Digest auth.
Outbound (LiveKit → PBX): LiveKit dials INVITE to your PBX's SIP server. Authentication is an optional Digest username/password or IP-trust (the PBX trusts our outbound IPs).
For each account the admin configures the PBX SIP server, transport, destination country, allowed inbound IPs, and credential pairs. Once created, the platform returns the public SIP gateway domain and the list of our outbound IPs — admins share these with the PBX owner so the routing can be wired up.
A step-by-step setup for both sides is in the Custom SIP guide.

## VoxImplant Integration
VoxImplant does not provide direct SIP trunk access. The platform uses a WebSocket Media Bridge — a Node.js service that:
Receives audio from VoxImplant via WebSocket
Streams it into a LiveKit room
Sends LiveKit audio back to VoxImplant
This allows full agent functionality with VoxImplant as the telephony backend.

## SIP Trunk (LiveKit)
LiveKit Server includes a built-in SIP component that handles:
SIP trunk registration
Dispatch rules for routing calls to rooms
Direct SIP-to-WebRTC bridging (for providers that support it)

<!-- source: https://docs.speaknode.com/en/guide/phone-numbers -->
## Phone Number Management
Import and manage phone numbers from Twilio and VoxImplant in Speaknode
Speaknode lets you connect phone numbers from external telephony providers so your agents can make and receive real phone calls. Currently, Twilio and VoxImplant are supported.

## Importing Numbers from Twilio
## Prerequisites
You need an active Twilio account with at least one phone number purchased.

## Step-by-Step
Navigate to Phone Numbers in the sidebar.
Click + Import Number.
Select Twilio as the provider.
Enter your Twilio credentials:
Account SID: Found on your Twilio Console dashboard.
Auth Token: Found on your Twilio Console dashboard.
Click Connect. Speaknode will fetch your available phone numbers.
Select the phone number(s) you want to import.
Click Import.
Speaknode will configure webhooks on the imported Twilio number. Any existing webhook configuration on that number will be overwritten.
You can find your Account SID and Auth Token at https://console.twilio.com on the main dashboard page.

## Importing Numbers from VoxImplant
## Prerequisites
You need a VoxImplant account with a service account key and at least one application with a phone number attached.

## Step-by-Step
Navigate to Phone Numbers in the sidebar.
Click + Import Number.
Select VoxImplant as the provider.
Upload or paste your Service Account Key JSON file. This is a JSON file generated in the VoxImplant control panel under service accounts.
Click Connect. Speaknode will fetch your VoxImplant applications and their numbers.
Select the Application from the dropdown.
Select the Phone Number from the available numbers in that application.
Click Import.

## Linking a Number to an Agent
After importing a phone number, you need to link it to an agent so that incoming calls are handled by that agent.
In the Phone Numbers list, find the number you want to configure.
Click on the number to open its settings.
Select an Agent from the dropdown.
Click Save.
Incoming calls to this number will now be routed to the selected agent.
A phone number can be linked to only one agent at a time. An agent can have multiple phone numbers linked to it.

## Editing a Phone Number
Click on a phone number in the list.
Change the linked agent or other settings.
Click Save.

## Deleting a Phone Number
Click on the phone number you want to remove.
Click Delete.
Confirm the deletion.
Deleting a phone number from Speaknode does not cancel or release the number from your Twilio or VoxImplant account. You will continue to be billed by the provider for the number itself.

## Summary
| Provider | Credentials Needed | What Gets Imported
| Twilio | Account SID + Auth Token | Phone numbers from your Twilio account
| VoxImplant | Service Account Key JSON | Phone numbers from a selected application

<!-- source: https://docs.speaknode.com/en/guide/custom-sip -->
## Custom SIP
Connect your own PBX / SIP trunk to Speaknode — setup on both the PBX side and the platform side
Speaknode supports connecting any SIP telephony — your own PBX (Mango Office, Asterisk, FreeSWITCH, a virtual PBX from a provider) — over standard SIP. This is an alternative to the Twilio and VoxImplant integrations for setups where you already have your own SIP trunk.

## Architecture
A Custom SIP connection has two sides, each with its own configuration. Both sides must be set up for calls to flow in both directions.
| Side | Responsibility
| Your PBX / SIP provider | Terminates the PSTN call, routes inbound to us, accepts our outbound
| Speaknode (LiveKit SIP) | Accepts inbound INVITE from your PBX, initiates outbound to it, dispatches the AI agent into a LiveKit room
PSTN ──► Your PBX ──SIP INVITE──► LiveKit SIP gateway ──► AI agent (LiveKit room)
PSTN ◄── Your PBX ◄──SIP INVITE── LiveKit SIP gateway ◄── AI agent (outbound)
LiveKit as a SIP endpoint
The platform's LiveKit server includes a built-in SIP component that behaves like a regular SIP trunk: it accepts INVITE, authenticates, routes into a LiveKit room with the agent, and conversely originates outbound INVITE under its own identity.

## What to configure on the platform side
In Speaknode you create a Custom SIP account — the bundle of parameters describing your PBX. Once created, the platform returns the public LiveKit data (gateway domain and our outbound IPs) that you share with the PBX side.

## Create the account
Go to Phone Numbers in https://app.speaknode.com
Click Import number → From Custom SIP
In the drawer click Add Custom SIP account
Fill out the form:
| Field | What to enter | Example
| Account name | Any human-readable name | Mango Office
| SIP server address | host[:port] of your PBX's SIP server (for our outbound calls). Empty = outbound disabled | vpbx400312852.mangosip.ru
| SIP transport | Transport protocol: Auto / UDP / TCP / TLS. Auto lets LiveKit pick | Auto
| Destination country | ISO-3166 α-2 (2 letters). Hint for LiveKit billing/routing, not a destination restriction | RU
| Allowed inbound IPs | Comma-separated list of IPv4 / IPv4 CIDR — the PBX IPs from which LiveKit will accept INVITE | 1.2.3.4, 10.0.0.0/24
| Outbound SIP username/password | Optional. If set — we authenticate to your PBX via Digest auth. If empty — IP-trust (your PBX trusts our IPs) | livekit-out / ***
| Inbound SIP username/password | Optional. If set — LiveKit requires Digest auth from your PBX on inbound calls. Most providers don't challenge inbound — leave empty | empty

## Pick up the platform's public parameters
Once the account is created the card shows:
Domain — the public LiveKit SIP gateway domain, e.g. livekit-sip.speaknode.com:5060. This is the destination your PBX sends INVITE to for inbound calls.
Our SIP server IPs — the list of our outbound IPs, e.g. 78.47.123.164:5060. Add these to your firewall whitelist so the PBX accepts our outbound calls.
Hand these to the PBX admin — without them the other side can't be configured.

## Bind a phone number
Once both sides are configured you can bind a number to an agent:
Phone Numbers → Import number → From Custom SIP
Pick the SIP account you created
Enter the number in E.164 format (e.g. +71234567890)
(optional) add a label
Click Connect
After binding, open the number's card and assign the agent that should handle inbound calls to it.

## What to configure on the PBX side
On your SIP PBX (Mango, Asterisk, etc.) you set up three things: where to forward inbound calls, who is allowed for outbound, and authentication (if used).

## Route PBX outbound to LiveKit (our inbound)
For PSTN inbound calls through your PBX to the agent, configure a route to our SIP gateway:
Destination / Outbound trunk URI: the LiveKit SIP gateway domain from the account card in Speaknode — e.g. sip:livekit-sip.speaknode.com:5060
Transport: matches what you set in the Custom SIP account (UDP / TCP / TLS or Auto)
Authentication (if Inbound auth is enabled): username/password from the Custom SIP account form
The specific steps depend on your vendor:
Mango Office — SIP trunk → "Routing" section → create a rule pointing the destination to our domain
Asterisk — add an extension in extensions.conf with Dial(SIP/livekit-sip.speaknode.com) via a configured [livekit] SIP peer
Virtual PBX from another provider — look for "Outbound routes" / "Outbound routing" / "SIP trunk"

## Whitelist our IPs (our outbound)
If your PBX sits behind a firewall, add our outbound IPs (Our SIP server IPs from the card) to the whitelist — without that your server will drop our INVITE packets for outbound calls from the agent.
Depending on the provider:
Corporate firewall — add IPs to your rules
Cloud PBX (Mango etc.) — IP whitelist in the admin panel
Asterisk + iptables — iptables -A INPUT -s <ip> -p udp --dport 5060 -j ACCEPT

## Outbound authentication (if enabled)
If you set Outbound SIP username/password in our account — create a SIP account on the PBX side with the same credentials. LiveKit will use them to authenticate when originating outbound calls.
If left empty — IP-trust mode: the PBX just trusts our IPs without a username/password. This is typical for Mango SIP trunk, Plivo, and other IP-allowlist providers.

## Pass call data to the agent
The agent knows who is calling and which number was dialled, and can receive any data of yours about the call (amount, contract number, customer name).
Number in To — the number bound to the agent, exactly as you imported it (e.g. 71234567890). It selects the agent; a call to another number or in another format (+7… instead of 7…, an extension like 1001) is rejected.
Number in From — the caller's number. The agent sees it as the variable {{system__from_number}}; call history shows it as the customer's number.
Your own data — as X-* headers in the INVITE:
INVITE sip:[email protected] SIP/2.0
From: <sip:[email protected]>;tag=…
To: <sip:[email protected]>
X-minimumAmount: 15000
X-loan-id: L-42
To turn headers into agent variables:
Declare the variables on the agent — e.g. minimumAmount and loan_id — and use them in the prompt or first message: {{minimumAmount}}.
In the phone number card (Phone Numbers → number), block SIP headers → agent variables, set the prefix X-.
Header X-minimumAmount fills variable minimumAmount: the prefix is stripped, case does not matter, - and _ are the same (X-loan-id → loan_id). Only variables declared on the agent are filled; system variables (system__*) are never filled from headers. A value is up to 1024 characters, at most 50 variables per call.
The prefix selects headers for variables. Every header of the INVITE is stored regardless, including the standard ones (P-Asserted-Identity, Diversion, User-Agent) — you can see them on the call card, see Debugging.
Values are substituted into the agent's system prompt and first message the same way as outbound-call variables, and are kept in the call history.
The trunk starts passing headers when a number is bound. Accounts created before 2026-10-13 need to re-bind a number once or run Reprovision (see below) — otherwise the headers never reach us.

## Debugging: what the PBX actually sent
A variable came out empty, and it is unclear why: the PBX did not send the header, sent it under another name, or the variable is not declared on the agent. To tell these apart, every incoming call stores all the headers of its INVITE — not only the ones that matched the prefix and the agent's schema.
Look here: Conversations → Calls → the call → SIP INVITE headers.
The table holds exactly what arrived: names in lower case, values as they came. Next to it, the Agent variables block shows what of it reached the agent. Comparing the two answers the question:
| What you see | What it means
| The header is not in the table at all | The PBX did not send it — a question for their side
| Header is there, variable is not | The name did not match, or the variable is not declared on the agent
| Both are there | All good
| The header table is empty | The trunk was not recreated after the number was bound — run Reprovision
Headers are stored regardless of the prefix and the agent's schema, so the table fills in even before any mapping is configured: first see what the PBX sends, then set up the prefix and the variables.
Headers carry personal data — names, amounts, contract numbers. They are visible to everyone with access to call history and are sent to the CallStarted / CallFinished webhooks. Values are never written to the logs, only header names.

## Authentication modes
A Custom SIP account configures two directions independently — outbound and inbound. For each, you choose one of two modes:
| Mode | When to use | What to do
| Digest auth | The provider requires SIP authentication via username/password | Set both fields (username + password)
| IP-trust | The provider authorizes via IP allowlist without authentication (Mango SIP trunk, Plivo, etc.) | Leave both fields empty
Pair invariant
The username and password are always set together or both left empty. Filling one without the other is rejected by the UI.
When editing an account, the password field has three states:
Untouched — current password is kept
Explicitly cleared — auth is disabled (clear the username too)
New value entered — password is replaced

## Verify and Reprovision
The Custom SIP account card exposes two diagnostic operations:

## Verify
The Verify button runs a health check and shows four checks:
| Check | Meaning
| Local config | Account is correctly configured in the DB (required fields are set)
| Inbound trunk | LiveKit sees the inbound SIP trunk, ready to accept inbound calls
| Outbound trunk | LiveKit sees the outbound SIP trunk, ready to originate outbound calls
| Numbers in sync | Bound numbers are synced with LiveKit
Each check is OK / Failed / Skipped. On Failed the reason is shown.

## Reprovision
The Reprovision button deletes and recreates the LiveKit trunks from the current DB config. Use it in two cases:
After editing credentials / server / transport on the account card (changes auto-reinitialize trunks; reprovision is a fallback if auto reinit didn't catch)
If LiveKit was unavailable when you first created the account or bound a number and the trunks didn't get created (HTTP 500 on bind / create)
Reprovision and active calls
Reprovision deletes the existing trunks. Any active calls going through them at that moment will drop. Run reprovision outside peak hours or when there are no active sessions.

## Deleting the account
When you delete a Custom SIP account (the Delete button on the card), the platform:
Removes all bound numbers
Removes the LiveKit inbound / outbound trunks
Soft-deletes the account in the DB
Your PBX-side routing to our gateway will remain — clean it up manually in the provider's admin panel if needed.

## Common issues
| Symptom | Cause | Fix
| Verify → Inbound trunk: Failed | LiveKit didn't create the inbound trunk (was unavailable on create) | Reprovision
| Verify → Numbers in sync: Failed | DB ↔ LiveKit drift (e.g., manual edit in LiveKit) | Reprovision
| Inbound calls don't reach the agent | Wrong destination on the PBX, or our IP isn't whitelisted | Check Domain on the card and the IP allowlist on the PBX
| Outbound fails with 403 / 407 | Outbound auth mismatch | Check Outbound username/password on the card and the SIP account on the PBX
| Outbound times out | Our IPs aren't whitelisted on the PBX firewall | Add Our SIP server IPs to the whitelist
| 409 on phone number bind | The number is already bound to another Custom SIP account (possibly in another Space) | Use a different number or remove the prior binding
| A variable from a header is empty | The header was not sent, was sent under another name, or the variable is not declared on the agent | Compare the two tables on the call card — Debugging
| No headers on the call card | The trunk was created before the number was bound and does not know about header passing | Reprovision
