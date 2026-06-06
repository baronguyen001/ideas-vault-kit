# Provider-Agnostic Idea Evaluation Prompt

Copy this prompt into Claude, Gemini, GPT, or any search-grounded LLM. Replace the bracketed fields with your idea and context.

```text
You are evaluating a side-project idea using a 4-pillar idea-vault framework.

Idea:
[paste the idea, link, claim, or rough problem]

Founder profile:
- Role: [your role]
- Strongest skills: [your strongest skills]
- Weak skills: [your weak skills]
- Network / audience: [your reachable audience]
- Budget / runway: [your budget]
- Weekly hours: [your weekly hours]
- Timezone / languages: [your timezone and languages]

Output language:
[English by default, or choose another language]

Workflow:
1. Confirm your understanding of the idea in 1-2 sentences.
2. If the idea is ambiguous, ask up to 3 clarifying questions before scoring.
3. Research the market using web sources if available.
4. Evaluate these four pillars, each 0-10:
   - Feasibility & Tech
   - Competition & Market
   - Scale & Unit Economics
   - Founder-Fit
5. Classify market_status as one of:
   - blue_ocean
   - validated
   - crowded
   - saturated
   - dominated
6. Apply the market modifier:
   - blue_ocean: -2
   - validated: +2
   - crowded: 0
   - saturated: -3
   - dominated: -5
7. Use these verdict thresholds after the modifier:
   - GO: adjusted score >= 30
   - PIVOT: adjusted score 15-29
   - NO-GO: adjusted score < 15
8. Apply the auto-downgrade rule:
   - If any pillar is <=2, the idea can never be GO.
   - If adjusted score <15, verdict is NO-GO; otherwise PIVOT.
9. Fill the six markdown files below.
10. End with a one-line INDEX.md row.

Required files:

README.md:
- YAML frontmatter:
  title, date, verdict, score, market_status
- TL;DR
- Scoreboard
- Links to the five detail files
- Sources

01-feasibility.md:
- Real build time
- Tech stack
- Platform / legal / data / API blockers
- Bull case and bear case
- Score and reasoning

02-competition.md:
- Demand signals
- Direct competitors with pricing
- Indie / stealth competitors
- Adjacent substitutes
- Market status
- Niche carve-out using vertical, geography, persona, price wedge, channel/UX, bundle, and AI-first angles
- Score and reasoning

03-scale-economics.md:
- Revenue model
- Unit economics
- CAC, LTV, margin, churn assumptions
- Scale ceiling
- Recurring vs one-time revenue
- Score and reasoning

04-founder-fit.md:
- Skill match
- Sales channel match
- Budget and runway
- Time to first revenue
- Energy match
- Score and reasoning

05-verdict.md:
- Final scoreboard
- Verdict
- Main reasoning
- Top 3 risks
- Pivot options
- Next steps if GO
- Kill criteria

Rules:
- Be evidence-driven and specific.
- Cite sources inline.
- If a number is unknown, write "needs verification".
- Include both bull and bear cases.
- Do not invent private context.
- Do not include credentials, personal handles, customer data, or private project names.
- No emoji in markdown files.

INDEX.md row format:
| NNN | Title | score/40 | VERDICT | YYYY-MM-DD | market_status |
```

Works best with a search-grounded model. For Gemini-oriented LLM engineering patterns, see [gemini-agent-toolkit](https://github.com/baronguyen001/gemini-agent-toolkit).
