# Who can open the site

> Renting the twin to the public is built and not deployed: see [RENTAL.md](RENTAL.md). Until the owner turns that on, everything below is how the site is gated.

The site is a set of static files. A sign-in form written into the pages would not protect them: the model files and every other file would still answer to anyone who knows the address. The gate therefore sits in front of the whole hostname, at Cloudflare, and nothing in this repository implements it.

**Update, later on 2026-11-16: applied.** A Cloudflare Access application, "Fly GACA C172 Twin (members only)", now covers the `c172` Worker that serves this site. It protects the whole Worker, not one hostname, so it covers `c172.flygaca.com`, the Worker's `workers.dev` address and its preview URLs through one destination of type Worker. It uses the account's one-time-PIN sign-in and one shared Allow policy, "Company domain and named members", which includes the company's email domain and a named list kept in Cloudflare. The same policy is attached to the Office, Airspace, C172 Twin and Ufuq applications, so a person is added or removed once.

After it was created, requests from outside to `https://c172.flygaca.com/`, to a file that does not exist and to the Worker's `workers.dev` address all answered 302 to the Access sign-in (status codes only, checked 2026-11-16).

Not established by this record: that a member can sign in end to end, which needs a person with their own email; and that the preview URLs are covered, which the documentation says a Worker destination does but nobody has requested one.

The superseded entry is kept below.

~~**Status on 2026-11-16, earlier: not applied.**~~ `https://c172.flygaca.com/` answered 200 with no sign-in. Applying the gate was the owner's action in the Cloudflare dashboard.

## The rule

One Cloudflare Access application for the hostname, with one Allow policy that includes:

- every address ending in the company's email domain, and
- a named list of invited addresses outside that domain.

Sign-in is by a one-time code sent to the person's email. Nobody else gets past Cloudflare, so no file is served to them.

## Steps (owner, in the Cloudflare dashboard)

These are the steps for a hostname-based application. The application that was created uses a Worker destination instead (see the update above), which makes step 6 unnecessary for it. The steps remain the way to rebuild or check it by hand.

Cloudflare renames its menus from time to time. Follow the current pages rather than this list where they differ: [self-hosted applications](https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/self-hosted-public-app/), [Access policies](https://developers.cloudflare.com/cloudflare-one/policies/access/), [one-time PIN](https://developers.cloudflare.com/cloudflare-one/identity/one-time-pin/).

1. Open Zero Trust, then Access, then Applications. Add an application of type **Self-hosted**.
2. Set the application's hostname to the site's hostname, with no path, so that every file is covered.
3. Under sign-in methods, enable **One-time PIN**.
4. Add a policy with the action **Allow**. Under Include, add a rule **Emails ending in** with the company domain (written with its `@`), and a second rule **Emails** with the invited addresses.
5. Save, then open the site in a private window. It must ask for an email before showing anything, and a deep address such as `…/08_realistic_digital_twin/` must ask too.
6. Cover the project's other address. A Pages or Workers project also answers at its own `*.pages.dev` or `*.workers.dev` address, which the application above does not cover. Either add that hostname to the same application, or turn that address off in the project's settings. Check it in a private window as well.

To add or remove a person later, edit the **Emails** rule of the policy. Removing someone takes effect when their session ends; revoke their session under Access, Users, to end it at once.

Keep the list of people in Cloudflare. Do not write addresses, account identifiers or tokens into this repository.

## What the pages do with it

Behind Access, Cloudflare answers `/cdn-cgi/access/get-identity` with the signed-in person. `site/ufuq/ufuq.shell.js` reads it on the home page, shows the email in the header and reveals a sign-out link to `/cdn-cgi/access/logout`. In a local preview, or while the gate is not applied, that address does not answer and the header shows neither.
