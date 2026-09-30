---
name: bithuman-integrate
description: Add a bitHuman real-time talking avatar (Essence 2 or Expression 2) to an app, a website, a Python or LiveKit voice agent, or a terminal. Use when a user asks to integrate bitHuman, render a talking avatar from speech, or choose between on-device, browser, self-hosted and bitHuman cloud rendering.
license: Apache-2.0
---

# Integrate a bitHuman avatar

bitHuman has two current models: Essence 2 renders a photoreal person from one portrait; Expression 2 renders any character (people, animals, cartoons) from one portrait. The docs are at https://docs.bithuman.ai; every page is also markdown at `<url>.md`, and the index is https://docs.bithuman.ai/llms.txt.

If the `bithuman-docs` MCP server is connected (https://docs.bithuman.ai/docs-mcp; read-only, no account, no key), use its `search` tool to find a page and `fetch` to read it, for example `fetch {"id": "/platforms/python"}`. Otherwise read the `.md` URLs below. Cite the docs URL you used in every answer.

## Rules

- From 2026-10-12, API and SDK use requires the Creator plan or higher. Never tell a user they can build on a free plan.
- The API secret is the user's to handle. Never ask the user to paste it into the chat, and never print, echo, log or commit it. Code reads it from the environment (`BITHUMAN_API_SECRET`); never write it into code, a command line, a config file under version control or a commit. If a secret appears in the conversation or a file, tell the user to rotate it at https://www.bithuman.ai/developer/api-keys.
- In a LiveKit worker, the secret is named `BITHUMAN_MASTER_SECRET` and the worker passes a minted token.
- Use two verbs: the avatar **renders** (on the device, in the browser, on your server or in the bitHuman cloud); the conversation **runs** (in the user's own stack, in the CLI's local conversation brain, or on bitHuman's servers).
- Send `model` (`"essence-2"` or `"expression-2"`) when creating an agent, and poll until `status` is `ready` or `failed`.
- Take versions from https://docs.bithuman.ai/versions.json, speed from https://docs.bithuman.ai/performance (× real time, with the device) and prices from https://docs.bithuman.ai/pricing. Do not type them from memory.
- Phones, Macs and browsers stay online: the Swift package, the Android SDK and the web embed check the credential when a session starts. For the offline license, send the user to https://docs.bithuman.ai/deploy/offline.md and promise nothing that page does not say.
- Claim no certification. For data questions, describe where data goes and link https://docs.bithuman.ai/deploy/privacy.md.
- Do not make avatars of real, named people, and do not compare bitHuman with other companies.

## 1. Pick a path

Ask what the user is building, then pick one row.

| The user wants | Use | Where the avatar renders | Docs |
|---|---|---|---|
| An avatar on a website | the web embed (an iframe) | bitHuman cloud, or the tab with WebGPU (`render=local`) | https://docs.bithuman.ai/platforms/web.md |
| An iPhone, iPad or Mac app | the Swift package | on the device (a physical iPhone or iPad) | https://docs.bithuman.ai/platforms/ios.md |
| An Android app | the Android SDK (`essence2-android` / `expression2-android`) | on the device (a physical arm64 phone) | https://docs.bithuman.ai/platforms/android.md |
| A Flutter app on Android | the Flutter plugin | on the device (a physical arm64 phone) | https://docs.bithuman.ai/platforms/flutter.md |
| Python code or a render job | the Python SDK (`bithuman`) | on the machine (macOS on Apple silicon, Linux x86_64/arm64) | https://docs.bithuman.ai/platforms/python.md |
| A face for a LiveKit voice agent | the LiveKit Agents plugin | your server, or the bitHuman cloud | https://docs.bithuman.ai/platforms/livekit.md |
| A terminal, kiosk or quick test | the CLI (`bithuman`) | on the machine (macOS on Apple silicon, Linux x86_64/arm64) | https://docs.bithuman.ai/platforms/cli.md |
| Any backend | the REST API | bitHuman cloud | https://docs.bithuman.ai/platforms/rest.md |

With the web embed, the conversation runs on bitHuman's servers, even when the avatar renders in the tab. Android, and Essence 2 on iPhone and iPad, need a physical device, not an emulator or the Simulator. All modes side by side: https://docs.bithuman.ai/deploy.md.

## 2. Install

Copy the install line from the platform page, with the version from `/versions.json`. Python goes into a virtual environment (`python3 -m venv .venv`). Sample avatars you can try without an account: Essence 2 `sofia-ramirez` and Expression 2 `wise-pup`.

## 3. Wire speech to frames

The Swift and Android SDKs render: the app passes in 16 kHz mono speech from any voice stack and draws the frames, so the persona, the voice and the language model are the user's to choose. The loop is the same on every SDK:

1. Keep one avatar open for the conversation.
2. Feed each audio chunk as it arrives (`feed(chunk)` in Swift and Kotlin, `push_audio(...)` in Python).
3. Show the frames the avatar hands out, on the audio player's clock where the platform offers one.
4. Mark the end of each reply (`flushTail()`, `endOfAudio()`, `flush()`); between replies the avatar keeps moving on idle frames.
5. On barge-in, interrupt the reply (`interrupt()`, `resetState(true)`, `resetAudio()`), then feed the next one.

Each platform's app page names the exact calls: https://docs.bithuman.ai/platforms/swift/app.md, https://docs.bithuman.ai/platforms/android/app.md, https://docs.bithuman.ai/platforms/flutter/app.md, https://docs.bithuman.ai/platforms/web/app.md, https://docs.bithuman.ai/platforms/python/app.md, https://docs.bithuman.ai/platforms/livekit/app.md, https://docs.bithuman.ai/platforms/cli/voice.md. A runnable voice agent: https://docs.bithuman.ai/build/voice-agent.md. A companion app: https://docs.bithuman.ai/build/companion-app.md.

## 4. Handle the secret

The user creates the secret at https://www.bithuman.ai/developer/api-keys (details: https://docs.bithuman.ai/start/api-secret.md) and sets it in their own shell or secret store. Write code and instructions that read it; never fill in its value.

- Local development: the user runs `export BITHUMAN_API_SECRET=...` in their own terminal (the Python SDK and the CLI read it; the CLI also has `bithuman login`). Add `.env` to `.gitignore` if the project keeps one.
- A shipped mobile app holds the secret on the phone: give each app its own secret that can be rotated or revoked, and fetch it from the user's backend at startup rather than compiling it in.
- A website never holds the secret: the embed opens a public or token-scoped agent.
- A LiveKit worker: `BITHUMAN_MASTER_SECRET` in the worker's environment, plus a minted token.

## 5. Check it worked

The avatar appears, moves while idle and its lips follow the speech. Credits pay for active session time, talking or idle, by the exact second; end sessions you are not using. If something fails, read https://docs.bithuman.ai/resources/troubleshooting.md and the platform's troubleshooting page (`/platforms/<platform>/troubleshooting.md`).
