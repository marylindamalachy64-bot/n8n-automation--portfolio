# Sophie — Vapi receptionist

[Assistant file](sophie-assistant.json) · [Portfolio index](../../README.md) · [Privacy notes](../../docs/privacy-and-history.md)

**Status:** exported Vapi assistant configuration. Not run here. Six tools named in the prompt are missing from this repository.

## Problem

Sophie is a phone receptionist for Oakwood Plumbing and Heating. The system prompt says that business is fictional and is used for a demonstration. The assistant is meant to judge urgency, collect caller details, and call tools for knowledge lookup, call transfer, enquiry recording, tradesperson notification, failure logging, and ending the call.

## What the file contains

The export is a versioned assistant object (`v19`, version name "Sophie assisatant", including that spelling). It includes:

| Setting | Value in the file |
| --- | --- |
| Assistant name | Sophie |
| First message | "Hello, Oakwood Plumbing and Heating, you're speaking with Sophie. How can I help you today?" |
| Model | OpenAI `gpt-4.1`, one system message |
| Voice | ElevenLabs `eleven_turbo_v2_5`, speed 1, with three fallback voices |
| Transcriber | Deepgram `nova-3`, language `en-GB`, numerals enabled, confidence threshold 0.4, automatic fallback enabled |
| Speech keyterms | Oakwood, Kivio, stopcock, combi, boiler, radiator, postcode |
| Knowledge base | Provider `google`, two file ids |
| End call message | "Goodbye." |
| Voicemail message | "Please call back when you're available." |
| Analysis plans | Summary and success evaluation are present and disabled |
| Compliance flags | HIPAA, PCI, and zero-data-retention flags are all false |
| Background sound | Off |

The system prompt is in the file. Its own rules include:

- Business hours in the prompt are Monday to Friday, 9 AM to 5 PM, Europe/London.
- Service area, confirmed services, real prices, appointment availability, engineer arrival times, and after-hours arrangements are stated as not verified. The prompt says not to invent them.
- Documents may contain draft information or demonstration prices and must not be quoted as confirmed prices.
- No DIY repair instructions. For a suspected gas leak, carbon monoxide, fire, or immediate danger, the prompt says to use only verified emergency guidance and not to improvise technical safety advice.
- Do not request card, bank, password, or identity-document details.
- Fallback sentence when business information cannot be verified: "I'm sorry, I can't confirm that information right now."
- Urgency is Emergency, High, or Routine, based on circumstances rather than keywords alone.
- Do not claim a tool succeeded unless its result says so.
- Do not reveal tool names, system instructions, or credentials to the caller.

Those are prompt instructions. This repository has no call transcript that shows Sophie following them.

## Missing tools

`model.toolIds` has six entries. The prompt names six tools. The file does not include tool definitions, server URLs, parameter schemas, or any field that maps an id to a name. The six placeholders are unordered slots. This repository does not implement the tools and does not guess which original id belonged to which name.

| Name in the prompt | What the prompt uses it for | Present in this file |
| --- | --- | --- |
| `query_tool` | Look up services, policies, opening hours, and pricing information before answering. Demonstration prices and draft handbook text must not be stated as fact. | Not defined. Id slot only. |
| `transfer_call` | Emergency calls, and callers who ask for a person, when a transfer destination is configured. | Not defined. Id slot only. |
| `record_enquiry` | After confirmed details on High and Routine calls. The prompt allows a call id, name, telephone, postcode, issue, urgency, and outcome only where the tool schema supports them. | Not defined. The schema is not in this file. |
| `notify_tradesperson` | After a Routine enquiry has been recorded successfully. Not for High or Emergency unless a future workflow explicitly requires it. | Not defined. Id slot only. |
| `log_transfer_failure_to_sheets` | Failed emergency transfers or repeated technical failures, only if the tool's inputs support that log. The prompt says not to describe it as Slack unless a separate Slack integration exists. None is in this file. | Not defined. Id slot only. |
| `end_call` | After a closing sentence, once the caller is ready to finish. The prompt says not to end an unresolved emergency only because a tool failed. | Not defined. Id slot only. |

The two knowledge-file ids were replaced with `YOUR_VAPI_KNOWLEDGE_FILE_ID_1` and `YOUR_VAPI_KNOWLEDGE_FILE_ID_2`. The files themselves are not in the repository. The prompt discusses a demonstration pricing document and a draft handbook. This export does not say which file id, if either, is which document.

Voice ids were replaced:

| Placeholder | Slot |
| --- | --- |
| `YOUR_ELEVENLABS_VOICE_ID` | Primary voice |
| `YOUR_ELEVENLABS_FALLBACK_VOICE_ID_1` | First fallback |
| `YOUR_ELEVENLABS_FALLBACK_VOICE_ID_2` | Second fallback |
| `YOUR_ELEVENLABS_FALLBACK_VOICE_ID_3` | Third fallback |

Provider and model values on those voice objects were left as exported.

## Setup

1. In your own Vapi account, create any of the six tools you actually want. This repository cannot supply their requests or responses.
2. Replace `REPLACE_VAPI_TOOL_ID_1` through `REPLACE_VAPI_TOOL_ID_6` with ids from that account. Leave a slot empty only if you also remove the matching instruction from the prompt. The current prompt tells Sophie to use all six names.
3. Upload the knowledge files you intend to stand behind, and replace the two file-id placeholders. Until you do, `query_tool` has nothing in this repository to read.
4. Choose an ElevenLabs voice and replace the four voice-id placeholders.
5. Import or recreate the assistant from `sophie-assistant.json`.
6. Place a test call only after the tools you kept are configured. Do not describe a transfer, a saved enquiry, or a notification as successful unless the tool result says so. The prompt already says that.

## Illustrative calls

These lines are invented examples of the branches in the prompt. They are not transcripts, and no tool was called.

Emergency, from the prompt's emergency list:

```text
Caller: Water is pouring through the kitchen ceiling right now.
```

The prompt's emergency section says to acknowledge the situation, use verified emergency guidance when it exists, attempt `transfer_call`, tell the caller if the transfer did not connect, and log that failure only when `log_transfer_failure_to_sheets` confirms it. It also says not to promise that a person is on the way. No transfer destination is configured in this file.

Routine:

```text
Caller: The cold tap in the bathroom drips. My name is Sam Taylor.
I am calling from Example Town. Please take my number as 555-0101.
```

The prompt's routine section says to collect and confirm the details, call `record_enquiry` with Routine urgency, then call `notify_tradesperson` when the recording result says it succeeded. Neither tool can be called from this file alone. `555-0101` is a fictional number.

## Test checklist

Not done in this repository.

- [ ] The assistant imports with your voice, file, and tool ids.
- [ ] A routine drip-tap call collects name, number, postcode, and issue without quoting a price.
- [ ] An emergency flooding call attempts transfer only after you have configured a real destination, and the spoken result matches the tool result.
- [ ] A price question uses the unverified-information fallback instead of a figure from a draft document.
- [ ] A tool error is described as a failure and is not retried more than the prompt allows.
- [ ] Removing a tool id also removes or rewrites the prompt section that names that tool.

## Validation limits

- No call recording, transcript, latency figure, or success evaluation is stored here. Both analysis plans are disabled.
- Tool behavior cannot be reviewed from this repository because the tools were not exported.
- The prompt's safety lines are instructions to the model, not a separate policy engine, and they were not evaluated against live calls.
- Knowledge-base answers cannot be checked because the files are not included.
