# Outbound campaigns

<!-- source: https://docs.speaknode.com/en/features/campaigns -->
## Outbound Campaigns
Mass outbound calling campaigns with AI agents in Speaknode
Speaknode allows you to run mass outbound calling campaigns using AI agents.

## Overview
A campaign is a collection of outbound calls to a list of contacts. Each call is handled by an AI agent with dynamically substituted variables per contact.

## Campaign Setup
Select an agent — choose the AI agent that will handle the calls
Add contacts — provide a list with phone numbers and variable data
Configure variables — map contact data to agent variables (e.g., {{customer_name}}, {{order_id}})
Launch — the platform sequentially dials each contact

## Campaign Items
Each contact in a campaign is a campaign item with:
Phone number to call
Variable values for this specific call
Status tracking (pending, in progress, completed, failed)
Link to the conversation session after the call

## How It Works
Campaign is created with a list of items
For each item, the platform:
Creates a LiveKit room
Dispatches the agent with item-specific variables
Initiates the outbound call via the telephony provider
Tracks the session status
Results are available per item (recording, transcript, status)

## Monitoring
Campaign progress is visible in the admin panel:
Overall campaign status
Per-item call results
Links to individual conversation sessions

<!-- source: https://docs.speaknode.com/en/guide/campaigns -->
## Outbound Campaigns
Guide to creating and managing outbound calling campaigns in Speaknode
Campaigns let you automate outbound calls to a list of contacts using a selected agent. Upload a contact list, map the columns, and Speaknode will call each contact automatically.

## Creating a Campaign
Navigate to Campaigns in the sidebar.
Click + Create Campaign.
Enter a Name for the campaign.
Select the Agent that will handle the calls.
Click Create.

## Uploading Contacts
Campaigns use Excel files (.xlsx) as the contact source.
In the campaign detail page, click Upload Contacts.
Select an Excel file from your computer.
Speaknode will parse the file and show a preview of the columns.
The file must contain at least one column with phone numbers. Other columns can be used as dynamic variables in the agent's system prompt and first messages.

## Mapping Columns
After uploading, you need to map the Excel columns to Speaknode fields.
Phone Number (required): Select the column that contains phone numbers.
Variables (optional): Map additional columns to variables used in your agent's configuration.
For example, if your agent's system prompt contains {{customer_name}} and {{order_id}}, map the corresponding Excel columns to these variables.
Make sure your phone numbers include the country code (e.g., +1234567890). Numbers without a country code may not be dialed correctly.

## Starting the Campaign
Review the mapped columns and contact count.
Click Start Campaign.
Speaknode begins dialing contacts from the list.
Once a campaign is started, it cannot be undone. Make sure your agent is properly tested and your contact list is correct before starting.

## Monitoring Progress
While the campaign is running, you can monitor its progress on the campaign detail page:
Total Contacts: The total number of contacts in the list.
Completed: The number of contacts that have been called.
In Progress: Calls currently active.
Pending: Contacts waiting to be called.
Failed: Calls that could not be completed (e.g., invalid number, no answer).

## Viewing Results
After the campaign completes (or while it is in progress), you can review the results for each contact.
Open the campaign detail page.
Scroll down to the Items list.
Each item shows:
The contact's phone number and mapped variables.
The call status (completed, failed, pending).
A link to the conversation record (if the call was answered).
Click on any item to view its full conversation details in the Conversations page.

## Summary
| Step | Action
| 1 | Create a campaign and select an agent
| 2 | Upload an Excel file with contacts
| 3 | Map columns to phone number and variables
| 4 | Start the campaign
| 5 | Monitor progress and review results
