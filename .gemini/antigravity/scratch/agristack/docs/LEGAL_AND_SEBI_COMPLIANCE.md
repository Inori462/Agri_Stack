# AgriStack: Legal & Regulatory Compliance Framework
**Pilot & Sandbox Environment Notice**

---

## 1. Regulatory Context

In India and many jurisdictions, fractional digital ownership and public pooling of capital for agricultural yields touch upon critical legal domains:

1. **SEBI (Collective Investment Schemes) Regulations, 1999**:
   - Any scheme where contributions or payments made by investors are pooled and utilized for the purposes of the scheme or arrangement to receive profits, produce, or income can potentially be deemed a Collective Investment Scheme (CIS).
   - Under Section 11AA of the SEBI Act, 1992, unauthorized CIS activities carry strict prohibitions.
2. **Agricultural Land Ceiling & Tenancy Laws**:
   - In states like Maharashtra (Maharashtra Tenancy and Agricultural Lands Act), non-farmers are generally restricted from holding title to agricultural land.
   - **AgriStack Model:** Investors do **not** acquire title or deed to the physical land. The underlying land remains 100% in the title and possession of the verified farmer. The digital shares represent contractual fractional profit-participation agreements in the **operational crop yield cycle** (operational revenue rights), not real estate ownership.
3. **Data Protection & Privacy (DPDP Act 2023 & UIDAI Guidelines)**:
   - Full 12-digit Aadhaar numbers must never be stored in plain text.
   - DigiLocker paperless e-KYC or masked Aadhaar tokens (last 4 digits only) with irreversible cryptographic HMAC hashes for duplicate detection must be strictly enforced.

---

## 2. Platform Sandbox & Pilot Safeguards

To ensure full compliance during testing, validation, and pilot rollout:

1. **Default Sandbox / Pilot Mode**:
   - AgriStack operates in pilot/sandbox mode by default.
   - Real payment gateways (Razorpay) run in test mode with test API credentials.
   - Project sizes and participation caps are strictly limited (e.g., maximum 100 shares per project, capped investor participation limits).
2. **Explicit Consent & Risk Disclosure**:
   - Prior to participating in any project, investors must digitally sign a statutory acknowledgement that:
     - Agricultural operations carry inherent climate, monsoon, pest, and market volatility risks.
     - Investment shares are not guaranteed fixed-income securities.
     - The project is a fractional participation pilot contract under sandbox governance.
3. **Escrow Milestones & Loss Mitigation**:
   - Investor capital is disbursed incrementally (40% sowing -> 40% mid-cycle growth -> 20% harvest) to prevent capital misappropriation.
   - In the event of crop loss, government insurance payouts (e.g., PMFBY) are applied to the settlement pool prior to final loss distribution.

---

## 3. Recommended Actions Prior to Commercial Launch

Before transitioning from sandbox to full public deployment:
1. Formal application to the **SEBI Regulatory Sandbox** or **RBI / NABARD Innovation Hub**.
2. Legal validation of the standard Farmer-Investor Profit Participation Agreement by an agricultural and securities law counsel.
3. Tie-ups with certified Primary Agricultural Credit Societies (PACS) and Farmer Producer Organizations (FPOs).
