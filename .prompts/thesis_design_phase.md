You are acting as an expert agentic Architect and AI Engineer. Review my centralized codebase documentation in `@ARCHITECTURE.md` [and tag any other relevant files, e.g., `@scheduler.py`, `@news_tool.py`]. Explain it to someone who’s an analyst who is learning about agents ( so not a software engineer) 

### Current State
* The `yfinance` API and `Scheduler` are fully functional and detecting market anomalies on a set cadence.
* The news retrieval tool is working and ready to be integrated.

### Goal
I need to implement the next phase of the project: **Sequential Thesis Generation**. Help me map out the exact technical implementation, architecture, and data flow based on our existing constraints and goals.

Please provide a detailed, production-grade architectural breakdown covering the following areas:

1. **The Step-by-Step Execution Plan:** Remind me of our overarching plan for this phase and how it integrates with the scheduler and news tool.
2. **Sequential Processing Pipeline:** Explain exactly how we will process multiple detected anomalies sequentially to prevent mixup of different tickers and theses, over flowing the llm and API rate-limiting.
3. **Thesis Generation Logic & LLM Inputs:** Detail how the LLM will evaluate if an anomaly is a "fundamental shift" vs. a "scare situation." Specify the exact input schema required (e.g., asset ticker, price delta, timestamp, anomaly flag, and the retrieved news payloads). Reflect - is this where the agent really is doing reflection? decideing whether to escalate and use more tools - which tools? Analyst opinion ? SEC filings ?  Suggest these only if necessary. Should these be implemented later and not in this version?
4. **Implementation Blueprint:** Look at my existing prompt logic [optionally tag `@prompt_template.txt` or paste your example prompt here] and explain how this is implemented within our file structure.
5. **Output Schema:** Define a clean, structured JSON output format for the final generated thesis so it can be reliably parsed by downstream services.

Do not write placeholders or generic advice. Align this entirely with the modular, file-driven architecture standards established in our `ARCHITECTURE.md` and other files