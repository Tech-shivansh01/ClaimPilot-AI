# ClaimPilot AI

An AI-assisted motor insurance claims platform I built to learn how to put together an actual agentic pipeline instead of just calling one LLM API. The idea: instead of a human adjuster manually going through accident photos + FIR + medical reports + repair estimates one by one, a chain of AI agents does the first pass, and only the risky/uncertain claims need to go to a human.

This was built as a personal/college project, not a production system — see the "what's real vs simplified" section below for an honest breakdown.

## What it does

1. You file a claim with your policy number, incident details, and upload accident photos + supporting docs (FIR, medical report, repair estimate)
2. The backend runs the claim through 5 agents, one after another:
   - **Vision agent** — looks at the accident photos, estimates damage severity + affected parts + repair cost (GPT-4o Vision)
   - **Document agent** — OCRs the uploaded documents and pulls out structured fields like policy number, vehicle number, amounts (Tesseract OCR + LLM)
   - **Fraud agent** — checks for tampered images, location mismatches, duplicate claims, and runs an anomaly detection model over the claim's features
   - **Settlement agent** — calculates the payout based on policy coverage, deductible, and the fraud risk
   - **Compliance agent** — writes a plain-English explanation for why the claim was approved/rejected/sent for review
3. You get the full breakdown on the claim detail page

## Tech stack

- **Frontend:** Next.js (App Router, plain JS, no TypeScript)
- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Agent orchestration:** LangGraph
- **LLM:** OpenAI GPT-4o / GPT-4o-mini
- **Vector DB:** Weaviate (for the duplicate-claim similarity check)
- **Fraud model:** scikit-learn IsolationForest
- **Deployment:** Docker 

## What's real vs. simplified

Being upfront about this since I'd rather explain it myself than have someone assume it's all production-grade:

| Feature | What the "ideal" version would be | What I actually built |
|---|---|---|
| Damage detection | Florence-2 / Grounding DINO / SAM2 segmentation | GPT-4o Vision — needs an API key, not a GPU, way more realistic for a solo project |
| Document parsing | Docling / LayoutLM / Nougat | Tesseract OCR + LLM extraction |
| Fraud detection | Graph Neural Network over a claims/policy/garage graph | Rule-based checks (EXIF tamper flag, location mismatch, duplicate-claim vector search) + IsolationForest anomaly scoring. A real GNN needs a labeled historical fraud dataset that doesn't exist here, so I didn't fake it |
| Deployment | Kubernetes | Docker + docker-compose, runs fine on a single AWS EC2 instance |

The app also has a **mock mode** — if you don't set an `OPENAI_API_KEY`, every agent still runs and returns placeholder-but-realistic results, so you can demo the whole flow without spending anything on API calls.

## Project structure

```
claimpilot-ai/
├── backend/
│   ├── app/
│   │   ├── agents/        # vision, document, fraud, settlement, compliance + langgraph pipeline
│   │   ├── routers/        # claims.py, policies.py
│   │   ├── services/        # llm wrapper, vector store, file storage
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py        # pydantic schemas
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                # home, dashboard, submit-claim, claim/[id]
│   ├── components/
│   └── lib/api.js
└── docker-compose.yml
```

## Running it locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # optionally add your OPENAI_API_KEY here
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`. Two demo policies (`POL1001`, `POL1002`) get seeded automatically on first run.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend runs on `http://localhost:3000`.

### Optional: Weaviate (for the duplicate-claim check)

```bash
docker-compose up weaviate
```

If you skip this, the duplicate-claim check just runs against an in-memory list instead — still works, just doesn't persist between restarts.

### Or run everything with Docker

```bash
docker-compose up --build
```
(frontend still needs to be run separately with `npm run dev`, see note in `docker-compose.yml`)

## API quick reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/claims` | create a new claim |
| POST | `/claims/{id}/documents` | upload a photo/FIR/medical report/repair estimate |
| POST | `/claims/{id}/process` | run the claim through the agent pipeline |
| GET | `/claims` | list all claims |
| GET | `/claims/{id}` | get full claim detail + AI results |
| GET | `/policies/{policy_number}` | look up a policy |

Interactive docs available at `http://localhost:8000/docs` once the backend is running.

## Future improvements

- Actually fine-tune a small GNN on a public synthetic fraud dataset instead of IsolationForest
- Video frame extraction for accident videos (currently just stored, not analyzed)
- Proper auth instead of trusting whatever policy number is typed in
- Switch SQLite → Postgres for anything beyond a demo
- Add a basic admin view for adjusters to review the `manual_review` queue
