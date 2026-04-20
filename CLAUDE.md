# SendGrid Bulk Mailer — Project Context for Claude Code

## What this project is

A single-file web app (`sendgrid-mailer.html`) for sending personalised bulk email campaigns via the SendGrid v3 API. No backend, no build tooling — everything runs in the browser.

## Architecture

### Single file: `sendgrid-mailer.html`

All HTML, CSS, and JavaScript lives in one file (~900 lines). External CDN dependencies only:

| Dependency | Version | Purpose |
|---|---|---|
| Quill.js | 1.3.7 | Rich text editor |
| Open Sans | Google Fonts | Typography |

### Key state globals (JS)

```js
let recipients      // array of row objects parsed from CSV
let csvColumns      // array of column header strings (lowercased, underscored)
let quill           // Quill editor instance
let lastCursorIndex // last known Quill cursor position (for chip insertion)
let sendRunning     // bool — campaign in progress
let sendStopped     // bool — user clicked Stop
let sendLog         // array of { ...recipientFields, _status: 'sent'|'failed' }
```

### Data flow

1. User uploads CSV → `parseCSV()` → populates `recipients[]` and `csvColumns[]`
2. `updateVarChips()` renders clickable `{{variable}}` chips from `csvColumns`
3. User composes subject + HTML body with `{{placeholders}}`
4. Preview tab: `interpolate(template, recipient)` replaces placeholders for selected recipient
5. Send: for each recipient, `interpolate()` personalises subject + body, then `sendEmail()` calls `POST https://api.sendgrid.com/v3/mail/send`

### CSV parsing

`parseCSVText()` handles quoted fields, escaped quotes, CRLF/LF. Column headers are normalised: lowercased, spaces→underscores. The `email` column is required; `name` is recommended but optional.

### Template variable insertion

- **Body**: `insertVar(varStr)` inserts at `lastCursorIndex` (tracked via `quill.on('selection-change')`)
- **Subject**: `insertSubjectVar(varStr)` inserts at `selectionStart` in the `<input>`
- Chips use `onmousedown` + `event.preventDefault()` to avoid stealing focus from the editor before insertion

### Sending

`startSend()` iterates recipients, calls `sendEmail()` (fetch to SendGrid), updates a live log table. Batching: pauses `batchDelay` ms every `batchSize` emails. A `sendStopped` flag lets the user abort mid-campaign.

### Config persistence

API key, from-email, and from-name are saved to `localStorage` under key `sg_mailer_config`.

## Design system

Matches the AEMO price viewer project:

- Font: Open Sans (400/500/600/700)
- Primary green: `#5bab44` / dark: `#3d8c2f`
- Background: `#f2f4f6`, Surface: `#ffffff`, Border: `#dde1e7`
- Danger: `#c0392b`, Warning: `#e67e22`, Success: `#27ae60`
- Layout: two-column grid (340px left config panel + fluid right editor panel)

## Key constraints

- **No backend** — all API calls go directly from the browser to `api.sendgrid.com`
- **No build step** — vanilla JS only, no modules, no transpilation
- **Single file** — keep everything in `sendgrid-mailer.html`; do not split into separate JS/CSS files
- **No fabricated data** — never mock or simulate send results; all send attempts must be real API calls

## SendGrid API

Endpoint: `POST https://api.sendgrid.com/v3/mail/send`
Auth: `Authorization: Bearer <api_key>`

Payload shape used:
```json
{
  "personalizations": [{ "to": [{ "email": "...", "name": "..." }] }],
  "from": { "email": "...", "name": "..." },
  "subject": "...",
  "content": [
    { "type": "text/plain", "value": "..." },
    { "type": "text/html",  "value": "..." }
  ]
}
```

A 202 response means accepted. Non-2xx responses include a JSON body with an `errors` array.

## Suggested next features

- Unsubscribe / opt-out list (paste or upload emails to exclude)
- Scheduled send (pick a date/time, use `setInterval` or Page Visibility API)
- SendGrid template ID support (use stored templates instead of composing inline)
- Open/click tracking toggle (SendGrid supports this via `tracking_settings`)
- Test send to a single address before launching the full campaign
- Dark mode
