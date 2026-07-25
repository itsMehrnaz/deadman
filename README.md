# deadman

A small Linux daemon that automatically shuts down your laptop shortly before a **scheduled power outage** in your area, so an abrupt power loss never catches you off guard.

Built for Iran's electricity distribution network (SAAPA / *Bargh-e-Man*), where planned outages are published per billing account. The tool reads your outage schedule directly from the provider's API, watches the clock, and powers the machine down a few minutes before the lights go out — after giving you a heads-up notification.

## Why

In many parts of Iran, planned power cuts are announced in advance but happen abruptly. An unclean shutdown risks data loss and, over time, wear on the hardware. `deadman` turns that announced schedule into an automatic, graceful shutdown so you're never surprised mid-work.

## How it works

The tool runs as a background service and repeats a simple loop:

1. **Fetch** the planned-outage schedule for your billing account from the provider API.
2. **Filter** the results down to outages at *your* address (matched by an address keyword).
3. **Watch the clock** — every minute it checks how many minutes remain until the next outage that is scheduled for *today*.
4. **Warn, then shut down** — it sends a desktop notification when an outage is close, and powers the machine off a few minutes before the outage begins.

The outage schedule is refreshed periodically (once an hour by default) rather than every minute, to avoid hammering the provider's server.

## Requirements

- Linux with `systemd` (tested on Ubuntu / GNOME)
- Python 3.10+
- A billing account (`bill_id`) registered with the SAAPA / Bargh-e-Man service
- Network access to the provider API from inside Iran (no proxy/VPN needed — the tool bypasses the system proxy)

Python dependencies:

- `requests`
- `jdatetime`

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/itsMehrnaz/deadman.git
cd deadman

python3 -m venv venv
source venv/bin/activate
pip install requests jdatetime
```

## Configuration

Before running, you need two things: your **billing ID** and an **authorization token**. Both are read from the provider's own website.

### 1. Get your billing ID and token

1. Log in to your account at [bargheman.com](https://bargheman.com).
2. Open the browser developer tools (`F12`) and go to the **Network** tab.
3. Filter by **Fetch/XHR**, then trigger a planned-outage lookup on the site.
4. Find the request to `PlannedBlackoutsReport` and inspect it:
   - The **Payload** contains your `bill_id`.
   - The **Request Headers** contain an `Authorization: Bearer …` value — this is your token.

### 2. Set your values

Open `main.py` and set the following near the top of the file:

| Variable  | Meaning                                              |
|-----------|------------------------------------------------------|
| `TOKEN`   | The `Bearer` token copied from the request headers   |
| `KEYWORD` | A distinctive part of your address, exactly as it appears in the outage data (e.g. `"مطهری"`) |
| `bill_id` | Your billing account ID (passed into `get_outages`)  |

> **Note on the address keyword:** match it exactly against the `outage_address` field returned by the API, including digit style. Persian and English digits are *not* interchangeable — `"10"` and `"۱۰"` are different strings.

### Security note

The `Authorization` token is a personal credential tied to your account. **Do not commit your real token to a public repository.** For a public setup, move the token into a separate, git-ignored file (for example a `.env` file or a local `config.py`) and load it at runtime. A committed token can be used by anyone to query your account's data.

The token is a JWT with a built-in expiry date; when it eventually expires, repeat the steps above to obtain a fresh one.

## Usage

### Run manually (for testing)

```bash
source venv/bin/activate
python main.py
```

While testing, keep the shutdown command commented out and rely on the log output to confirm the timing logic behaves correctly before letting it power the machine off for real.

### Run automatically at login (recommended)

Install it as a `systemd` **user service** so it starts on its own after login.

1. Create the service file at `~/.config/systemd/user/deadman.service`:

```ini
[Unit]
Description=Deadman power outage auto-shutdown
After=network-online.target

[Service]
ExecStart=/home/YOUR_USER/deadman/venv/bin/python /home/YOUR_USER/deadman/main.py
Restart=on-failure
RestartSec=30

[Install]
WantedBy=default.target
```

Replace the paths in `ExecStart` with the real paths to your virtual environment's Python and to `main.py`.

2. Enable and start it:

```bash
systemctl --user daemon-reload
systemctl --user enable --now deadman.service
```

3. Check that it's running:

```bash
systemctl --user status deadman.service
```

Look for `active (running)`.

4. Follow the live logs:

```bash
journalctl --user -u deadman.service -f
```

You should see a periodic `still working` message confirming the loop is alive.

To keep the service running even before you log in graphically, enable lingering:

```bash
sudo loginctl enable-linger YOUR_USER
```

## Shutdown behaviour

The tool uses `systemctl poweroff -i` to power off. The `-i` flag ignores desktop *inhibitors* (the soft locks a graphical session places to prevent abrupt shutdowns), which is what allows an automated shutdown to proceed. It runs without `sudo` on a typical desktop session.

A desktop notification is sent a few minutes ahead of the shutdown as a warning to save your work. If notifications don't appear when running under the systemd service, the service may need access to your session's D-Bus address; add an `Environment=DBUS_SESSION_BUS_ADDRESS=…` line to the `[Service]` section.

## Configurable values

You can adjust these in `main.py` to change the behaviour:

- **Warning / shutdown windows** — how many minutes before an outage the warning is sent and the shutdown fires.
- **Refresh interval** — how often the outage schedule is re-fetched from the server.
- **Date range** — how many days ahead of today the schedule is requested. Note that the provider may return outages slightly beyond the requested end date; the per-day filter in the code is what ultimately decides when to act.

## Limitations

- Built specifically for the SAAPA / Bargh-e-Man API; other providers use different endpoints and data formats.
- Address matching is keyword-based. Choose a keyword specific enough to avoid matching a neighbouring street.
- The API may return duplicate or slightly out-of-range entries; the code tolerates this but does not deduplicate.
- The auth token must be refreshed manually once it expires.

## Disclaimer

This tool powers off your machine automatically. Test the timing logic thoroughly with the shutdown command disabled before enabling it for real, and always save your work — the shutdown can occur without further confirmation.

## License

MIT
