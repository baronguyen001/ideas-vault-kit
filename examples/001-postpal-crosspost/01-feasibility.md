# 01 - Feasibility & Tech Difficulty

## Core question

Can a solo developer ship a markdown-first cross-post scheduler without drowning in platform API edge cases?

---

## 1.1 Real Build Time

| Step | Realistic time | Tools / notes |
|---|---:|---|
| Markdown editor + preview | 3-5 days | CodeMirror or textarea first |
| OAuth for Mastodon + LinkedIn | 4-7 days | Mastodon varies by instance; LinkedIn review can slow down |
| X posting integration | 2-5 days | API pricing and access must be verified before launch |
| Queue + scheduler | 2-3 days | Postgres + background worker |
| Platform-specific transforms | 3-5 days | Thread splitting, link cards, character counts |
| Billing + plans | 2-3 days | Stripe Checkout |
| Deployment + monitoring | 1-2 days | Render/Fly/Railway + cron/worker |
| **Total to first real customer** | **3-5 weeks** | Feasible if X scope is validated early |

## 1.2 Proposed Tech Stack

- Frontend: Next.js or simple server-rendered app with a markdown editor.
- Backend: Python FastAPI or Node/Next API routes.
- Queue: Postgres + worker, or managed queue if volume grows.
- Hosting: Render, Fly.io, Railway, or similar.
- Billing: Stripe Checkout.
- Minimum monthly cost: about $30-80 before scale.

## 1.3 Bottlenecks / Blockers

- X API access and pricing can change; validate before coding around it.
- LinkedIn permissions and review can create launch friction.
- Cross-posting must respect platform terms and rate limits.
- Rich media upload increases scope; MVP should start with text + links.

## 1.4 Bull vs Bear

**Bull case**:

- This is mostly CRUD, OAuth, scheduling, and text transformation.
- Markdown-first scope avoids building a full social media command center.
- Mastodon is open and LinkedIn is documented enough for a narrow MVP.

**Bear case**:

- API policy changes can break the product.
- Users expect reliability and exact preview behavior across platforms.
- X access may make the low-price plan hard to sustain.

---

## Score: 8/10

**Reasoning**:

The build is realistic for one person if the MVP starts with text, links, markdown preview, and a small number of platforms. The biggest risk is platform API access, not core engineering.
