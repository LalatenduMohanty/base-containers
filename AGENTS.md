# AGENTS.md - AI Agent Instructions for ODH Base Containers

## Project Overview

This repository provides standardized Containerfiles for building Open Data Hub (ODH) midstream base images for AI/ML workloads in OpenShift AI.

| Image | Base OS | Containerfile |
|-------|---------|---------------|
| Python 3.12 | UBI 9 | `Containerfile.python` |
| CUDA 12.8 | CentOS Stream 9 | `Containerfile.cuda` |

## Repository Structure

```text
base-containers/
├── Containerfile.python              # Python 3.12 on UBI 9 (CPU)
├── Containerfile.cuda                # CUDA 12.8 + Python 3.12 (GPU)
├── .hadolint.yaml                    # Hadolint linter configuration
├── build-args/
│   ├── python-app.conf               # Python build arguments
│   └── cuda-app.conf                 # CUDA build arguments
├── requirements-build.txt            # Build-time deps (uv) - Dependabot updates
├── scripts/
│   ├── build.sh                      # Main build script
│   ├── lint-containerfile.sh                       # Containerfile linter (Hadolint)
│   └── fix-permissions               # OpenShift permission fixer
├── .github/
│   └── workflows/
│       └── ci.yml                                  # CI workflow (Hadolint, tests)
└── docs/
    └── RATIONALE.md
```

## Build Commands

```bash
./scripts/build.sh python             # Build Python image
./scripts/build.sh cuda               # Build CUDA image
./scripts/build.sh all                # Build all images
```

## Lint Commands

```bash
./scripts/lint-containerfile.sh                     # Lint all Containerfiles
./scripts/lint-containerfile.sh Containerfile.python    # Lint specific file
./scripts/lint-containerfile.sh Containerfile.*         # Lint matching files
```

Hadolint configuration is in `.hadolint.yaml`. Run linting before submitting PRs.

## Build System

Config files in `build-args/*.conf` are passed directly to podman via `--build-arg-file`. Format: `KEY=value` (one per line, `#` comments allowed). DO NOT source these as shell scripts or use shell syntax.

## Code Style Guidelines

### Containerfiles
- Use section headers with `# ----` separators
- Group related ENV statements
- Use `--chmod` and `--chown` in COPY commands
- Pin package versions via build args, not hardcoded

### Containerfile Consistency
When modifying `Containerfile.python` or `Containerfile.cuda`, check if the same change applies to the other. Keep Python environment setup, package index configuration, directory permissions, user setup, and documentation sections consistent. Only CUDA-specific sections (packages, NVIDIA env vars) should differ.

### Config Files (build-args/*.conf)
- Format: `KEY=value` (no `export`, no `$(...)`)
- Include source URLs for version numbers

## Container Standards

| Property | Value |
|----------|-------|
| User ID | 1001 |
| Group ID | 0 (root group for OpenShift) |
| Workdir | `/opt/app-root/src` |
| OpenShift SCC | `restricted` compatible |

## Common Patterns

**Adding a build argument:** Add to `build-args/*.conf`, then add corresponding `ARG` in the Containerfile.

**Updating versions:** Edit the appropriate `.conf` file and run `./scripts/build.sh` to test.

## Things to Avoid

- DO NOT hardcode versions in Containerfiles - use build args
- DO NOT use `:latest` tags in production builds
- DO NOT run containers as root (UID 0) in final image

## External Resources

- [NVIDIA CUDA Dockerfiles](https://gitlab.com/nvidia/container-images/cuda/-/tree/master/dist)
- [UBI Python Images](https://catalog.redhat.com/software/containers/ubi9/python-312)
- [uv Package Manager](https://github.com/astral-sh/uv/releases)
- [buildah-build(1) documentation](https://github.com/containers/buildah/blob/main/docs/buildah-build.1.md)
- [Hadolint - Dockerfile Linter](https://github.com/hadolint/hadolint)