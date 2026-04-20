# SendGrid Bulk Mailer

A self-contained, single-file web app for sending personalised bulk email campaigns via the [SendGrid API](https://sendgrid.com/). No backend, no build step, no dependencies to install — open the HTML file directly in any modern browser.

---

## Features

- **Rich text editor** — Full formatting toolbar (headings, bold/italic/underline, colour, lists, links, blockquotes) powered by [Quill.js](https://quilljs.com/)
- **CSV recipient upload** — Drag & drop or browse for a CSV; every column header automatically becomes a template variable
- **Personalisation** — Use `{{variable}}` placeholders in the subject and body; click any chip to insert at cursor
- **Live preview** — See exactly how each recipient's personalised email will look before sending
- **Test send** — Send a single personalised email to yourself before launching; choose which recipient's data to use for variable substitution; subject is prefixed with `[TEST]`
- **Duplicate detection** — Warns immediately when a CSV contains duplicate email addresses; one-click deduplication keeps the first occurrence of each address
- **Named campaigns** — Save, reload, and delete campaigns by name; all compose state and CSV data are stored in `localStorage`
- **Auto-draft** — Subject, body, and CSV are silently saved as you type; reloading the page restores exactly where you left off
- **Send history** — Every completed campaign send is logged with per-recipient status, expandable detail view, and CSV export
- **Batch sending** — Configurable batch size and inter-batch delay to respect SendGrid rate limits
- **LocalStorage config** — API key, from-name and from-email persist across sessions

---

## Getting Started

1. Open `sendgrid-mailer.html` in a browser (no server required)
2. Enter your **SendGrid API key** in the left panel and click *Save to localStorage*
3. Set your **From Email** and **From Name** (the sending domain must be verified in SendGrid)
4. Upload a **CSV** of recipients
5. Compose your email in the **Compose** tab
6. Preview personalisation in the **Preview** tab
7. Review the summary and click **Send Campaign**

---

## CSV Format

The CSV must have at least an `email` column. A `name` column is strongly recommended. Any additional columns become available as `{{variable}}` placeholders.

```csv
email,name,company,city
alice@example.com,Alice,Acme Corp,Sydney
bob@example.com,Bob,Widget Co,Melbourne
```

Column headers are lowercased and spaces replaced with underscores when used as variables (e.g. `First Name` → `{{first_name}}`).

---

## Template Variables

In both the **subject line** and **email body**, use `{{column_name}}` syntax:

```
Subject: Hi {{name}}, your order from {{company}} is ready
Body:    Dear {{name}}, we're writing to you in {{city}}…
```

All available variables are shown as clickable chips above the subject and body fields after a CSV is loaded. Clicking a chip inserts it at the current cursor position.

---

## Campaigns

The **Campaigns** panel on the left lets you save the full state of a campaign — subject, body, from details, send settings, and the recipient CSV — under a custom name.

- **Save** — enter a name and click Save (or press Enter)
- **Load** — click any saved campaign to restore everything instantly
- **Delete** — use the bin icon next to a campaign
- **New / Clear** — resets the composer to a blank state

Campaigns are stored in `localStorage` and persist indefinitely.

---

## Send History

The **History** tab records every completed send with:

- Campaign name and subject
- Date and time sent
- Sent / failed counts
- Per-recipient status (expandable)
- Export to CSV per send

---

## Send Settings

| Setting | Description |
|---|---|
| **Batch Size** | Number of emails to send before pausing |
| **Delay (ms)** | Milliseconds to wait between batches |

SendGrid's free tier allows ~100 emails/day. Paid tiers support much higher volumes; adjust batch settings accordingly.

---

## Security Notes

- Your API key is stored only in your browser's `localStorage` — it never leaves your machine except in requests to `api.sendgrid.com`
- Use a SendGrid API key scoped to **Mail Send** only (not a full-access key)
- All email sending goes directly from your browser to `https://api.sendgrid.com/v3/mail/send`

---

## Files

```
sendgrid-mailer.html   — the entire application (HTML + CSS + JS, ~1600 lines)
```

---

## Requirements

- A [SendGrid account](https://sendgrid.com/) with a verified sender identity
- A modern browser (Chrome, Firefox, Edge, Safari)
- No Node.js, Python, or any other runtime needed
