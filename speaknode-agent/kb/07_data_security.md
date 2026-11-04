# Data security

<!-- source: https://www.speaknode.com/ -->
Is SpeakNode HIPAA compliant for medical front-desk use?
Your data stays in your AI provider account (your OpenAI, Anthropic, or Deepgram tenant with its own BAA where applicable). SpeakNode orchestrates the workflow — it does not store call audio or PHI by default. Medical practices configure their AI provider for HIPAA coverage and use SpeakNode to wire the AI phone agent to the PMS/EHR.

## Tell us your numbers. We'll show you the payback.
Book a call with sales. We look at your call volume, what a booking is worth, and which agent to build first.

<!-- source: https://www.speaknode.com/solutions/ai-medical-receptionist -->
Compliance and data handling
Be careful with vendors that claim “HIPAA compliant” on a marketing page. The honest framing matters.
Your data stays in your AI provider account (e.g., your OpenAI, Anthropic, or Deepgram tenant with its own BAA where applicable). SpeakNode orchestrates the workflow.
In practice, that means you choose an AI provider that signs your BAA, configure your workflow so PHI is processed inside their environment, and SpeakNode passes the call between nodes without holding patient data outside that environment. SpeakNode itself does not claim HIPAA compliance, does not claim SOC 2 certification, and does not sign BAAs directly. Anyone telling you otherwise about a voice AI orchestration layer is overstating what their software does.
Pricing

<!-- source: https://docs.speaknode.com/en/lifecycle-support -->
## Software lifecycle support
Support, evolution, incident response, and security processes for the Speaknode platform
This document describes the processes, organisational practices, and technical means used by the developer of the «Speaknode AI-agent automation platform» to keep the software working, fix defects, ship new releases, and interact with users. It applies both to the cloud deployment and to on-premise delivery to a customer's infrastructure.

## General information
## Product name
Full product name: «Speaknode AI-agent automation platform». The document also uses the short forms «Speaknode» and «the software».

## Purpose
The document describes how the developer:
keeps the software working throughout its life cycle;
fixes defects discovered in operation;
evolves the software — ships new versions with extended functionality and improvements;
communicates with users (technical and informational support).

## Lifecycle support processes
## Overall lifecycle model
The lifecycle is sustained by the developer and covers:
design, development, and testing of new software versions;
release and delivery of versions to end users;
user support and technical assistance;
intake, diagnosis, and resolution of defects discovered during operation;
continuous improvement based on user feedback and the internal product roadmap;
information security throughout the lifecycle.
The processes run continuously: new versions ship as changes accumulate, user requests are accepted via the channels described below, defect fixes are prioritised and folded into the current release cycle.

## Development and release process
Development follows an iterative model with short release cycles. The key elements are:
Requirements management — incoming requests, suggestions, and feedback are captured in the task tracker, prioritised, and added to the roadmap.
Development and code review — changes go into a single source-control system and are subject to mandatory peer code review.
Automated testing — critical components and scenarios are covered by unit and integration tests run by CI on every change.
Manual testing on staging environments configured to closely match production: agent nodes, integrations, telephony, and the embeddable widget.
Release artefacts — source code is built into container images, validated, and tagged with a release version.
Release — artefacts are published to the container registry; cloud installations are upgraded centrally via Kubernetes, on-premise installations receive updated Helm charts.
Non-functional changes (bug fixes, optimisations) may ship more frequently than functional updates and are applied to the cloud installation automatically.

