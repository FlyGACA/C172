# Self-hosted CI runner

The C172 workflows can use a dedicated Linux runner for trusted branches and same-repository
pull requests. Pull requests from forks always use GitHub-hosted runners because untrusted PR
code must not run on a private server.

## Register the runner

1. Open **C172 → Settings → Actions → Runners → New self-hosted runner**.
2. Follow GitHub's current Linux installation commands on the server. Create a dedicated,
   non-login user and do not run the service as root.
3. Add a custom runner label such as `c172-ci` during configuration.
4. Install Git, Python 3.12, Node 22, and the system libraries listed in
   `.github/workflows/ci.yml`. Docker or a disposable VM is recommended.
5. Install the runner as a service using the `svc.sh` commands shown by GitHub.
6. Confirm the runner appears online with the `c172-ci` label. Trusted jobs select that label
   directly; no repository variable is required.

## Security and maintenance

- Use this runner only for C172; do not share it with unrelated public repositories.
- Keep the runner user away from production credentials, SSH keys, and deployment tokens.
- Prefer an ephemeral VM or container snapshot for each job when possible.
- Patch the operating system and runner application regularly.
- Monitor disk space because Blender downloads, npm caches, screenshots, and rebuilt GLBs
  can accumulate quickly.
- Never remove the fork-PR guard in `ci.yml` without an equivalent isolation boundary.
