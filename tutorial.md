Tutorial: Run XSSApp locally with a Chrome-trusted HTTPS certificate

Goal
----
Run the `XSSApp` project locally over HTTPS using a certificate the browser (Chrome 85+) will trust. This tutorial uses `mkcert` to create a local CA and issue a certificate for a local hostname. The result: open `https://xssapp.local:8443` in Chrome and see a valid padlock.

Prerequisites
-------------
- macOS (this tutorial targets macOS). 
- Homebrew installed.
- Python virtualenv for the project (you already have `venv`).
- Basic privileges to edit `/etc/hosts` and install a local CA into the macOS Keychain.

Overview of steps
-----------------
1. Pick a local hostname and map it to `127.0.0.1`.
2. Install `mkcert` and create a local CA trusted by macOS (used by Chrome).
3. Create a certificate for your hostname and put cert+key in the project.
4. Start the Flask app with TLS enabled (port 8443).
5. Open `https://xssapp.local:8443` in Chrome and verify the padlock.
6. Troubleshooting and security notes.

Step 1 — Choose hostname and map to localhost
----------------------------------------------
Pick a clear, meaningful name for the local site; here we'll use `xssapp.local`.

Edit `/etc/hosts` (requires sudo) and add the mapping:

```bash
# add to /etc/hosts (one line)
127.0.0.1    xssapp.local
::1          xssapp.local
```

Save the file. This makes `xssapp.local` resolve to your local machine.

Step 2 — Install mkcert and set up a local CA
---------------------------------------------
Install `mkcert` (and `nss` only if you plan to test in Firefox):

```bash
brew install mkcert nss
```

Create and install the local CA into macOS Keychain (mkcert will do the heavy lifting):

```bash
mkcert -install
```

This registers a local CA as trusted by the system and by Chrome.

Step 3 — Generate a certificate for `xssapp.local` (and localhost)
-----------------------------------------------------------------
From the project root (or a `certs/` folder inside the project) run:

```bash
mkdir -p XSSApp-1.0/certs
cd XSSApp-1.0/certs
mkcert xssapp.local localhost 127.0.0.1 ::1
```

This produces two files similar to: `xssapp.local+2.pem` and `xssapp.local+2-key.pem` (mkcert prints exact names). For convenience you can rename them or reference them by name. Example:

```bash
mv xssapp.local+2.pem xssapp.local.pem
mv xssapp.local+2-key.pem xssapp.local-key.pem
```

Important: Do NOT commit private keys to version control. Add the `certs/` directory to `.gitignore`.

Step 4 — Configure the Flask app to use the cert and run on 8443
----------------------------------------------------------------
Open the project file `XSSApp-1.0/XSSApp/app.py` and modify the `start_app()` `app.run(...)` call to use `ssl_context` and port `8443`.

Change the existing line near the bottom from:

```python
    app.run(host="0.0.0.0", port=8000)
```

to something like:

```python
    certfile = os.path.join(os.path.dirname(__file__), "certs", "xssapp.local.pem")
    keyfile = os.path.join(os.path.dirname(__file__), "certs", "xssapp.local-key.pem")
    app.run(host="0.0.0.0", port=8443, ssl_context=(certfile, keyfile))
```

Save the file. (Alternative: run behind a reverse proxy such as Caddy or nginx which handles TLS for you.)

Step 5 — Activate environment and run the app
---------------------------------------------
Activate your virtual environment and run the packaged module from the project root:

```bash
cd /Users/odeddidi/Documents/bar\ ilan/oded\ cs/סייבר/cyber-ex3/XSSApp-1.0
source ../venv/bin/activate      # adjust path to your venv
python -m XSSApp
```

If you changed the port to 8443 and added `ssl_context`, the server will start with TLS on `https://xssapp.local:8443`.

Open Chrome and navigate to:

```
https://xssapp.local:8443
```

Because `mkcert` installed a trusted local CA into your Keychain, Chrome should display a secure padlock and show the certificate chain as trusted.

Step 6 — Verify Chrome 85+ trust and take a screenshot
------------------------------------------------------
1. In Chrome open `https://xssapp.local:8443`.
2. Look for the padlock to the left of the URL. Click it → `Connection is secure` → `Certificate is valid`.
3. Take a screenshot on macOS using `Cmd+Shift+4` and select area, or use DevTools → right-click → `Capture screenshot`.

Save the screenshot and include it with your deliverables.

Troubleshooting
---------------
- If Chrome still shows a certificate error:
  - Make sure the exact hostname in the address bar matches the certificate CN/SAN (i.e., `xssapp.local`).
  - Re-run `mkcert -install` to ensure the CA is in the Keychain.
  - Clear HSTS entries for the domain: open `chrome://net-internals/#hsts` and delete domain.
- If port 8443 is in use, choose another free port and update both `app.run(...)` and the browser URL.
- If Flask refuses to start due to permission errors, ensure your process has permission to read the cert/key files.

Security notes
--------------
- The `mkcert` CA is local to your machine. Do NOT use mkcert certs for public sites.
- Never commit private key files to git. Add the `certs/` folder to `.gitignore`.
- For production/public deployment, use a real CA (Let's Encrypt) and a proper reverse proxy such as Caddy or nginx.

Alternative: use Caddy (recommended for production-like setup)
-------------------------------------------------------------
Caddy can automatically obtain and manage real certificates for public domains. For a local development flow that still demonstrates HTTPS, you can configure Caddy to use the mkcert-generated certs or let Caddy manage TLS when the site is reachable publicly.

Example Caddyfile snippet (useful when exposing site publicly):

```
xssapp.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

Caddy will obtain a certificate automatically if DNS points to your machine and the site is reachable.

What to submit for the assignment
---------------------------------
1. `tutorial.md` (this file)
2. A screenshot showing `https://xssapp.local:8443` with the Chrome padlock and certificate details visible.
3. A short note describing where you put the generated cert/key (e.g., `XSSApp-1.0/certs/`) and a reminder not to commit the keys.

That's it — follow the steps and you will have a Chrome-trusted local HTTPS site running the `XSSApp` project.
