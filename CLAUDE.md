# SendGrid Bulk Mailer — Project Context for Claude Code

## What this project is

A single-file web app (`sendgrid-mailer.html`) for sending personalised bulk email campaigns via the SendGrid v3 API. No backend, no build tooling — everything runs in the browser.

## Architecture

### Single file: `sendgrid-mailer.html`

All HTML, CSS, and JavaScript lives in one file (~1350 lines). External CDN dependencies only:

| Dependency | Version | Purpose |
|---|---|---|
| Quill.js | 1.3.7 | Rich text editor |
| Open Sans | Google Fonts | Typography |

### Key state globals (JS)

```js
let recipients             // array of row objects parsed from CSV
let csvColumns             // array of column header strings (lowercased, underscored)
let quill                  // Quill editor instance
let lastCursorIndex        // last known Quill cursor position (for chip insertion)
let sendRunning            // bool — campaign in progress
let sendStopped            // bool — user clicked Stop
let sendLog                // array of { ...recipientFields, _status: 'sent'|'failed' }
let currentCampaignId      // id of the currently loaded campaign (null if unsaved)
let currentCampaignCsvText // raw CSV text for the current recipients (saved with campaign)
let draftTimer             // setTimeout handle for debounced auto-draft persistence
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

### Campaigns

`saveCampaign()` / `loadCampaign(id)` / `deleteCampaign(id)` manage named campaign objects stored in `localStorage` under `sg_campaigns` (array). Each campaign stores: name, subject, bodyHtml, fromEmail, fromName, batchSize, batchDelay, csvText (raw), recipientCount, createdAt, updatedAt.

### Auto-draft

`scheduleDraft()` debounces `persistDraft()` by 800ms on every subject input and Quill text-change event. Draft stored under `sg_draft`; `loadDraft()` restores it on page load (including re-parsing the CSV).

### Send history

`saveSendHistory(entry)` appends to `sg_send_history` array after every completed send. Each entry contains: id, sentAt, campaignName, subject, totalRecipients, sent, failed, stopped, log[]. History capped at 20 entries if storage is full. `renderHistoryTab()` builds the History tab UI; `exportHistoryEntry(id)` exports a single entry's log.

### Config persistence

API key, from-email, and from-name are saved to `localStorage` under key `sg_mailer_config`.

## Design system

Matches the AEMO price viewer project:

- Font: Open Sans (400/500/600/700)
- Primary green: `#5bab44` / dark: `#3d8c2f`
- Background: `#f2f4f6`, Surface: `#ffffff`, Border: `#dde1e7`
- Danger: `#c0392b`, Warning: `#e67e22`, Success: `#27ae60`
- Layout: two-column grid (340px left config panel + fluid right editor panel)

## Documentation rule

**Always update README.md when adding or changing features.** Keep the Features list, section descriptions, and file line-count accurate. This must be done in the same commit as the feature change.

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

- **Test send** — send to a single address (e.g. yourself) before launching the full campaign; confirm subject/body look right in a real inbox
- **Opt-out / exclusion list** — paste or upload a list of emails to skip; checked before every send; stored in `localStorage`
- **Duplicate detection** — warn before sending if the same campaign+recipient combination appears in history
- **Inline image support** — drag images into the Quill editor; encode as base64 data URIs or use SendGrid attachments API
- **Reply-to field** — separate reply-to address (common for marketing where sender ≠ reply-to)
- **CC / BCC per send** — static CC/BCC address applied to every email in the campaign
- **SendGrid dynamic template support** — enter a template ID and pass CSV columns as dynamic template data instead of composing inline
- **Open/click tracking toggle** — `tracking_settings` in the SendGrid payload; currently always on by default
- **Scheduled send** — pick a datetime; use `setTimeout` + Page Visibility API to keep the tab alive, or show a "keep this tab open" warning
- **Dark mode** — CSS variable swap; respect `prefers-color-scheme`
- **Attachment support** — attach a file (e.g. PDF) to every outgoing email via SendGrid `attachments` array (base64 encoded)
