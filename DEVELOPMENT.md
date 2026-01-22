# Development Notes

### Linting Containerfiles

```bash
# Lint all Containerfiles in project
./scripts/lint-containerfile.sh

# Lint specific file
./scripts/lint-containerfile.sh Containerfile.python
./scripts/lint-containerfile.sh path/to/Dockerfile
```

Requires [Hadolint](https://github.com/hadolint/hadolint). If not installed locally, the script falls back to running Hadolint via podman.
