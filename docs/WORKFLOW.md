# Ideas Vault Workflow

This is the canonical method behind `ideas-vault-kit`. Use it manually, through the CLI, or as the structure for the prompt in [prompt.md](prompt.md).

## Goal

When a new idea appears, the workflow should:

1. Confirm the idea in one or two sentences.
2. Research the real market, competitors, constraints, and buyer behavior.
3. Fill a six-file idea folder.
4. Score four pillars out of 10.
5. Apply the market-status modifier.
6. Return GO, PIVOT, or NO-GO with evidence.
7. Update the vault index.

## Process

### 1. Receive the idea

The input can be a short pitch, a social post, a link, a product category, or a rough problem statement. If it is vague, ask up to three clarifying questions before research.

### 2. Create the folder

Use `ivault new "Idea name"` or manually create `NNN-short-slug/`. Keep the slug in English, kebab-case, and no more than six words.

### 3. Research

Collect evidence from public and primary-ish sources when possible. Prefer official docs, pricing pages, industry data, review sites, founder posts, customer forums, and current competitor pages. Avoid AI-generated listicles as primary evidence.

Research these areas:

- Demand signals: search trend, community chatter, "wish someone built X" posts, funding signals.
- Competitors: direct, indie, adjacent substitutes, and big platform threats.
- Niche carve-out: the specific wedge that would let a small builder enter.
- Tooling and compliance: platform policy, regulation, API risk, data access, payment issues.
- Pricing: competitor range, buyer willingness to pay, free-to-paid norms.
- Founder leverage: skill fit, channel fit, budget, time, and energy.

### 4. Classify Market Status

| Status | Signs | Strategy |
|---|---|---|
| blue_ocean | 0-2 competitors, weak complaint volume | Validate demand before building. |
| validated | 3-7 competitors, revenue signals, no dominant winner | Often best. Go narrow and ship better UX. |
| crowded | 10+ competitors, clear demand | Niche carve-out is mandatory. |
| saturated | 50+ competitors, free clones, commodity pricing | Usually skip unless a strong B2B wedge exists. |
| dominated | 1-2 winners own most of the market | Usually skip or serve a tiny ignored use case. |

### 5. Find a Niche Carve-Out

| Angle | Description | Example pattern |
|---|---|---|
| Vertical | Same job, narrower industry | Scheduling for dental clinics |
| Geography | Localized market | Payments or compliance for one country |
| Persona | Smaller target user | Email marketing for solo course creators |
| Price wedge | Similar core value at much lower price | Lightweight alternative to enterprise suite |
| Channel / UX | Different workflow surface | Slack-first or CLI-first version |
| Bundle | Replace multiple tools | Intake + payment + contract in one flow |
| AI-first | AI layer over legacy workflow | Summaries, classification, draft automation |

One-line test:

> X for Y who want Z.

### 6. Fill the Six Files

1. `01-feasibility.md`
2. `02-competition.md`
3. `03-scale-economics.md`
4. `04-founder-fit.md`
5. `05-verdict.md`
6. `README.md`

Each pillar file ends with a 0-10 score and a short reason.

### 7. Score and Decide

Use [scoring.md](scoring.md) as the source of truth:

- GO: adjusted score >=30
- PIVOT: adjusted score 15-29
- NO-GO: adjusted score <15
- Any pillar <=2 triggers the auto-downgrade rule, so the idea can never be GO.

### 8. Shortlist Mode

For "top N ideas" requests, do not create full folders for everything. Create a short comparison table, write about 300 words per idea, score quickly, and recommend one or two ideas for a deep dive.

Ideas can come from your own research, customer conversations, notes, or an LLM-assisted brainstorm. Do not treat the shortlist as final; it is a filter before full evaluation.

## Writing Principles

- No emoji in files.
- Numbers need sources or a "needs verification" note.
- Be specific: "$49/mo competitor" beats "cheap competitor".
- Write both bull case and bear case.
- Kill the idea cleanly when the evidence says to kill it.
- Keep private projects, customer data, credentials, personal handles, and sensitive plans out of public vaults.
