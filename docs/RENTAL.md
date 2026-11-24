# Renting out the twin

Status on 2026-11-24: **built, not deployed, not on sale.** The owner asked for the twin to be rented. This page says how the gate works and what the owner has to do to turn it on. Until then the site stays as [ACCESS.md](ACCESS.md) describes it: behind Cloudflare Access, for the company's own people.

Fly GACA is independent and is not affiliated with GACA, Textron Aviation (Cessna) or Lycoming. The twin is for study only: it is not a Pilot's Operating Handbook and not a simulator approved for training. (فلاي قاكا جهة مستقلة وليست تابعة للهيئة العامة للطيران المدني. التوأم للدراسة فقط.)

## How it works

Two repositories share the work, and one secret.

| Part | Where | What it does |
| --- | --- | --- |
| The shop | FlyGACA/FlightBag (`lib/twin.js`, `api/twin-signin.js`) | Takes the payment (30 days, 12 months, or a classroom licence for one instructor and up to 30 students), keeps the record of who has access until when, and emails a sign-in link. A renewal adds days to the end. Nothing renews by itself. |
| The pass | signed by the shop with `TWIN_ACCESS_SECRET` | Five minutes long. It says when the access ends and carries a hash in place of the email, so this site never learns who the renter is. |
| The gate | here: `worker/access.js`, `worker/index.js` | Checks the pass, sets its own session cookie (until the access ends, or 30 days, whichever is first), and lets a signed-in visitor open the files. |

What a visitor can open:

- **Anyone:** the home page and `site/` (styles, the mark, the hero picture, the locked page).
- **A renter with a session:** everything else, including the aircraft, the cockpit, the flight lessons, the model files, and the handbook pages and PDFs under `11_training_handbook/`.
- **Signed out:** a page answers with the locked page (status 402), which links to the shop's sign-in and its rental page; any other file answers 401 and is never read.

It fails closed. With no `TWIN_ACCESS_SECRET`, or one shorter than 32 characters, no pass and no session is valid, so only the home page answers.

## Turning it on (the owner, in this order)

Nothing below has been done, and none of it is done from this repository.

1. **Find out how the `c172` Worker is deployed today.** There is no Wrangler file at the root of this repository, so its settings live in the Cloudflare dashboard. The config for the gated version is parked at `deploy/twin/wrangler.jsonc` so that no deploy picks it up by accident. It serves the repository root as static files, as the site does now; check what the current deployment leaves out (for example `.git` and `node_modules`) and keep leaving it out.
2. **Make one secret** of 32 random characters or more and set it as `TWIN_ACCESS_SECRET` on **both** Workers: `c172` here and `flightbag` in the shop. Never write it into a file.
3. On the shop, set `TWIN_ORIGIN` to this site's address (for example `https://c172.flygaca.com`), and the prices `PRICE_C172_TWIN_MONTH` and `PRICE_C172_TWIN_YEAR`.
4. **Deploy the gated Worker to a preview address first**, with Cloudflare Access still on. Check there: the home page opens; `08_realistic_digital_twin/index.html` shows the locked page; a model file answers 401.
5. **Make a test purchase** on a shop preview with `C172_TWIN_SALE_ENABLED=1`, follow the emailed link, and fly a lesson.
6. **Only then remove the Cloudflare Access application** from the `c172` Worker, and switch the sale on in production. Removing Access before the gated Worker is live would open every file to everyone.

## Open, for the owner

- **Not tested against real services.** The gate and the shop are tested with fakes only. No deploy, no purchase and no sign-in has been tried.
- **The repository is public.** Everything the gate protects on the site can be taken from GitHub without paying. The gate is worth little until the repository is private. See `LICENSING.md`.
- **The handbook is inside the gate.** A renter can read the handbook pages and download its PDFs from this site. The shop also sells that handbook as a licensed PDF for one price; the two overlap.
- **Staff access.** Once Cloudflare Access is removed, the company's own people need a pass like anyone else. There is no free or staff pass yet.
- **The sign-out link in the header** still points at Cloudflare Access (`site/ufuq/ufuq.shell.js`, copied from FlyGACA/UFUQ and not edited here). `/api/signout` exists; the header does not use it yet.
- **Classes.** A classroom licence is built on the shop's side: students join there with a class code, and each then signs in here like any renter. This site cannot tell a student from any other renter, and the instructor cannot remove a student.
- **Sharing.** A session is tied to a browser, not a person; nothing stops a renter from forwarding the sign-in link while it is valid.

## Checks

`npm test` runs `test/rental.test.mjs`: the pass and the session cannot be forged or stretched, only the home page and `site/` are open, a signed-out visitor never reaches a model file, a missing secret opens nothing, and the deploy config is not at the root. One pass string is pinned here and in the shop's tests, so the two sides cannot drift apart unnoticed.
