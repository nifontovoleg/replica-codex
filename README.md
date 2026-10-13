# Replica Codex

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-Agent%20Skills-111827?style=flat-square)
![Skills](https://img.shields.io/badge/Skills-11-6366F1?style=flat-square)
![Tools](https://img.shields.io/badge/Python%20tools-6-14B8A6?style=flat-square)
![Language](https://img.shields.io/badge/Skill%20UI-Russian-EC8C9C?style=flat-square)
[![CI](https://github.com/nifontovoleg/replica-codex/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nifontovoleg/replica-codex/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**Replica Codex** is a pack of 11 skills for building your own application from
observable product behavior: map screens and flows, plan the architecture,
implement the core workflow, test it, compare features, and prepare an original brand.

Built for **ChatGPT Codex Desktop, Codex CLI and the IDE extension**.
Skill names in the picker are Russian; Codex responds in the user's language.
The workflow instructions and code identifiers are English.

> This is a skill pack, not an application or an autonomous agent service.
> It runs inside your existing Codex session and uses the tools available there.
> The six Python tools run locally with the standard library.

[Quick start](#quick-start) · [Skills](#the-11-skills) · [Usage](#try-one-workflow) ·
[Tools](#local-python-tools) · [Testing](#testing) · [Troubleshooting](#troubleshooting) ·
[Подробный план тестирования](docs/TESTING.md)

---

## Why this exists

Rebuilding a product is easier to evaluate when each stage produces a concrete
artifact: a screen inventory, a feature matrix, a working flow, or a reproducible
bug report. Replica Codex connects these stages through a `replica/` folder in
your application project.

It studies public behavior and writes a fresh implementation. The original
product's code, private APIs, assets, copy and identity are outside that workflow.

## Features

| Capability | Current behavior |
| --- | --- |
| **11 focused skills** | Research, architecture, design, build, backend, QA, diff, reviews, brand, launch and deploy |
| **Codex integration** | `$replica-...` invocation, Russian picker labels and starter prompts |
| **Local installation** | User-wide or project-local; preserves existing files that differ |
| **Windows support** | Quoted absolute tool paths, separate project working directory, Python launcher guidance |
| **Six offline tools** | Feature parity, PNG layout diff, review analysis, contrast, brand sweep and listing lint |
| **Strict readiness check** | Missing must-have features block deployment even above the overall score threshold |
| **Evidence-based reporting** | Executed checks, failures and checks not run are reported separately |
| **Explicit scope** | A suggested next stage does not silently start a build, payment or deployment |

## Requirements

- **Git** to clone this repository.
- **Python 3.8+** for installation, tests and local tools. Python 3.12 is a
  straightforward choice for the Windows commands below.
- **Codex Desktop, CLI or IDE extension** with an active account/session.
- **Optional browser access** for observing pages and testing the resulting UI.
  Screenshots and supplied requirements can be used when browsing is unavailable.

No `pip install` is needed for the installed tools. No separate API key is
needed to install the pack. Model runs use your Codex account limits; third-party
services used by an application may need their own credentials and billing.

## Quick start

### Windows / PowerShell

Run in a directory where you keep source projects:

```powershell
git clone https://github.com/nifontovoleg/replica-codex.git
cd replica-codex
py -3.12 --version
py -3.12 scripts/install_codex.py --dest "$HOME/.agents/skills"
py -3.12 scripts/install_codex.py --check --dest "$HOME/.agents/skills"
```

The first command installs **all 11 skills**. The second verifies their files.
If Python 3.12 is not installed, choose an installed Python 3.8+ version:

```powershell
py --list-paths
python --version
python scripts/install_codex.py --dest "$HOME/.agents/skills"
```

If neither launcher works, use the absolute path to a working Python executable:

```powershell
& "C:/path/to/python.exe" scripts/install_codex.py --dest "$HOME/.agents/skills"
```

### Linux / macOS

```bash
git clone https://github.com/nifontovoleg/replica-codex.git
cd replica-codex
python3 --version
python3 scripts/install_codex.py --dest "$HOME/.agents/skills"
python3 scripts/install_codex.py --check --dest "$HOME/.agents/skills"
```

### Open in Codex

1. Open **your application project folder** in Codex.
2. Start a message and select a Replica skill in the skill picker. In CLI/IDE,
   type `$replica-recon` or use `/skills`.
3. Send a request with the reference URL and the single workflow to investigate.
4. Inspect the files saved in your application's `replica/` folder.

New skills should be available on the next turn. If they do not appear, restart
Codex. See the [official skill documentation](https://learn.chatgpt.com/docs/build-skills).

### Project-local installation

To expose the pack only in one project:

```powershell
py -3.12 scripts/install_codex.py --dest "C:/Projects/my-app/.agents/skills"
```

```bash
python3 scripts/install_codex.py --dest /path/to/my-app/.agents/skills
```

Choose **one installation scope**. Installing identical names in both the user
and project folders can produce duplicate picker entries. Running the installer
without `--dest` uses `$CODEX_HOME/skills`, or `~/.codex/skills` when unset;
this README uses the explicit `~/.agents/skills` location consistently.

### Install as a Codex plugin

Use this as an alternative to standalone skill installation. Do not install
both copies into the same profile. From the cloned repository:

```powershell
py -3.12 scripts/build_plugin.py
codex plugin marketplace add .
codex plugin add replica-codex@replica-codex-local
codex plugin list --marketplace replica-codex-local --json
```

```bash
python3 scripts/build_plugin.py
codex plugin marketplace add .
codex plugin add replica-codex@replica-codex-local
codex plugin list --marketplace replica-codex-local --json
```

The builder creates `dist/replica-codex/` with the Codex manifest, the 11 skills
under `skills/`, their tools and the MIT license. It excludes repository history,
test environments and local settings. The repo marketplace points to this built
package. Codex installs a separate copy in its plugin cache.

Plugin skills use a namespace:

```text
$replica-codex:replica-recon Разбери приложение <URL> и сохрани карту сценариев.
```

Use `$replica-codex:replica-test`, `$replica-codex:replica-diff` and the equivalent
names for other stages. Standalone installations use the short commands below.
See [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins).

## The 11 skills

| Command | Artifact / responsibility |
| --- | --- |
| `$replica-recon` | Screen inventory, flows, sources, inferred data model and `replica/features.csv` |
| `$replica-architect` | Stack, schema, API and vertical-slice build order |
| `$replica-design` | Design tokens, component specs and a contrast report |
| `$replica-build` | Working core flow, subsequent screens and feature progress |
| `$replica-backend` | Auth, database, test payments and official integrations |
| `$replica-test` | Test plan, end-to-end tests and reproduced bug reports |
| `$replica-diff` | Feature parity, screenshot layout comparison and missing features |
| `$replica-entrepreneur` | Sourced review analysis, improvements and positioning |
| `$replica-brand` | Original name, palette, voice and a scan for old-brand traces |
| `$replica-launch` | Landing copy, pricing research, store listings and launch plan |
| `$replica-deploy` | Readiness checks and deployment within the user's authorization |

For a full project:

```text
recon -> architect -> design -> build -> backend -> test -> diff
      -> entrepreneur -> brand -> launch -> deploy
```

Each skill can run independently. Read the result before requesting another stage.

## Try one workflow

Start with a narrow scope, such as booking one appointment:

```text
$replica-recon Разбери приложение <URL>. Платформа: веб.
Нужен только сценарий записи на встречу.
Сохрани карту экранов, сценарии и матрицу функций в replica/.
Укажи источники и неизвестные состояния. Разработку пока не начинай.
```

Then request the next step when ready:

```text
$replica-architect Спланируй приложение по собранной карте.
Сохрани существующий стек проекта. Начни с одного рабочего сценария.
```

```text
$replica-build Реализуй основной сценарий по карте и архитектуре.
Проверь результат в браузере и обнови replica/features.csv.
```

```text
$replica-test Пройди основной сценарий, ошибки и повторную отправку.
Сохрани воспроизводимые ошибки. Отдельно укажи проверки, которые не запускались.
```

Research and implementation outputs belong to **your application project**:

```text
my-app/
  replica/
    recon.md
    features.csv
    architecture.md
    design/
    build-log.md
    backend.md
    test-plan.md
    bugs.md
    parity.md
    reviews.csv
    fixes.md
    brand.json
    launch/
    deploy.md
```

This is an example artifact map; individual stages create only the files they need.
Reference screenshots remain research material and are not shipped with the app.

## Local Python tools

Run these commands from **your application project**, after the relevant input
files have been created. Set the path to the chosen installation directory:

```powershell
$replicaSkills = Join-Path $HOME '.agents/skills'

py -3.12 "$replicaSkills/replica-diff/parity.py" replica/features.csv
py -3.12 "$replicaSkills/replica-diff/parity.py" replica/features.csv --require-must-have --fail-under 80
py -3.12 "$replicaSkills/replica-diff/imgdiff.py" replica/screens/S01.png replica/clone-screens/S01.png --out replica/diff-S01.png
py -3.12 "$replicaSkills/replica-design/contrast.py" replica/design/tokens.json
py -3.12 "$replicaSkills/replica-entrepreneur/reviews.py" replica/reviews.csv --out replica/feedback.md
py -3.12 "$replicaSkills/replica-brand/sweep.py" . --config replica/brand.json
py -3.12 "$replicaSkills/replica-launch/listing.py" replica/launch/listing.json
```

On Linux/macOS use `python3` and the same quoted script paths:

```bash
REPLICA_SKILLS="$HOME/.agents/skills"
python3 "$REPLICA_SKILLS/replica-diff/parity.py" replica/features.csv --require-must-have --fail-under 80
python3 "$REPLICA_SKILLS/replica-design/contrast.py" replica/design/tokens.json
```

| Tool | Meaning / exit behavior |
| --- | --- |
| `parity.py` | Weights must/should/could features. Reporting mode can return 0 with incomplete features; use the strict flags for release checks |
| `imgdiff.py` | Compares PNG layout/edges; does not judge product behavior or promise pixel-perfect replication |
| `contrast.py` | Checks configured text/background pairs; returns 1 for failing pairs |
| `reviews.py` | Analyzes supplied review rows; drops rows without URLs; does not collect reviews from the web |
| `sweep.py` | Scans your app for configured names, domains and colors; returns 1 when traces remain |
| `listing.py` | Checks supplied store metadata; returns 1 for errors; a pass is not store approval |

Use `--help` for each tool's options. A score is evidence for that check only,
not a guarantee that the application is ready for production.

## Testing

From the **Replica Codex repository root**:

```powershell
py -3.12 -m unittest discover -s tests -v
py -3.12 scripts/install_codex.py --check --dest "$HOME/.agents/skills"
py -3.12 scripts/check_codex_discovery.py --out .test-artifacts/codex-discovery.json
py -3.12 scripts/smoke_codex.py --skills-dir "$HOME/.agents/skills"
py -3.12 scripts/check_plugin.py
```

```bash
python3 -m unittest discover -s tests -v
python3 scripts/install_codex.py --check --dest "$HOME/.agents/skills"
python3 scripts/check_codex_discovery.py --out .test-artifacts/codex-discovery.json
python3 scripts/smoke_codex.py --skills-dir "$HOME/.agents/skills"
python3 scripts/check_plugin.py
```

| Verified locally | Result |
| --- | --- |
| Automated suite | 67 tests passed |
| Codex skill format validation | 11 skills passed |
| Installed Codex `skills/list` discovery | 11 skills found and enabled |
| Installed tool smoke checks | 11 checks passed |
| Native Codex plugin installation and discovery | Installed in an isolated profile; 11 bundled skills found |
| Tools from the installed plugin cache | 11 checks passed; installed files verified |

CI runs the suite, isolated installation, integrity checks and synthetic tool
smoke checks on Windows and Linux with Python 3.8 and 3.12.
CI also builds the Codex plugin and exercises its bundled tools.

`check_plugin.py` builds the package, installs it using the real Codex CLI in
an isolated temporary profile, verifies all installed files, asks Codex to load
the 11 namespaced skills, then executes the tools from the installed cache.
It does not change your main Codex profile or make model calls. Codex CLI is
required for this check; it is tested locally separately from the Python CI.

Discovery uses the installed Codex app-server. It does not start a model run,
create a chat or publish anything. Smoke data and PNGs are synthetic; they do
not demonstrate a completed real-world clone. Full browser/E2E behavior and
automatic skill selection still need a concrete application to evaluate.

See [the verification report](docs/VALIDATION.md) and
[the full testing guide](docs/TESTING.md). PyYAML is needed only if you separately
run the bundled `skill-creator` validator; it is not an installed-tool dependency.

## Updating and uninstalling

Get the latest source and verify the installed copy:

```powershell
git pull --ff-only
py -3.12 scripts/install_codex.py --check --dest "$HOME/.agents/skills"
```

The installer intentionally refuses to overwrite different files. If an update
changes a skill, back up its installed folder, remove or move that exact folder,
and reinstall. Keep any customizations for comparison. Do not delete the entire
skills directory: it also contains unrelated skills.

For plugin updates, back up the generated `dist/replica-codex` folder before
rebuilding if the builder reports different files. Rebuild, then reinstall:

```text
codex plugin remove replica-codex@replica-codex-local
codex plugin add replica-codex@replica-codex-local
```

To uninstall the plugin, run only the remove command above. To remove its catalog:

```text
codex plugin marketplace remove replica-codex-local
```

To uninstall this pack, remove only the 11 `replica-*` folders listed above from
the installation directory you chose, then refresh/restart Codex. Your application
code and its `replica/` research files remain in your project.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| `python` or `py` is missing | Install Python 3.8+, restart the terminal, or use the executable's full path |
| `py -3` selects a broken version | Run `py --list-paths`, then select a working version explicitly, e.g. `py -3.12` |
| Skills are not visible | Check the exact destination, send a new turn, restart Codex and run the discovery script from your normal user account |
| Duplicate skills | Keep one user or project installation; remove only the duplicate Replica folders |
| `Existing skill differs` | The destination contains another version or local edits; back it up before replacing that exact folder |
| Discovery returns no skills in a restricted shell | Repeat from the normal account/profile that runs Codex; sandbox visibility can differ |
| `codex` is not found during discovery | Add Codex CLI to PATH or pass `--codex /full/path/to/codex` |
| No browser tool in the session | Supply screenshots/specs; unobserved states must stay marked as unknown |
| Plain ChatGPT web chat cannot run scripts | Use a local Codex environment; this repository is not a published ChatGPT web plugin |
| A script cannot find `replica/...` | Run it from your application project after the input-producing stage |

## Project structure

```text
replica-recon/          # SKILL.md, metadata and research templates
replica-architect/      # architecture workflow and template
replica-design/         # tokens and contrast.py
replica-build/          # frontend/core-flow implementation workflow
replica-backend/        # backend and integration workflow
replica-test/           # QA templates and Playwright example
replica-diff/           # parity.py and imgdiff.py
replica-entrepreneur/   # reviews.py and theme rules
replica-brand/          # sweep.py and branding workflow
replica-launch/         # listing.py and listing example
replica-deploy/         # deployment workflow and preflight template
scripts/               # installer, Codex discovery and installed-tool smoke checks
tests/                 # standard-library unit and integration tests
docs/                  # verification results and further testing guide
.github/workflows/     # Windows/Linux CI
.codex-plugin/         # native Codex plugin manifest
.agents/plugins/       # local Codex marketplace catalog
LICENSE                # MIT license
```

Each installed skill includes `SKILL.md`, `agents/openai.yaml`, its supporting
files and a copy of the license. Installation uses the Codex skill directories
described above.

## Fine print

Use public sources or accounts you are authorized to use. Respect the relevant
source restrictions. Implement observable functionality with your own code,
assets, words and identity. Reference screenshots are not release assets.

Do not invent reviews, quotes, pricing, name availability, test results or
publication status. Reviews of another product are research, not testimonials
for yours. Real provider calls, payments and deployments require the corresponding
credentials and user-authorized scope.

## License

**MIT License.** See [LICENSE](LICENSE).
