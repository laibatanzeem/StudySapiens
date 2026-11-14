/* ==========================================================================
   StudySapiens · ss-config.js — SITE SETTINGS (the only file you edit here)
   --------------------------------------------------------------------------
   After you sign up for the services below, paste your values here and
   re-upload this ONE file (site/assets/js/ss-config.js) — nothing else
   changes. Until a value is empty, that form safely falls back to opening
   the visitor's email app (the old behaviour), so the site never breaks.

   ⚠ SAFETY: only paste values that are MEANT to be public (form URLs and
   website "access keys"). NEVER paste a secret API key from any service —
   everything in this file is visible in the visitor's browser.
   ========================================================================== */
window.SS_CONFIG = {

  /* ---- CONTACT FORM (Web3Forms — free, no account needed) --------------
     1. Go to  https://web3forms.com
     2. Enter  admin@studysapiens.com  and submit.
     3. They email you an "Access Key" (a short code). Paste it below.
     Contact messages then arrive straight in that inbox, with spam
     filtering + our hidden honeypot field blocking bots.                 */
  contactEndpoint: "https://api.web3forms.com/submit",
  contactAccessKey: "",            // <-- paste your Web3Forms access key here

  /* ---- NEWSLETTER (your ESP: MailerLite / Brevo / Buttondown / Kit…) ---
     Recommended: MailerLite (free up to 1,000 subscribers, double opt-in
     built in). In your ESP, create an embedded/sign-up form, then copy its
     form ACTION URL (the address inside  <form action="...">  of the embed
     code) and paste it below.

     - Buttondown / Brevo / Kit forms use field name "email"  → leave
       newsletterEmailField as "email".
     - MailerLite embeds use  fields[email]  → change it to "fields[email]".
     - If the embed code contains hidden inputs (e.g. groups[] or list ids),
       copy them into newsletterFields below.

     In your ESP settings, turn DOUBLE OPT-IN ON (confirmation email) —
     the site's success message already tells students to expect it.      */
  newsletterEndpoint: "",          // <-- paste your ESP form action URL here
  newsletterEmailField: "email",   // MailerLite: "fields[email]"
  newsletterFields: {},            // e.g. { "groups[]": "1234567890" }

  /* Fallback address used when the values above are still empty: */
  notifyEmail: "admin@studysapiens.com"
};
