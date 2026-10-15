#!/usr/bin/env python3
"""Dependency-free command interface shared by spine-enabled repositories."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ACTION_USE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.MULTILINE)
FULL_COMMIT_SHA = re.compile(r"[0-9a-fA-F]{40}")


def load_manifest(root: Path) -> tuple[Path, dict[str, Any]]:
    candidates = (root / ".spine" / "manifest.json", root / "spine.json")
    for path in candidates:
        if path.is_file():
            with path.open(encoding="utf-8") as handle:
                data = json.load(handle)
            if data.get("schemaVersion") != 1:
                raise ValueError(f"Unsupported spine schema in {path}")
            return path, data
    raise FileNotFoundError("No .spine/manifest.json or spine.json found")


def load_ecosystem(
    root: Path, data: dict[str, Any]
) -> tuple[Path | None, dict[str, Any] | None]:
    relative = data.get("ecosystemCatalog")
    if relative is None:
        return None, None
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("ecosystemCatalog must be a non-empty relative path")
    if Path(relative).is_absolute():
        raise ValueError("ecosystemCatalog must stay inside the repository")
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError("ecosystemCatalog must stay inside the repository") from error
    with path.open(encoding="utf-8") as handle:
        catalog = json.load(handle)
    return path, catalog


def validate_ecosystem(root: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        path, catalog = load_ecosystem(root, data)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [f"invalid ecosystem catalog: {error}"]
    if path is None or catalog is None:
        return errors
    if catalog.get("schemaVersion") != 1:
        errors.append("ecosystem catalog schemaVersion must be 1")
    if catalog.get("policyAuthority") != "docs/tool-lifecycle.md":
        errors.append("ecosystem policy authority must be docs/tool-lifecycle.md")
    defaults = catalog.get("defaults", {})
    if defaults.get("activation") != "off":
        errors.append("external capabilities must default to off")
    if defaults.get("autoInstall") is not False:
        errors.append("ecosystem must prohibit automatic installation")
    if defaults.get("autoUpdate") is not False:
        errors.append("ecosystem must prohibit automatic updates")
    precedence = catalog.get("precedence", [])
    if not precedence or "owner instruction" not in precedence[0].lower():
        errors.append("ecosystem precedence must begin with owner instruction")
    capability_types = set(catalog.get("capabilityTypes", []))
    sources = catalog.get("sources", [])
    if not isinstance(sources, list) or not sources:
        errors.append("ecosystem catalog must include at least one source")
        return errors
    seen_ids: set[str] = set()
    source_by_id: dict[str, dict[str, Any]] = {}
    seen_repositories: set[str] = set()
    revision_pattern = re.compile(r"[0-9a-f]{40}")
    repository_pattern = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
    for source in sources:
        if not isinstance(source, dict):
            errors.append(f"invalid ecosystem source entry: {source!r}")
            continue
        source_id = source.get("id")
        if not isinstance(source_id, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", source_id
        ):
            errors.append(f"invalid ecosystem source id: {source_id!r}")
            source_id = repr(source_id)
        elif source_id in seen_ids:
            errors.append(f"duplicate ecosystem source id: {source_id}")
        else:
            seen_ids.add(source_id)
            source_by_id[source_id] = source
        repository = source.get("repository")
        if not isinstance(repository, str) or not repository_pattern.fullmatch(
            repository
        ):
            errors.append(f"{source_id}: invalid GitHub repository")
        elif repository in seen_repositories:
            errors.append(f"duplicate ecosystem repository: {repository}")
        else:
            seen_repositories.add(repository)
        if source.get("capabilityType") not in capability_types:
            errors.append(f"{source_id}: unsupported capability type")
        if source.get("state") not in {
            "supported-reference",
            "experimental",
            "observed",
            "blocked",
            "deprecated",
        }:
            errors.append(f"{source_id}: unsupported lifecycle state")
        if source.get("autoInstall") is not False:
            errors.append(f"{source_id}: automatic installation is prohibited")
        if not isinstance(source.get("activationEligible"), bool):
            errors.append(f"{source_id}: activationEligible must be boolean")
        if (
            source.get("activationEligible")
            and source.get("license") == "UNVERIFIED"
        ):
            errors.append(f"{source_id}: unverified licence blocks activation")
        pin = source.get("pin", {})
        if not isinstance(pin.get("ref"), str) or not pin.get("ref"):
            errors.append(f"{source_id}: reviewed ref is required")
        if not isinstance(pin.get("revision"), str) or not revision_pattern.fullmatch(
            pin.get("revision", "")
        ):
            errors.append(f"{source_id}: immutable 40-character revision is required")
        monitor = source.get("monitor", {})
        if not isinstance(monitor.get("ref"), str) or not monitor.get(
            "ref", ""
        ).startswith("refs/"):
            errors.append(f"{source_id}: monitor ref must be a full refs/ path")
        if not isinstance(
            monitor.get("reviewedRevision"), str
        ) or not revision_pattern.fullmatch(monitor.get("reviewedRevision", "")):
            errors.append(f"{source_id}: monitored revision must be immutable")
    seen_capabilities: set[str] = set()
    for route in catalog.get("routes", []):
        if not isinstance(route, dict):
            errors.append(f"invalid ecosystem route entry: {route!r}")
            continue
        capability = route.get("capability")
        source_id = route.get("source")
        if not isinstance(capability, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", capability
        ):
            errors.append(f"invalid routed capability: {capability!r}")
        elif capability in seen_capabilities:
            errors.append(f"duplicate routed capability: {capability}")
        else:
            seen_capabilities.add(capability)
        if source_id not in seen_ids:
            errors.append(
                f"{capability}: route references unknown source {source_id!r}"
            )
        else:
            source = source_by_id[source_id]
            if not source.get("activationEligible"):
                errors.append(f"{capability}: route source is not activation eligible")
        if route.get("state") not in {"pilot", "supported"}:
            errors.append(f"{capability}: unsupported route state")
        if route.get("activation") != "explicit-task-match":
            errors.append(f"{capability}: route activation must be explicit-task-match")
    return errors


def validate_github_policy(root: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    policy = data.get("githubPolicy")
    if not isinstance(policy, dict):
        return ["githubPolicy must be configured"]
    authority = policy.get("authority")
    if not isinstance(authority, str) or not authority:
        errors.append("github policy authority must be configured")
    else:
        authority_path = Path(authority)
        try:
            resolved_authority = (root / authority_path).resolve()
            resolved_authority.relative_to(root.resolve())
        except ValueError:
            errors.append("github policy authority must stay within the repository")
        else:
            if authority_path.is_absolute():
                errors.append("github policy authority must stay within the repository")
            elif not resolved_authority.is_file():
                errors.append(f"missing GitHub policy authority: {authority}")
    if policy.get("releaseDecision") not in {
        "required-before-first-public-release",
        "public-versions-only",
        "not-applicable",
    }:
        errors.append("github release decision must be explicit")
    if policy.get("releaseAuthority") != "supplemental":
        errors.append("GitHub Releases must remain supplemental authority")
    if policy.get("automaticPublish") is not False:
        errors.append("automatic GitHub Release publishing is prohibited")
    if policy.get("generatedNotes") != "review-input-only":
        errors.append("generated release notes must remain review input only")
    if policy.get("actionsPinning") != "full-commit-sha":
        errors.append("GitHub Actions must be pinned to full commit SHAs")
    if policy.get("immutableReleases") not in {
        "recommended-when-releases-apply",
        "enabled",
        "disabled",
        "not-applicable",
    }:
        errors.append("immutable release disposition must be explicit")
    repository = policy.get("repository")
    if repository is not None and not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(repository)
    ):
        errors.append("githubPolicy repository must be owner/name")
    checks = policy.get("liveReviewChecks", [])
    if not isinstance(checks, list):
        errors.append("githubPolicy liveReviewChecks must be a command list")
    return errors


def validate_github_action_pins(root: Path) -> list[str]:
    errors: list[str] = []
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return errors
    for path in sorted((*workflows.glob("*.yml"), *workflows.glob("*.yaml"))):
        text = path.read_text(encoding="utf-8")
        for action in ACTION_USE.findall(text):
            if action.startswith("./"):
                continue
            if "@" not in action:
                errors.append(
                    f"external workflow dependency has no revision: "
                    f"{path.relative_to(root)} ({action})"
                )
                continue
            target, revision = action.rsplit("@", 1)
            if not FULL_COMMIT_SHA.fullmatch(revision):
                errors.append(
                    f"workflow dependency is not pinned to a full SHA: "
                    f"{path.relative_to(root)} ({target}@{revision})"
                )
    return errors


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        return f"unavailable: {result.stderr.strip()}"
    return result.stdout.strip()


def run_commands(root: Path, commands: list[list[str]], label: str) -> int:
    if not commands:
        print(f"{label}: no project-specific commands configured")
        return 0
    for command in commands:
        if not command or not all(isinstance(part, str) for part in command):
            print(f"{label}: invalid command entry {command!r}", file=sys.stderr)
            return 2
        print(f"{label}: {' '.join(command)}")
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            print(
                f"{label}: failed with exit code {result.returncode}",
                file=sys.stderr,
            )
            return result.returncode
    return 0


def internal_audit(root: Path, manifest_path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for relative in data.get("authorities", []):
        if not (root / relative).is_file():
            errors.append(f"missing authority: {relative}")
    for relative in data.get("adapters", []):
        path = root / relative
        if not path.is_file():
            errors.append(f"missing adapter: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if "AGENTS.md" not in text:
            errors.append(f"adapter does not point to AGENTS.md: {relative}")
        if len(text.splitlines()) > 80:
            errors.append(f"adapter is not thin (over 80 lines): {relative}")
    if not data.get("capabilityPolicy", {}).get("recommendationDuty", False):
        errors.append("capability policy must preserve proactive recommendations")
    if data.get("capabilityPolicy", {}).get("scriptsAreExclusiveAllowList", True):
        errors.append("repository commands must not be an exclusive tool allow-list")
    errors.extend(validate_github_policy(root, data))
    errors.extend(validate_github_action_pins(root))
    errors.extend(validate_ecosystem(root, data))
    if data.get("appleSkills"):
        errors.extend(apple_module().policy_errors(root, data))
    print(f"manifest: {manifest_path.relative_to(root)}")
    return errors


def command_doctor(root: Path, manifest_path: Path, data: dict[str, Any]) -> int:
    errors = internal_audit(root, manifest_path, data)
    print(f"python: {sys.version.split()[0]}")
    for tool in data.get("requiredTools", ["git", "python3"]):
        location = shutil.which(tool)
        print(f"{tool}: {location or 'missing'}")
        if not location:
            errors.append(f"required tool is missing: {tool}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("doctor: ready")
    return 0


def orientation(root: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "project": data.get("project", {}),
        "spineVersion": data.get("spineVersion"),
        "branch": git(root, "branch", "--show-current"),
        "head": git(root, "rev-parse", "--short", "HEAD"),
        "status": git(root, "status", "--short"),
        "remote": git(root, "remote", "get-url", "origin"),
    }


def command_orient(root: Path, data: dict[str, Any], as_json: bool) -> int:
    result = orientation(root, data)
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    for key, value in result.items():
        if isinstance(value, dict):
            value = json.dumps(value, sort_keys=True)
        print(f"{key}: {value or '(clean/empty)'}")
    return 0


def command_audit(root: Path, manifest_path: Path, data: dict[str, Any]) -> int:
    errors = internal_audit(root, manifest_path, data)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    result = run_commands(root, data.get("checks", {}).get("audit", []), "audit")
    if result == 0:
        print("audit: passed")
    return result


def command_verify(
    root: Path, manifest_path: Path, data: dict[str, Any], lane: str
) -> int:
    audit_result = command_audit(root, manifest_path, data)
    if audit_result:
        return audit_result
    commands = data.get("checks", {}).get("verify", {}).get(lane, [])
    result = run_commands(root, commands, f"verify lane {lane}")
    if result == 0:
        print(f"verify lane {lane}: configured commands passed")
        guidance = data.get("verificationGuidance", {}).get(lane, [])
        if guidance:
            print("Additional task-specific evidence remains required:")
            for item in guidance:
                print(f"- {item}")
        print("This result is not by itself release, deployment, or merge approval.")
    return result


def command_capabilities(data: dict[str, Any]) -> int:
    policy = data.get("capabilityPolicy", {})
    print(policy.get("default", "Capabilities follow AGENTS.md."))
    print(f"proactive recommendations: {policy.get('recommendationDuty', False)}")
    print(
        "scripts are exclusive allow-list: "
        f"{policy.get('scriptsAreExclusiveAllowList', True)}"
    )
    print(f"read-only research allowed: {policy.get('researchReadOnlyAllowed', False)}")
    print("Human gates:")
    for gate in data.get("humanGates", []):
        print(f"- {gate}")
    return 0


def command_ecosystem(
    root: Path, data: dict[str, Any], as_json: bool, check_upstream: bool
) -> int:
    errors = validate_ecosystem(root, data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    path, catalog = load_ecosystem(root, data)
    if path is None or catalog is None:
        print("ERROR: no ecosystem catalog configured", file=sys.stderr)
        return 2
    if as_json and not check_upstream:
        print(json.dumps(catalog, indent=2, sort_keys=True))
        return 0
    print(f"catalog: {path.relative_to(root)}")
    print(f"catalog version: {catalog.get('catalogVersion')}")
    print(f"reviewed: {catalog.get('reviewedAt')}")
    print("precedence:")
    for index, item in enumerate(catalog.get("precedence", []), start=1):
        print(f"{index}. {item}")
    print("sources:")
    for source in catalog.get("sources", []):
        pin = source["pin"]
        eligibility = "eligible" if source["activationEligible"] else "disabled"
        print(
            f"- {source['id']}: {source['state']}; {source['capabilityType']}; "
            f"{eligibility}; {pin['ref']}@{pin['revision']}"
        )
    print("routes:")
    for route in catalog.get("routes", []):
        print(
            f"- {route['capability']} -> {route['source']} "
            f"({route['state']}; {route['activation']})"
        )
    if not check_upstream:
        print("No installation, update, or external mutation was performed.")
        return 0
    print("upstream drift (read-only git ls-remote):")
    result_code = 0
    for source in catalog.get("sources", []):
        repository = source["repository"]
        monitor = source["monitor"]
        try:
            result = subprocess.run(
                [
                    "git",
                    "ls-remote",
                    f"https://github.com/{repository}.git",
                    monitor["ref"],
                ],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            print(f"- {source['id']}: unavailable (5-second timeout)")
            result_code = 1
            continue
        if result.returncode != 0 or not result.stdout.strip():
            detail = result.stderr.strip() or "ref not found"
            print(f"- {source['id']}: unavailable ({detail})")
            result_code = 1
            continue
        current_revision = result.stdout.split()[0]
        if current_revision == monitor["reviewedRevision"]:
            print(f"- {source['id']}: unchanged ({current_revision})")
        else:
            print(
                f"- {source['id']}: REVIEW DUE "
                f"({monitor['reviewedRevision']} -> {current_revision})"
            )
            result_code = 1
    print("The check reports drift only; it never installs or updates a source.")
    return result_code


def _gh_api(root: Path, endpoint: str) -> tuple[int, Any | None, str]:
    try:
        result = subprocess.run(
            ["gh", "api", endpoint],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        return 1, None, str(error)
    if result.returncode != 0:
        return result.returncode, None, result.stderr.strip()
    if not result.stdout.strip():
        return 0, None, ""
    try:
        return 0, json.loads(result.stdout), ""
    except json.JSONDecodeError as error:
        return 1, None, f"invalid GitHub response: {error}"


def command_github_review(root: Path, data: dict[str, Any], check_live: bool) -> int:
    errors = validate_github_policy(root, data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    policy = data["githubPolicy"]
    print(f"authority: {policy['authority']}")
    print(f"release decision: {policy['releaseDecision']}")
    print(f"release authority: {policy['releaseAuthority']}")
    print(f"automatic publish: {policy['automaticPublish']}")
    print(f"immutable releases: {policy['immutableReleases']}")
    print(f"generated notes: {policy['generatedNotes']}")
    print(f"Actions pinning: {policy['actionsPinning']}")
    print(
        "Review: Releases/tags; repository rules/merge controls; Actions, "
        "environments and OIDC; security/provenance; ownership and "
        "collaboration features."
    )
    if not check_live:
        print(
            "Offline policy review only; no GitHub request or mutation was "
            "performed."
        )
        return 0

    repository = policy.get("repository")
    if not repository:
        print(
            "ERROR: githubPolicy repository is required for --check-live",
            file=sys.stderr,
        )
        return 2
    print(f"live repository: {repository} (read-only)")
    status, metadata, detail = _gh_api(root, f"repos/{repository}")
    if status:
        print(f"ERROR: repository metadata unavailable ({detail})", file=sys.stderr)
        return 1
    default_branch = metadata.get("default_branch", "main")
    print(f"visibility: {metadata.get('visibility', 'unknown')}")
    print(f"default branch: {default_branch}")
    print(
        "merge methods: "
        f"squash={metadata.get('allow_squash_merge')}, "
        f"merge={metadata.get('allow_merge_commit')}, "
        f"rebase={metadata.get('allow_rebase_merge')}; "
        f"delete branch={metadata.get('delete_branch_on_merge')}"
    )
    security = metadata.get("security_and_analysis")
    print(f"security and analysis: {json.dumps(security, sort_keys=True)}")

    checks = (
        ("published Releases", f"repos/{repository}/releases?per_page=1"),
        ("immutable releases", f"repos/{repository}/immutable-releases"),
        ("repository rulesets", f"repos/{repository}/rulesets"),
        (
            "default-branch protection",
            f"repos/{repository}/branches/{default_branch}/protection",
        ),
        (
            "Actions workflow permissions",
            f"repos/{repository}/actions/permissions/workflow",
        ),
        ("deployment environments", f"repos/{repository}/environments?per_page=1"),
        ("Dependabot vulnerability alerts", f"repos/{repository}/vulnerability-alerts"),
    )
    for label, endpoint in checks:
        check_status, response, check_detail = _gh_api(root, endpoint)
        if check_status:
            summary = check_detail.splitlines()[0] if check_detail else "unavailable"
            print(f"- {label}: unavailable ({summary})")
        elif label == "published Releases":
            print(f"- {label}: {'present' if response else 'none'}")
        elif label == "repository rulesets":
            print(f"- {label}: {'present' if response else 'none'}")
        elif label == "deployment environments":
            count = response.get("total_count", 0) if isinstance(response, dict) else 0
            print(f"- {label}: {count}")
        elif label == "Dependabot vulnerability alerts":
            print(f"- {label}: enabled")
        else:
            print(f"- {label}: {json.dumps(response, sort_keys=True)}")
    result = run_commands(
        root, policy.get("liveReviewChecks", []), "github-review"
    )
    print("The live check is read-only and never changes repository settings.")
    return result


def command_release_plan(root: Path, data: dict[str, Any]) -> int:
    print("release-plan: read-only; no upload, submission, deployment, or mutation")
    command_orient(root, data, False)
    print("Human approval gates:")
    for gate in data.get("humanGates", []):
        print(f"- {gate}")
    policy_errors = validate_github_policy(root, data)
    if policy_errors:
        for error in policy_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    policy = data.get("githubPolicy", {})
    print("GitHub Release policy:")
    print(f"- decision: {policy.get('releaseDecision', 'not configured')}")
    print(f"- authority: {policy.get('releaseAuthority', 'not configured')}")
    print(f"- automatic publish: {policy.get('automaticPublish', 'not configured')}")
    if not data.get("appleSkills"):
        apple = {"status": "not_applicable"}
    else:
        try:
            apple = apple_module().check(root, data, fresh=True)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            apple = {"status": "review_required" if str(error).startswith("review_required:") else "blocked", "reason": str(error)}
    print("Apple skills: " + json.dumps(apple, sort_keys=True))
    if apple["status"] not in ("ready", "not_applicable"):
        return 1
    result = run_commands(
        root, data.get("checks", {}).get("releaseReadOnly", []), "release-plan"
    )
    if policy.get("releaseDecision") == "required-before-first-public-release":
        print(
            "ERROR: record the reviewed GitHub Release decision before release",
            file=sys.stderr,
        )
        return result or 1
    return result


def command_evidence(root: Path, data: dict[str, Any], lane: str) -> int:
    state = orientation(root, data)
    print("# Development Evidence")
    print(f"\n- Spine version: `{state['spineVersion']}`")
    print(f"- Branch: `{state['branch']}`")
    print(f"- Commit: `{state['head']}`")
    print(f"- Risk lane: `{lane}`")
    print(f"- Working tree: `{'clean' if not state['status'] else 'has changes'}`")
    print("\n## Required completion notes")
    print("\n- Outcome and acceptance criteria:")
    print("- Checks run and exact results:")
    print("- Checks not run and why:")
    print("- Accessibility, privacy, security, and failure-path evidence:")
    print("- Cost/runtime impact:")
    print("- External state changed:")
    print("- Rollback:")
    print("- Remaining human decisions:")
    return 0


def command_process_review(data: dict[str, Any]) -> int:
    review = data.get("processReview", {})
    print(f"cadence: {review.get('cadence', 'not configured')}")
    print("Review evidence:")
    for metric in review.get("metrics", []):
        print(f"- {metric}")
    print("Questions:")
    print("- Which control prevented a real failure?")
    print("- Which control added cost without useful evidence?")
    print("- What repeated work should become deterministic automation?")
    print("- What new platform or AI capability should be piloted?")
    print("- What should be simplified, replaced, or removed?")
    return 0


def apple_module():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import spine_apple_skills
    return spine_apple_skills


def command_workflow(root: Path, arguments: list[str]) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import spine_liveness
    cli = argparse.ArgumentParser(description="Lazy workflow state; no polling or background jobs")
    spine_liveness.add_parsers(cli.add_subparsers(dest="command", required=True))
    try:
        return spine_liveness.dispatch(root, cli.parse_args(arguments))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "blocked", "reason": str(error), "verified": False}), file=sys.stderr)
        return 3


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=Path.cwd())
    subparsers = result.add_subparsers(dest="command", required=True)
    workflow = subparsers.add_parser("workflow", help="Compact resume and on-demand capability checks")
    workflow.add_argument("arguments", nargs=argparse.REMAINDER)
    apple = subparsers.add_parser("apple-skills", help="Reviewed local Xcode skill lifecycle")
    apple.add_argument("arguments", nargs=argparse.REMAINDER)
    subparsers.add_parser("doctor")
    orient = subparsers.add_parser("orient")
    orient.add_argument("--json", action="store_true")
    subparsers.add_parser("audit")
    verify = subparsers.add_parser("verify")
    verify.add_argument("--lane", choices=("A", "B", "C"), required=True)
    subparsers.add_parser("capabilities")
    ecosystem = subparsers.add_parser("ecosystem")
    ecosystem.add_argument("--json", action="store_true")
    ecosystem.add_argument("--check-upstream", action="store_true")
    github_review = subparsers.add_parser("github-review")
    github_review.add_argument("--check-live", action="store_true")
    subparsers.add_parser("release-plan")
    evidence = subparsers.add_parser("evidence")
    evidence.add_argument("--lane", choices=("A", "B", "C"), required=True)
    subparsers.add_parser("process-review")
    return result


def main() -> int:
    args = parser().parse_args()
    root = args.root.resolve()
    try:
        manifest_path, data = load_manifest(root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if args.command == "apple-skills":
        if not data.get("appleSkills"):
            print("Apple skills: not applicable for this project profile")
            return 0
        return apple_module().command(root, data, args.arguments)
    if args.command == "workflow":
        return command_workflow(root, args.arguments)
    if args.command == "doctor":
        return command_doctor(root, manifest_path, data)
    if args.command == "orient":
        return command_orient(root, data, args.json)
    if args.command == "audit":
        return command_audit(root, manifest_path, data)
    if args.command == "verify":
        return command_verify(root, manifest_path, data, args.lane)
    if args.command == "capabilities":
        return command_capabilities(data)
    if args.command == "ecosystem":
        return command_ecosystem(root, data, args.json, args.check_upstream)
    if args.command == "github-review":
        return command_github_review(root, data, args.check_live)
    if args.command == "release-plan":
        return command_release_plan(root, data)
    if args.command == "evidence":
        return command_evidence(root, data, args.lane)
    if args.command == "process-review":
        return command_process_review(data)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
