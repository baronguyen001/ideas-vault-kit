# 01 - Feasibility & Tech Difficulty

## Core question

Can a solo builder reliably ship separate iOS apps for local restaurants fast enough to justify a repeatable productized service?

---

## 1.1 Real Build Time

| Step | Claimed time | Realistic time | Notes |
|---|---:|---:|---|
| Generate prototype UI | 30 minutes | 30-90 minutes | AI builders can help here |
| Add menu, branding, photos | Not counted | 2-4 hours | Requires messy customer assets |
| Payment setup | Not counted | 4-8 hours | Merchant/KYC/payment testing |
| Restaurant Apple Developer account | Not counted | 2-7 days | Content provider should submit |
| App Store review | Not counted | 1-3 days | Rejection risk is material |
| Staff onboarding | Not counted | 4-8 hours | Menu updates, order flow, training |
| **Total to usable app** | **30 minutes** | **5-15 business days** | Claim is off by orders of magnitude |

## 1.2 Proposed Tech Stack

- Fastest honest option: responsive ordering page or PWA.
- Native-ish option: React Native or Flutter with a shared template.
- Backend: Supabase/Firebase for auth, DB, storage, and menu data.
- Payments: Stripe, Square, or local payment provider depending on geography.
- Hosting: managed platform plus monitoring.

## 1.3 Bottlenecks / Blockers

### Apple Guideline 4.2.6

Apple says apps created from a commercialized template or app generation service may be rejected unless they are submitted directly by the content provider. For restaurants, that means each restaurant may need to submit under its own developer account.

Consequences:

- The agency cannot safely submit many near-template restaurant apps under one account.
- Each restaurant needs enrollment, payment, ownership, and support.
- The compliant alternative is a multi-restaurant directory or ordering app, which is a different business.

### Operational blockers

- Restaurants need payment setup, menu mapping, staff training, refunds, and updates.
- POS integration with Toast, Square, Clover, or Lightspeed can become the real project.
- App maintenance becomes permanent unless recurring support is priced in.

## 1.4 Bull vs Bear

**Bull case**:

- A web/PWA version can be built quickly and may solve the real need.
- Productized service templates can reduce marginal build time after several customers.

**Bear case**:

- The original iOS app promise runs into App Store policy and customer onboarding reality.
- Selling a web app as an "iOS app" creates trust and refund risk.

---

## Score: 3/10

**Reasoning**:

The technical build is possible, but the original claim is not. App Store policy and restaurant onboarding turn a simple AI prototype into a slow service operation.
