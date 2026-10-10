# Website lane working instructions

This is the xiom-lang website lane (xiom-lang.org). SESSION.md is the
running record; DEPLOY.md is the deploy reference. Read both before acting.

Cross-lane coordination goes through the private relay bus:

- At session start and before finishing any task: pull xiom-relays
  (`git -C E:\xiom-lang\xiom-relays pull --ff-only`) and process items
  addressed to the website lane (`python tools/relay.py view --lane
  website`), updating the statuses the website lane owns.
- Never edit another lane's item; open a new item instead.
- One item per issue; the addressed lane moves open -> acked -> fixed,
  the reporter moves fixed -> verified -> closed. Full rules:
  xiom-relays PROTOCOL.md.

Site rules (full list in SESSION.md):

- Pure-ASCII files only.
- Never hardcode versions in pages; read the mirror JSON (latest.json).
- Pin GitHub Actions refs to full SHAs.
- Keep the site static and honest: no claim the implementation does not
  support.
- Sign every commit (`git commit -s`, DCO) with the repo-local identity
  Lefteris Notas <lefterisnotas@gmail.com>.