## Delivery and deployment
The software is delivered as:
Cloud operation — the user accesses the software through a web browser over the Internet (https://app.speaknode.com); deployment and upgrades are handled by the developer; the user only needs to register a workspace and connect their own credentials for external services (LLM providers, telephony).
On-premise in the customer's infrastructure — the server side is deployed on Kubernetes; delivery is in the form of Helm charts and a set of container images, accompanied by the operations documentation (Architecture, Installation guide) describing installation, initial configuration, and routine maintenance.
In both delivery options the client side (workspace web UI and the embeddable voice-agent widget) runs in the user's browser and does not require additional software on the workstation.
For on-premise installations, updated chart and image versions are delivered to the customer through an agreed channel; the customer's operations team applies updates via Helm and Kubernetes.

## Support process
User support is provided by the developer and includes:
intake and registration of user requests;
classification by type (operations question, incident, change request) and priority;
diagnosis: explanation to the user, request for more information, or routing to engineering;
progress updates and delivery of a resolution or workaround;
closure after user confirmation.
Support channels
Primary support channels:
Built-in AI assistant in the workspace at https://app.speaknode.com — the main channel for day-to-day questions, agent setup help, and feature explanations. The assistant responds in a conversational format around the clock and escalates to a human specialist when needed.
Email at — a private channel for workspace inaccessibility, critical incidents, and requests requiring confidentiality.
Documentation and self-service
In addition to contacting support, the user has the following self-service resources:
the operations documentation published at , including Functional characteristics, User guide, Architecture, and Installation guide;
the built-in AI assistant that can explain, design, and debug agent and telephony scenarios interactively inside the workspace;
conversation history with recordings, transcripts, telemetry, and per-session error messages, allowing users to localise the cause of an incident on their own.

## Defect resolution process
A defect is a deviation of actual software behaviour from the behaviour documented in the operations docs, or a failure of a software component.
The defect resolution process consists of:
Intake. A defect report comes in through a support channel or is surfaced by internal monitoring and observability. Every report is logged in the task tracker.
Classification and prioritisation. The report is classified as a defect, operations incident, or change request. Priority is assigned based on user impact, availability of a workaround, and the number of users affected.
Diagnosis. A support engineer or developer reproduces the issue, analyses session logs, telemetry, and system logs, and asks the user for additional information if needed.
Resolution. For critical incidents a workaround is provided first and (or) a hot-fix is applied to the cloud installation. A permanent fix lands in source control, goes through code review and automated testing, and ships in the next release.
Delivery of the fix. For cloud operation the fix reaches the user automatically with the next component upgrade. For on-premise operation the fix ships in an updated Helm chart and container images; the customer's operations team applies the update.
Notification and closure. The user is informed of the result and the request is closed.
Specific response and resolution times are not fixed by this document and may be specified in a separate agreement (contract, SLA) with a particular customer.

## Continuous improvement
Continuous improvement is driven by:
user feedback (requests via support channels, suggestions through the in-app AI assistant);
the internal product roadmap maintained by the engineering team — market requirements, new technologies (new LLM models, new TTS/STT providers, new telephony integrations), and architectural improvements;
operational analysis — common configuration errors, performance bottlenecks, and the most-requested integrations.
Improvement work takes the form of:
new functionality (new agent types, new integrations, new voice scenarios, support for new LLM/TTS/STT providers and models);
usability improvements (agent builder, AI assistant, debugging tools);
performance and scalability optimisation;
updates to libraries, runtimes, and base images.
Changes flow into the standard release cycle. Notable changes are documented in the operations docs.

## Information security during support
The lifecycle processes follow these principles:
developer staff have access to production environments and user data only to the extent required by their role;
access to code, infrastructure, and the task tracker is via personal accounts;
credentials for external services that users entrust to the platform (LLM API keys, telephony tokens, webhook secrets) are stored in a secure secret store separate from agent configuration and are accessed only at execution time;
dependencies and base container images are updated regularly with vulnerability information; critical security updates are prioritised and shipped outside the regular release cycle;
if an information-security incident occurs, affected users are notified through the support channels.

## Lifecycle infrastructure
## Development, staging, and production environments
The lifecycle uses logically separated environments:
development — for writing, validating, and running code locally;
staging — for verifying built versions on stands closely matching production;
production — the cloud installation accessible to users over the Internet, or the customer's infrastructure for on-premise operation.
Changes propagate through environments sequentially: reaching production requires passing automated and manual checks in the preceding environments.

## Source control and build systems
a single source-control system with mandatory code review and change history;
a CI/CD system that builds container images, runs automated checks, and publishes artefacts;
a container registry used both for cloud operation and for on-premise delivery.

## Request tracking and task management
user-facing support channels (the in-app AI assistant and support email) are integrated with the internal task tracker; every request requiring engineering work is captured as a task and linked to a release;
an internal product roadmap is maintained; priorities are reviewed regularly by the engineering team.

## Distribution and storage
source code and build configuration are stored in source control;
binary artefacts (container images) are stored in the container registry ;
on-premise Helm charts are versioned and delivered to the customer over an agreed channel together with the operations documentation;
operations documentation is published at and kept up to date.

## Staffing for software support
## Roles
The developer maintains a qualified team covering the following roles:
Backend engineers — design and maintenance of the API, the voice-agent execution engine, integration services (telephony, widget), storage, and observability;
Frontend engineers — workspace web UI, agent builder, in-app AI assistant, and the embeddable widget;
AI/integrations engineers — integrations with LLM providers and TTS/STT providers, media processing, real-time protocols (WebRTC, SIP), agent tools and webhooks;
Operations engineers (DevOps / SRE) — Kubernetes clusters, build and delivery pipelines, observability, reliability, and scaling;
QA engineers — automated and manual testing, regression coverage of release candidates;
Support specialists — request intake, registration, and processing, liaison with engineering on incidents and feature requests;
Technical writers and content managers — preparing and maintaining the operations documentation;
Product managers and engineering leads — prioritisation, release coordination, product direction.
Headcount in each role is determined by current product and operations needs and ensures all processes described in this document are performed.

## Qualification requirements
General requirements for staff involved in the lifecycle:
relevant education (higher or vocational in IT) or demonstrable practical experience in the role;
proficiency in the relevant technologies and tooling: web frameworks and languages (TypeScript, C#, Python), databases, real-time protocols for engineers; Kubernetes, Helm, observability, and CI/CD for operations engineers; an overall understanding of the platform's architecture and how voice agents work for support specialists;
understanding of secure-development principles and handling of confidential user data;
ability to work in an iterative model and respond promptly to user requests.

## Sustaining competencies
Staff competencies are sustained by:
onboarding and knowledge sharing inside teams;
continuous work with current versions of the technology stack (runtimes, databases, Kubernetes, LLM models);
staff involvement in product development and operation, providing direct hands-on familiarity with the deployed solution;
keeping internal technical documentation up to date (architecture descriptions, support playbooks, component operation instructions).

## User contact channels
The developer provides the following user-facing channels for support, evolution, and operational questions:
| Channel | Address | Purpose
| Built-in AI assistant | https://app.speaknode.com | Primary support channel: operations questions, help with agent and scenario setup, feature explanations
| Email | | Private channel: workspace inaccessibility, critical incidents, confidential requests
| Operations documentation | | Reference material on the software, features, typical scenarios, and troubleshooting
The in-workspace AI assistant is available to users around the clock. Email requests are handled by the support team during business days; critical incidents reported by email are reviewed regardless of working hours.
