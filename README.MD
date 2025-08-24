# Tanzanian African Art Ecommerce — Feature Blueprint & System Architecture

*Audience:* Founder + Engineering lead  
*Focus:* Vinyago (Makonde carvings), paintings, Maasai jewelry, fabrics  
*Goals:* Celebrate provenance, enable local & global payments, provide immersive shopping (360°/AR), and support artist livelihoods with fair payouts.

---

## 1) MVP Scope (12–16 weeks)
**Buyer:** browse, search, filter, view 3D/AR, add to cart, checkout (M‑Pesa/Airtel/Tigo + PayPal/Stripe), order tracking.  
**Artist:** onboarding (KYC-lite), create product, inventory, pricing, shipping profile, see sales, request payout.  
**Trust:** artist story + artwork meaning, certificate of authenticity (QR), reviews.  
**Ops:** back-office moderation, order management, refunds, payouts, shipping labels (Posta/DHL).  
**Content:** collections (Makonde, Tinga‑Tinga, Zanzibar Doors), blog/cultural notes.

---

## 2) High-Level Architecture
```
[Web (Nuxt/Vue)]  [Mobile (Flutter - later)]
          │
          ▼
   API Gateway / BFF (Django DRF)
          │
 ┌────────┴────────────────────────────────────────────────────────────────┐
 │ Modular Monolith services (Django apps):                                │
 │  • Auth & Profiles      • Catalog & Media      • Orders & Checkout      │
 │  • Artists & Payouts    • Payments             • Shipping/Fulfillment   │
 │  • Reviews & Ratings    • Certificates         • CMS/Collections        │
 │  • Search (Meilisearch) • Notifications        • Analytics              │
 └────────┬────────────────────────────────────────────────────────────────┘
          │           │            │            │             │
          ▼           ▼            ▼            ▼             ▼
     PostgreSQL     Redis     Object Store   Message Bus   Meilisearch
                    (cache)   (R2/S3)        (Celery)      (full‑text)
          │                        │             │             │
          ▼                        ▼             ▼             ▼
   Back-office (Next.js/Django Admin)   Media CDN   Workers (ETL, image/3D, emails)
```

**Why Modular Monolith?** Fast to build & iterate; clear boundaries. Later, peel off heavy modules (search, media, certificates) into microservices if needed.

---

## 3) Key Components & Responsibilities
- **Frontend (Nuxt 3 + Vue):** SSR for SEO; localized content; `<model-viewer>` for 3D/AR (GLB/USDZ); lazy image/video; shimmers; accessible UI.
- **Backend (Django + DRF):** BFF layer, validation, rate limits, serialization; Django Admin for ops.
- **Database (PostgreSQL):** ACID core data; JSONB for flexible attributes (materials, tribe, motif).
- **Search (Meilisearch or OpenSearch):** Typo‑tolerant search, facets (tribe, region, material, size, price, artist).
- **Cache & Queue:** Redis for cache/sessions; Celery workers for thumbnails, 3D processing, emails, payouts, webhook handlers.
- **Object Storage & CDN:** Cloudflare R2/S3 + Cloudflare CDN for images/video/GLB/USdz; signed URLs.
- **Payments:** Local (DPO/Selcom/PesaPal → M‑Pesa, Airtel Money, Tigo Pesa, bank); International (Stripe/PayPal/Wise). Webhooks to capture payment status.
- **Shipping:** Posta/EMS Tanzania + DHL/Aramex. Live rate quote tables; label creation; tracking webhooks.
- **Notifications:** Email (Mailgun/SES), SMS (InfoBip/Hubtel), WhatsApp (Cloud API) for order updates.
- **Certificates Service:** Generate QR‑linked digital certificate PDF; optional on‑chain token (Polygon) for premium pieces; anti‑fraud watermarking.
- **Analytics:** Events pipeline (PostHog/Segment), product & funnel analytics; artist dashboard KPIs.

---

