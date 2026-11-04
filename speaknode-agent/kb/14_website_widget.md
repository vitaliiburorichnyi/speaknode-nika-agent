# Website widget

<!-- source: https://docs.speaknode.com/en/features/widget -->
## Website Widget
Embeddable web component for adding a voice agent to any website
Speaknode provides an embeddable web component that adds a voice agent to any website.

## Overview
The widget is an Angular web component packaged as <speaknode-agent>. It connects to a published agent and allows website visitors to have a voice conversation directly in the browser.

## Installation
Place the custom element where you want the widget to appear, and add the loader script anywhere on the page (typically right after the element or before </body>):
<speaknode-agent agent-id="your-agent-id"></speaknode-agent>
<script src="https://widget.speaknode.com/speaknode-widget-loader.js"></script>
The loader registers the <speaknode-agent> custom element, fetches the published agent configuration, and renders the widget once the user clicks to start a conversation.

## Configuration
## Attributes
| Attribute | Type | Description
| agent-id | string | ID of the published agent
| agent-token | string | Pre-generated JWT token (optional)
| language | string | Override language locale
| initialized | boolean | Use external configuration mode

## Passing Variables via URL
Dynamic variables can be passed as URL query parameters. The widget reads them automatically and passes to the agent at dispatch time.
Example:
https://yoursite.com/page?customer_name=John&order_id=12345

## Widget Configuration in Admin Panel
In the agent edit page, the Widget tab allows you to:
Configure widget placement and appearance
Generate embed code
Set custom theme colors

## How It Works
Widget loads on the page and fetches the public agent configuration
User clicks to start a conversation
Widget requests a dispatch token from the backend
LiveKit room is created, agent is dispatched
Widget connects to the room via WebRTC
Voice conversation begins in real time
When the conversation ends, the session is saved

## Requirements
The agent must be published (is_published: true)
The user's browser must support WebRTC
Microphone access is required

<!-- source: https://docs.speaknode.com/en/guide/widget -->
## Embedding the Widget
Add a Speaknode voice AI agent widget to any web page
The Speaknode widget lets you add a voice AI agent to any web page. Visitors can start a voice conversation directly in their browser without leaving your site.

## Prerequisites
Before embedding the widget, your agent must be published. See Creating and Configuring Agents.

## Getting the Embed Code
Open the agent you want to embed.
Go to the Widget section in the agent settings.
Copy the generated embed code.

## HTML Snippet
The embed code uses a custom HTML element:
<speaknode-agent
agent-id="your-agent-id"
agent-token="your-agent-token"
language="en"
></speaknode-agent>
<script src="https://widget.speaknode.com/speaknode-widget-loader.js"></script>
The agent-token is a public token scoped to the specific agent. It is safe to include in client-side code but should not be confused with your personal API token.

## Attributes
| Attribute | Required | Description
| agent-id | Yes | The unique identifier of the published agent.
| agent-token | Yes | The public token for this agent, used for authentication.
| language | No | The default language code (e.g., en, es, de). If omitted, the agent's default language is used.

## Appearance Settings
## Variant
The widget supports three visual variants:
| Variant | Description
| Tiny | A small floating button that expands when clicked. Minimal footprint.
| Compact | A medium-sized widget with a microphone button and status indicator.
| Full | A full panel with transcript display, microphone controls, and language selection.
Set the variant by adding the variant attribute:
<speaknode-agent
agent-id="your-agent-id"
agent-token="your-agent-token"
variant="compact"
></speaknode-agent>

## Placement
Control where the widget appears on the page:
<speaknode-agent
agent-id="your-agent-id"
agent-token="your-agent-token"
placement="bottom-right"
></speaknode-agent>
Common placement values: bottom-right, bottom-left, top-right, top-left.

## Passing Variables via URL Parameters
The widget automatically reads URL query parameters and passes them as dynamic variables to the agent session.
For example, if your agent uses {{customer_name}} and {{plan}}, direct users to:
https://your-site.com/support?customer_name=Alice&plan=Pro
The widget will pass customer_name=Alice and plan=Pro to the agent.
This is useful for embedding the widget on a CRM page or customer portal where user details are available in the URL.

## Language Dropdown Toggle
If your agent supports multiple languages, the widget can display a language selector dropdown.
By default, the language dropdown is shown in the Full variant and hidden in the Tiny and Compact variants. You can override this behavior:
<speaknode-agent
agent-id="your-agent-id"
agent-token="your-agent-token"
show-language-selector="true"
></speaknode-agent>
Set show-language-selector="false" to hide it in the Full variant, or "true" to show it in Compact.

## Complete Example
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Support Page</title>
</head>
<body>
<h1>Need help? Talk to our AI assistant</h1>
<speaknode-agent
agent-id="abc123"
agent-token="tok_xyz789"
language="en"
variant="compact"
placement="bottom-right"
show-language-selector="true"
></speaknode-agent>
<script src="https://widget.speaknode.com/speaknode-widget-loader.js"></script>
</body>
</html>

## Troubleshooting
| Issue | Solution
| Widget not appearing | Ensure the <script> tag is included and the URL is correct. Check the browser console for errors.
| "Agent not found" error | Verify the agent-id and agent-token values. Make sure the agent is published.
| No audio | The user must grant microphone access. Some browsers block microphone on non-HTTPS pages.
| Variables not working | Ensure URL parameter names match the variable names exactly (case-sensitive).
