# Who can open the site

The site is a set of static files. A sign-in form written into the pages would not protect them: the model files and every other file would still answer to anyone who knows the address. The gate therefore sits in front of the whole hostname, at Cloudflare, and nothing in this repository implements it.

**Status on 2026-11-16: not applied.** `https://c172.flygaca.com/` answered 200 with no sign-in. Applying the gate is the owner's action in the Cloudflare dashboard.

## The rule

One Cloudflare Access application for the hostname, with one Allow policy that includes:

- every address ending in the company's email domain, and
- a named list of invited addresses outside that domain.

Sign-in is by a one-time code sent to the person's email. Nobody else gets past Cloudflare, so no file is served to them.

## Steps (owner, in the Cloudflare dashboard)

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
