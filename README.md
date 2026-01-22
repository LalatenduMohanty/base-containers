# ODH Base Containers

Common base container images for Open Data Hub (ODH) workloads.

## Overview

This repository provides standardized Containerfiles for building ODH midstream base images. These images serve as the foundation for AI/ML workloads in OpenShift AI.

**Why base images?** See [docs/RATIONALE.md](docs/RATIONALE.md) for the motivation behind this project.
For development setup and workflow, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Quick Start

### Using Build Script (Recommended)

```bash
# Build all images using versions from config file
./scripts/build.sh all

# Build only Python base image
./scripts/build.sh python

# Build only CUDA base image
./scripts/build.sh cuda
```

### Manual Build

```bash
# Build Python base image
podman build -t odh-midstream-python-base:3.12-ubi9 \
  -f Containerfile.python .

# Build CUDA base image
podman build -t odh-midstream-cuda-base:12.8-py312 \
  -f Containerfile.cuda .
```

## Repository Structure

```text
base-containers/
├── Containerfile.python       # Python 3.12 on UBI 9
├── Containerfile.cuda         # CUDA 12.8 + Python 3.12
├── .hadolint.yaml             # Hadolint configuration
├── build-args/
│   ├── python-app.conf        # Python/CPU image build arguments
│   └── cuda-app.conf          # CUDA/GPU image build arguments
├── requirements-build.txt     # Build-time Python deps (enables Dependabot)
├── scripts/
│   ├── build.sh               # Build script
│   ├── lint-containerfile.sh  # Containerfile linter (Hadolint)
│   └── fix-permissions        # OpenShift permission fixer
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI workflow (Hadolint, tests)
├── docs/
│   ├── DEVELOPMENT.md         # Development setup and workflow
│   └── RATIONALE.md           # Why this project exists
├── .tekton/                   # Konflux pipeline definitions
├── LICENSE
└── README.md
```

## Why Two Base Images?

| Template | Base | Reason |
|----------|------|--------|
| Python (CPU) | UBI 9 | Smaller footprint, Red Hat supported |
| CUDA (GPU) | CentOS Stream 9 | CUDA requires OpenGL/mesa libs not in UBI 9 |

**Note:** 
* CUDA packages fail on UBI 9 due to missing dependencies (OpenGL, mesa libs). CentOS Stream 9 includes these libraries.
* Python images remain on UBI 9 to minimize migration impact. A unified CentOS Stream 9 base for all images may be considered in the future.

## Common Properties

Both images share consistent configuration:

| Property | Value |
|----------|-------|
| User ID | 1001 |
| Group ID | 0 (root group) |
| Workdir | `/opt/app-root/src` |
| OpenShift SCC | `restricted` compatible |

## Extending Base Images

### Python Application

```dockerfile
FROM quay.io/opendatahub/odh-midstream-python-base:3.12-ubi9

# pip and uv are pre-configured with package indexes
COPY requirements.txt .
RUN pip install -r requirements.txt
# Or use uv (faster): RUN uv pip install -r requirements.txt

COPY --chown=1001:0 . .
CMD ["python", "app.py"]
```

### CUDA Application

```dockerfile
FROM quay.io/opendatahub/odh-midstream-cuda-base:12.8-py312

# pip and uv are pre-configured with PyPI + PyTorch CUDA indexes
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=1001:0 . .
CMD ["python", "train.py"]
```

## Build Arguments

Build arguments are defined in config files under `build-args/`:

| Config File | Image |
|-------------|-------|
| `build-args/python-app.conf` | Python/CPU |
| `build-args/cuda-app.conf` | CUDA/GPU |

The build script passes these directly via `--build-arg-file`. To update versions, edit the appropriate `.conf` file and rebuild.

```bash
# Update versions and rebuild
vim build-args/python-app.conf
./scripts/build.sh python
```

## CI/CD

Images will be built using [Konflux](https://konflux-ci.dev/) pipelines.

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

