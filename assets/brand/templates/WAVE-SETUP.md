# Branding invoices in Wave (waveapps.com)

Wave generates invoices from its own builder — you can't upload a custom HTML/PDF design, but you can make Wave invoices on-brand with the settings below. If you ever need full control, use `invoice-template.html` in this folder (print to PDF).

## 1. Business profile
Settings → Business:
- **Business name:** Syltech AI Systems, Inc.
- **Address:** Waterloo, ON, Canada
- **Email:** sylvesterranjithfrancis@gmail.com
- **Currency:** CAD

## 2. Logo
Invoice customization → upload logo:
- Use **`assets/brand/syltech-logo-horizontal-light.png`** (badge + dark wordmark, transparent — reads on Wave's white invoice).
- If Wave crops to a square, use **`assets/brand/linkedin/logo-400x400.png`** (badge only).

## 3. Accent color
Invoice customization → accent/color:
- Set to **`#ff5c00`** (Signal Orange).
- Template: pick the cleanest option (e.g. "Modern"); left-aligned logo.

## 4. Products & Services
Pre-create your common line items so invoicing is one click:
- Platform engineering — hourly / day rate
- AI integration — hourly / project
- Cloud infrastructure / DevSecOps — hourly / project
- Consulting / advisory — hourly

## 5. Taxes
Settings → Sales Taxes:
- Add **HST 13%** (Ontario) **only if you are GST/HST registered**. Ontario's small-supplier threshold is CAD $30k in revenue; below that, registration is optional — leave tax off until then.

## 6. Payment terms & footer
Invoice settings:
- **Terms:** Net 15.
- **Footer/memo:** "Payable to Syltech AI Systems, Inc. · Thank you for your business."
- Optionally enable online payments (Wave Payments) for card/bank.

## 7. Numbering
- Start invoices at **INV-0001** and let Wave auto-increment.

---
Colors and logo files live in `../` (see `assets/brand/README.md`). Standalone template: `invoice-template.html`.
