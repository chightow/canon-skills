# Contributing

## Contributing a Skill

Skills follow [`standards/skill-setup-std.md`](standards/skill-setup-std.md) —
flat under `skills/`, lowercase-hyphenated filename matching `name:`, required
frontmatter (`name`, `description`, `category`, `tags`), resolvable `@` imports,
and a `depends:` list that matches sibling imports.

Before opening a PR:

1. **Lint**: `./skills.sh lint` — deterministic conformance check; must pass.
2. **Test**: `npm test` — runs the lint plus the core CLI workflow suite.
3. **Catalog**: `./skills.sh catalog` if you added or renamed a skill; commit `CATALOG.md`.
4. One skill, one job. If the description needs an "and then", split it.

`skills.sh lint` runs as part of `npm test`, so running the suite catches
non-conforming skills before they merge.

## Continuous Integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs `npm test` (the
core suite plus `skills.sh lint`) on every pull request to `main` and every
push to `main`.

While the repository is **private**, this check is **advisory** — GitHub branch
protection requires a public repo (or GitHub Pro), so a red check does not yet
block a merge. Do not merge a PR with a failing check.

Branch protection is kept as version-controlled config in
[`.github/rulesets/main-protection.json`](.github/rulesets/main-protection.json):
a PR is required (0 approvals — solo-friendly), the `test` check must pass with
the branch up to date, and `main` allows no deletion, force-push, or merge
commits (squash/rebase only). When the repo goes public, apply it once:

```bash
gh api --method POST repos/sunitghub/canon/rulesets \
  --input .github/rulesets/main-protection.json
```

After that, direct pushes to `main` stop — all changes land through PRs that
pass CI.

## Release Checklist

1. **Bump version** in `package.json` (follow semver: patch for fixes, minor for new skills, major for breaking changes)
2. **Update** any `standards/*.md` files that changed — bump their `version:` and `updated:` frontmatter
3. **Run tests**: `npm test`
4. **Commit** the bump: `git commit package.json -m "chore: bump version to X.Y.Z"`
5. **Tag** the commit: `git tag vX.Y.Z && git push --tags`
6. **Dry run** to verify the package contents: `npm pack --dry-run`
7. **Publish**: `npm publish --access public`
8. **Verify** live: `npm info canon-skills version` and `npx canon-skills@latest`
