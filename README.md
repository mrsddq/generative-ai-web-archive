# Azure Translator Flask Learning App

A small Flask application that calls Azure Translator. The historical repository name is retained, but this app is an API integration exercise: it does not train or host a generative model.

## Run locally

Python 3.11 is used for the automated checks. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r AI-Web-App/requirements.txt
cd AI-Web-App
cp .env.example .env     # Windows PowerShell: Copy-Item .env.example .env
# Set KEY, ENDPOINT and LOCATION in .env for your Azure Translator resource.
flask --app app run --host 127.0.0.1
```

Open http://127.0.0.1:5000. The form uses the tracked `template/` directory. Real translation requires an Azure resource and can incur service charges; no credentials are included.

## Verify without Azure

From the repository root with the environment active:

```bash
python -m unittest discover -s tests -v
```

The request tests exercise form rendering, translation responses, input rejection, timeouts, missing configuration, malformed provider responses, parameter encoding, and a finite timeout. HTTP calls are mocked. CI runs these checks without secrets or network translation calls.

## Scope and limitations

Input is capped at 5,000 characters and language choices are validated before a request. Provider error details are not shown to the user. This remains a local learning app: it has no authentication, rate limiting, durable audit trail, or deployment operations. Mocked tests do not establish live Azure compatibility or translation quality.

Learning material and existing attribution in the archive are retained. Repository cleanup and tests do not imply ownership of third-party course material. See [the earlier upgrade notes](docs/UPGRADE_PLAN.md) for historical context.
