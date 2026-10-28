# TCoE SKILL.md Regression Selection Demo

## Goal
Demonstrate:
Change Event -> SKILL.md -> AI regression selection -> Tosca/manual execution packs -> human review

## Run
```bash
python -m venv .venv
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Windows:
```powershell
.venv\Scripts\activate
```

Install:
```bash
pip install -r requirements.txt
```

Start:
```bash
streamlit run app.py
```

The app starts in rehearsal mode and requires no AWS connection.

## Live Amazon Bedrock
1. Configure AWS credentials.
2. Grant `bedrock:InvokeModel`.
3. Toggle **Use live Amazon Bedrock**.
4. Enter a supported model or inference-profile ID for your Region/account.

## Demo flow
1. Show change `TR12345`.
2. Open `SKILL.md`.
3. Show the 25-test O2C inventory.
4. Show transparent deterministic pre-score.
5. Click **Analyze change and select tests**.
6. Show risk, selected tests, coverage gap, Tosca pack, manual pack, and human-review gate.
7. Close: **Agent reasons. SKILL.md standardizes. Inventory grounds. Tosca/manual testers execute.**

## Next enhancement
Connect Tosca MCP or Tosca APIs to replace the CSV inventory and add `triage-test-failure/SKILL.md`.