## 4) Data Model (Core Entities)
**User(id, name, email, phone, role[buyer,artist,admin], locale, created_at)**  
**Artist(id, user_id, display_name, bio, tribe, region, socials, kyc_status)**  
**Address(id, user_id, type[billing,shipping], line1..country, latlng)**  
**Artwork(id, artist_id, title, slug, story, meaning, category, tribe, material, dimensions, weight, price, currency, stock, status, tags[], attributes JSONB)**  
**Media(id, artwork_id, kind[image,video,glb,usdz], url, alt, meta)**  
**Collection(id, title, description, cover_media_id, sort_order)**  
**Cart(id, user_id, currency)**  
**CartItem(id, cart_id, artwork_id, qty, unit_price, snapshot JSONB)**  
**Order(id, user_id, status, total, currency, shipping_cost, taxes, shipping_address_id, payment_id)**  
**OrderItem(id, order_id, artwork_id, qty, unit_price, tax_rate, snapshot JSONB)**  
**Payment(id, provider, provider_ref, amount, currency, status, method, meta)**  
**Payout(id, artist_id, amount, currency, status, provider, provider_ref)**  
**Shipment(id, order_id, carrier, tracking_no, label_url, status, events JSONB)**  
**Review(id, user_id, artwork_id, rating, comment, images[])**  
**Certificate(id, artwork_id, serial, pdf_url, qr_url, onchain_tx?, issued_at)**  
**Workshop(id, artist_id, title, price, schedule, location, capacity)** *(phase 2)*

Indexes: `Artwork(title, tags, tribe, material)`, `Order(user_id, created_at)`, `Payment(provider_ref)`; search index mirrors core artwork fields.

---

## 5) API (Illustrative)
**Auth**  
- `POST /auth/register`, `POST /auth/login` (JWT); `POST /auth/refresh`; `POST /auth/social/{provider}`

**Catalog**  
- `GET /artworks?query=&tribe=&region=&material=&price_min=&price_max=&sort=`  
- `GET /artworks/{slug}` includes media, artist, availability, AR assets  
- `GET /collections` / `GET /collections/{id}`

**Cart & Checkout**  
- `POST /cart/items` (artwork_id, qty) / `PATCH /cart/items/{id}` / `DELETE`  
- `POST /checkout` → creates `Order` + client_secret/redirect for provider  
- `POST /payments/webhook/{provider}` (idempotent)

**Artist**  
- `GET /me/artist`, `POST /me/artist` (onboarding, KYC)  
- `POST /me/artworks`, `PATCH /me/artworks/{id}`  
- `GET /me/payouts`, `POST /me/payouts` (request)

**Ops**  
- `POST /admin/moderate/artworks/{id}`  
- `POST /admin/orders/{id}/refund`  
- `POST /admin/shipments/{id}/create-label`

**Certificates**  
- `POST /certificates/{artwork_id}` issues PDF + QR  
- `GET /certificates/verify/{serial}` public verification page  
- `POST /certificates/{id}/mint` *(optional, premium tier)*

---

## 6) Unique Differentiators (Product)
1) **Provenance-first PDP:** prominent artist bio + tribe + meaning + map of origin.  
2) **360°/AR for vinyago:** GLB+USDZ assets; on-page `<model-viewer>` with room-scale AR on mobile.  
3) **Local + global payments unified:** M‑Pesa/Airtel/Tigo + Stripe/PayPal in one checkout.  
4) **QR certificates:** scannable provenance; anti-tamper watermark; optional blockchain mint.  
5) **Artist mini‑shops:** vanity URLs, tip jar, workshop bookings (phase 2).  
6) **Tourist flow:** buy online → pickup at airport/partner gallery or ship home tax‑friendly.  
7) **Cultural curation:** collections by motif/tribe/region; editorial content boosts SEO.

---

## 7) User Flows (Sequence Summaries)
**Checkout (local wallet):**  
Buyer → Add to cart → Address/rates → Choose M‑Pesa → Create PaymentIntent → STK push → Webhook confirms → Create Shipment label → Notify buyer & artist.

**Artist onboarding:**  
Sign up → Artist profile (ID photo, bank/mobile wallet) → Submit first artwork → Moderation queue → Live → Sales dashboard.

**Certificate issuance:**  
Order paid → Worker generates PDF (ReportLab) + QR (serial verify URL) → Upload to R2 → Email/SMS link to buyer.

**AR asset pipeline:**  
Artist uploads photos → Worker (Blender/headless) and/or photogrammetry pipeline creates GLB + USDZ → store & attach to artwork.

---

