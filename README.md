# SendGrid Bulk Mailer

A self-contained, single-file web app for sending personalised bulk email campaigns via the [SendGrid API](https://sendgrid.com/). No backend, no build step, no dependencies to install — open the HTML file directly in any modern browser.

---

## Features

- **Rich text editor** — Full formatting toolbar (headings, bold/italic/underline, colour, lists, links, blockquotes) powered by [Quill.js](https://quilljs.com/)
- **CSV recipient upload** — Drag & drop or browse for a CSV; every column header automatically becomes a template variable
- **Personalisation** — Use `{{variable}}` placeholders in the subject and body; click any chip to insert at cursor
- **Live preview** — See exactly how each recipient's personalised email will look before sending
- **Attachments** — Attach one or more files to every outgoing email; drag & drop or browse; shows a size bar with a 30 MB SendGrid limit warning
- **Test send** — Send a single personalised email to yourself before launching; choose which recipient's data to use for variable substitution; subject is prefixed with `[TEST]`
- **Duplicate detection** — Warns immediately when a CSV contains duplicate email addresses; one-click deduplication keeps the first occurrence of each address
- **Export / Import** — Export all campaigns, history, and config to a single `.json` file; import on another device or share via SharePoint; merges with existing data rather than overwriting
- **Named campaigns** — Save, reload, and delete campaigns by name; all compose state and CSV data are stored in `localStorage`
- **Auto-draft** — Subject, body, and CSV are silently saved as you type; reloading the page restores exactly where you left off
- **Send history** — Every completed campaign send is logged with per-recipient status, expandable detail view, and CSV export
- **Batch sending** — Configurable batch size and inter-batch delay to respect SendGrid rate limits
- **LocalStorage config** — API key, from-name and from-email persist across sessions
- **Holiday Alert tab** — Cross-references people, buildings, and exportUsers CSVs to compute who needs a public holiday warning email; built-in 2025–2026 Australian public holiday schedule; recipient list with per-person enable/disable checkboxes; loads directly into the mailer as the campaign recipient list with variables `{{first_name}}`, `{{buildings}}`, `{{holiday}}`, etc.

---

## Getting Started

> **Important:** Browsers block API calls from files opened directly (`file://`). You must run the included local server.

1. Start the local server:
   ```bash
   python mailer_server.py
   ```
2. Open **http://localhost:8766** in your browser
3. Enter your **SendGrid API key** in the left panel and click *Save to localStorage*
4. Set your **From Email** and **From Name** (the sending domain must be verified in SendGrid)
5. Upload a **CSV** of recipients
6. Compose your email in the **Compose** tab
7. Preview personalisation in the **Preview** tab
8. Review the summary and click **Send Campaign**

The server has no dependencies beyond Python's standard library — no `pip install` needed.

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

## Data Storage

When running via `mailer_server.py` (the recommended way), all data is saved to local JSON files in `mailer_data/` next to the server:

| File | Contents |
|---|---|
| `mailer_data/config.json` | API key, from email/name, reply-to, BCC |
| `mailer_data/campaigns.json` | All saved campaigns |
| `mailer_data/history.json` | Send history |
| `mailer_data/draft.json` | Auto-saved draft |

Data loads automatically when you open the app and saves instantly as you work. If you place the project folder in a **OneDrive or SharePoint-synced folder**, all data is shared across devices automatically — no manual export/import needed.

When opened directly as `file://` (not via the server), the app falls back to the browser's `localStorage`.

## Sharing Campaigns Across Devices

**Recommended:** Put the project folder in a SharePoint/OneDrive-synced location. The `mailer_data/` folder syncs automatically.

**Alternative (manual):** Use the Export / Import panel to copy data between machines:

1. Click **Export all data (.json)** in the Data Export / Import panel
2. Save the exported file to SharePoint (or any shared folder)
3. On the other device, open the HTML file and click **Import from .json file**
4. Select the exported file — campaigns, history, and config are merged in (existing data is kept)

---

## Send Settings

| Setting | Description |
|---|---|
| **Batch Size** | Number of emails to send before pausing |
| **Delay (ms)** | Milliseconds to wait between batches |

SendGrid's free tier allows ~100 emails/day. Paid tiers support much higher volumes; adjust batch settings accordingly.

---

## Security Notes

- Your API key is saved in `mailer_data/config.json` (local file, never transmitted except in requests to `api.sendgrid.com`)
- Use a SendGrid API key scoped to **Mail Send** only (not a full-access key)
- All email sending goes directly from your browser to `https://api.sendgrid.com/v3/mail/send`

---

## Files

```
sendgrid-mailer.html   — the entire application (HTML + CSS + JS, ~1860 lines)
mailer_server.py       — local Python proxy server (stdlib only, no pip installs)
```

---

## Requirements

- A [SendGrid account](https://sendgrid.com/) with a verified sender identity
- A modern browser (Chrome, Firefox, Edge, Safari)
- No Node.js, Python, or any other runtime needed



add a new "tab" to this project. It will be a tool to send out emails to users who have buildings in particular states as a warning when public holidays are approaching so they can ensure their building will shut down and save energy.  
- Use the excel spreadsheet as example
INPUTS:
- people.csv - list of all people
- buildings.csv - list of all buildings
- exportUsers.csv - a list t of people and which buildings they can see
- do not send list.csv - a list of emails addresses NOT to send emails to
- public holidays
- 

The tool should cross reference these spreadsheets to work out which users to send emaisl to:
- Users that are:
  - Enabled is True
  - Role is Super or User
  - Only users who can see buildings in the state where the public holiday applies

- The tool should generate a list of people to send the email to, but allow the users of this html file to disable any users they do not want to send emails to
- The list of users should contain their email address, name, first name, buildings that they can see





