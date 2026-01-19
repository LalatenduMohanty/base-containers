#!/bin/bash
# =============================================================================
# ODH Base Containers - Build Script
# =============================================================================
# Usage: ./scripts/build.sh [python|cuda|all]
#
# Environment Variables:
#   IMAGE_REGISTRY    - Registry prefix (default: quay.io/opendatahub)
#   PUSH_IMAGES       - Push after build (default: false)
#
# Note: Requires podman/buildah (uses --build-arg-file, not supported by docker)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

IMAGE_REGISTRY="${IMAGE_REGISTRY:-quay.io/opendatahub}"
PUSH_IMAGES="${PUSH_IMAGES:-false}"

# Require podman/buildah (--build-arg-file not supported by docker)
if ! command -v podman &> /dev/null; then
    echo "Error: podman is required (--build-arg-file not supported by docker)" >&2
    exit 1
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# Detect target architecture (maps uname -m to OCI arch names)
get_target_arch() {
    local arch
    arch=$(uname -m)
    case "${arch}" in
        x86_64)  echo "amd64" ;;
        aarch64) echo "arm64" ;;
        *)       echo "${arch}" ;;
    esac
}

get_config_value() {
    local config_file="$1"
    local key="$2"
    grep "^${key}=" "${config_file}" 2>/dev/null | cut -d'=' -f2- || true
}

build_image() {
    local target="$1"
    local config_file="${PROJECT_ROOT}/build-args/${target}-app.conf"
    local containerfile="${PROJECT_ROOT}/Containerfile.${target}"

    if [[ ! -f "${config_file}" ]]; then
        log_error "Config file not found: ${config_file}"
        exit 1
    fi

    if [[ ! -f "${containerfile}" ]]; then
        log_error "Containerfile not found: ${containerfile}"
        exit 1
    fi

    local image_tag
    image_tag=$(get_config_value "${config_file}" "IMAGE_TAG")
    if [[ -z "${image_tag}" ]]; then
        log_error "IMAGE_TAG not defined in ${config_file}"
        exit 1
    fi

    local image_name="${IMAGE_REGISTRY}/odh-midstream-${target}-base"
    local full_image="${image_name}:${image_tag}"

    local target_arch
    target_arch=$(get_target_arch)

    log_info "Building ${target} base image: ${full_image}"
    log_info "  Config: ${config_file}"
    log_info "  Arch: ${target_arch}"

    podman build \
        --build-arg-file "${config_file}" \
        --build-arg BUILD_DATE="$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        --build-arg TARGETARCH="${target_arch}" \
        -t "${full_image}" \
        -f "${containerfile}" \
        "${PROJECT_ROOT}"

    log_info "Successfully built: ${full_image}"

    if [[ "${PUSH_IMAGES}" == "true" ]]; then
        log_info "Pushing: ${full_image}"
        podman push "${full_image}"
    fi
}

print_usage() {
    echo "Usage: $0 [python|cuda|all]"
    echo ""
    echo "Build ODH base container images using config from build-args/<target>-app.conf"
    echo ""
    echo "Targets:"
    echo "  python  - Build Python base image (CPU)"
    echo "  cuda    - Build CUDA base image (GPU)"
    echo "  all     - Build all images (default)"
    echo ""
    echo "Environment Variables:"
    echo "  IMAGE_REGISTRY    - Registry prefix (default: quay.io/opendatahub)"
    echo "  PUSH_IMAGES       - Push after build (default: false)"
    echo ""
    echo "Note: Requires podman (uses --build-arg-file, not supported by docker)"
}

main() {
    local target="${1:-all}"

    log_info "=== ODH Base Containers Build ==="
    echo "  Image Registry: ${IMAGE_REGISTRY}"
    echo "  Push Images:    ${PUSH_IMAGES}"
    echo "=================================="

    case "${target}" in
        python|cuda)
            build_image "${target}"
            ;;
        all)
            build_image "python"
            build_image "cuda"
            ;;
        -h|--help|help)
            print_usage
            exit 0
            ;;
        *)
            log_error "Unknown target: ${target}"
            print_usage
            exit 1
            ;;
    esac

    log_info "Build completed successfully!"
}

main "$@"