## 8) Tech Choices & Libraries
- **Frontend**: Nuxt 3, Vue 3, Pinia, VueUse, `<model-viewer>`, Vite, Tailwind, i18n.  
- **Backend**: Django 5, DRF, Django Admin + custom Ops UI, Celery, Redis, drf-spectacular (OpenAPI).  
- **Payments**: DPO/Selcom/PesaPal (TZ wallets), Stripe/PayPal (intl).  
- **Search**: Meilisearch (managed or self-hosted).  
- **Storage/CDN**: Cloudflare R2 + CDN; image thumbnails via Thumbor/ImgProxy.  
- **3D/AR**: Google Model‑Viewer, Blender (CLI), OpenExif/ExifTool, optional Polycam/RealityCapture pipeline.  
- **Comms**: Mailgun/SES, WhatsApp Cloud API, SMS (Infobip).  
- **Analytics**: PostHog (self-host possible) or Plausible + server events.

---

## 9) DevOps & Deployment
- **Runtime**: Dockerized services (web, worker, search, db, cache).  
- **Web**: Nginx → Gunicorn (Django) with HTTP/2; Cloudflare in front (WAF, CDN).  
- **CI/CD**: GitHub Actions (tests, migrations, container build, deploy); environments: Dev/Staging/Prod.  
- **IaC**: Terraform (R2 buckets, secrets, DB, Meilisearch).  
- **Monitoring**: Sentry (BE/FE), Prometheus + Grafana, UptimeRobot.  
- **Backups**: Nightly DB snapshots; object lifecycle rules.

**Scaling:** Horizontal app autoscale; Redis caching; search read‑replicas; media via CDN; eventual microservices for Search/Certificates if needed.

**Security:** JWT + refresh tokens, OAuth (Google/Apple); strict media validation, size limits; object store signed URLs; webhook signature verification; RBAC; audit logs; rate limiting.

---

## 10) Shipping & Taxes (TZ + Intl)
- **Carriers:** Posta/EMS, DHL, Aramex.  
- **Rates:** rule table by weight/size + zone; optional carrier API quotes.  
- **Duties/Taxes:** show landed cost estimates for intl; HS codes per category; provide COA/Certificate of Origin where relevant.

---

## 11) Back‑Office (Ops)
- Moderation queue (new artworks, edits).  
- Orders list with timeline & notes; partial refunds; re‑ship.  
- Dispute management.  
- Payout approval & logs; export to CSV.  
- Artist health: cancellations, OOS rates, SLA alerts.  
- Simple CMS for collections, blog, home banners.

---

## 12) Roadmap (Phased)
**Phase 0 (2–3 wks):** Brand, design system, content taxonomy, payments selection, carrier deals.  
**Phase 1 (8–10 wks):** MVP (catalog, checkout, local+intl payments, shipping, certificates basic, artist onboarding, admin).  
**Phase 2 (6–8 wks):** 360°/AR pipeline, collections editorial, reviews, analytics, SEO.  
**Phase 3:** Workshops & experiences booking; airport pickup; on‑chain certificates for premium.

---

## 13) KPIs & Metrics
- GMV, AOV, conversion rate, repeat purchase rate.  
- Artist retention, time‑to‑first‑sale, payout TAT.  
- Content depth (avg media per PDP), % items with story, AR engagement.  
- NPS/CSAT, delivery SLA, refund rate.

---

## 14) Risks & Mitigations
- **Counterfeits:** QR certificates + moderation + random audits.  
- **Payments failures:** idempotent webhooks, robust retry, reconciliation jobs.  
- **Fragile shipping:** packaging guides + insured carriers + dimensional weight rules.  
- **Image/3D heavy:** CDN + background processing + size budgets.  
- **Artist onboarding friction:** mobile-first KYC, assisted onboarding via WhatsApp.

---

## 15) Next Steps (Actionable)
1) Confirm payment & shipping providers (DPO vs PesaPal; Posta vs DHL).  
2) Lock taxonomy (tribe, region, materials).  
3) Design wireframes for PDP (story-first + AR).  
4) Stand up Dev environment (Docker compose template).  
5) Implement Catalog → Checkout → Webhooks → Certificates (happy path).  
6) Recruit 10 pilot artists (Makonde, Tinga‑Tinga, Kilwa crafts) for seed inventory.

