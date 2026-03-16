"""Tests specific to the CUDA base image.

These tests verify CUDA-specific environment variables, libraries,
and labels. All tests run without GPU hardware.
"""

import os
import re

import pytest

# --- CUDA Environment Tests ---


def test_cuda_version(cuda_container):
    """Verify CUDA_VERSION environment variable matches expected version.

    The expected version is controlled by the CUDA_VERSION environment variable.
    If not set, version validation is skipped (only checks env var exists).
    """
    actual_version = cuda_container.get_env("CUDA_VERSION")
    assert actual_version, "CUDA_VERSION environment variable should be set in container"

    expected_version = os.environ.get("CUDA_VERSION")
    if expected_version is None:
        pytest.skip(
            "CUDA_VERSION not set - skipping version validation. "
            "Set CUDA_VERSION env var to validate specific version."
        )
    assert actual_version.startswith(expected_version), (
        f"Expected CUDA_VERSION to start with {expected_version}, got {actual_version}"
    )


def test_nvidia_visible_devices(cuda_container):
    """Verify NVIDIA_VISIBLE_DEVICES is set to 'all'."""
    assert cuda_container.get_env("NVIDIA_VISIBLE_DEVICES") == "all"


def test_cuda_in_path(cuda_container):
    """Verify CUDA bin directory is in PATH."""
    assert "/usr/local/cuda/bin" in cuda_container.get_env("PATH")


def test_cuda_home(cuda_container):
    """Verify CUDA_HOME points to the CUDA toolkit directory.

    PyTorch source builds (torch.utils.cpp_extension) and Triton JIT kernel
    compilation rely on CUDA_HOME to locate the toolkit.
    """
    assert cuda_container.get_env("CUDA_HOME") == "/usr/local/cuda"


# --- CUDA Toolkit Tests ---


def test_nvcc_exists(cuda_container):
    """Verify nvcc compiler is installed."""
    result = cuda_container.run("which nvcc")
    assert result.returncode == 0
    assert "/usr/local/cuda" in result.stdout


def test_cuda_dir_exists(cuda_container):
    """Verify CUDA toolkit directory exists."""
    assert cuda_container.dir_exists("/usr/local/cuda")


# --- CUDA Library Tests ---


def test_libcudart_present(cuda_container):
    """Verify CUDA runtime library is present."""
    result = cuda_container.run("ldconfig -p | grep libcudart")
    assert result.returncode == 0, "libcudart.so not found - cuda-cudart package may be missing"


def test_libcublas_present(cuda_container):
    """Verify cuBLAS library is present."""
    result = cuda_container.run("ldconfig -p | grep libcublas")
    assert result.returncode == 0, "libcublas.so not found - libcublas package may be missing"


def test_libnccl_present(cuda_container):
    """Verify NCCL (NVIDIA Collective Communications Library) is present.

    Required for multi-GPU and distributed training with PyTorch and TensorFlow.
    Installed via libnccl package.
    """
    result = cuda_container.run("ldconfig -p | grep libnccl")
    assert result.returncode == 0, "libnccl.so not found - libnccl package may be missing"


def test_libnpp_present(cuda_container):
    """Verify NPP (NVIDIA Performance Primitives) library is present.

    Provides GPU-accelerated image, signal, and video processing primitives.
    Installed via libnpp package.
    """
    result = cuda_container.run("ldconfig -p | grep libnpp")
    assert result.returncode == 0, "libnpp.so not found - libnpp package may be missing"


def test_libcudnn_present(cuda_container):
    """Verify cuDNN library is present."""
    result = cuda_container.run("ldconfig -p | grep libcudnn")
    assert result.returncode == 0, "libcudnn.so not found - libcudnn package may be missing"


# --- PyTorch CUDA Library Tests ---


def test_libcupti_present(cuda_container):
    """Verify CUPTI (CUDA Profiling Tools Interface) library is present.

    Required by the PyTorch profiler for GPU profiling.
    Installed via cuda-cupti package.
    """
    result = cuda_container.run("ldconfig -p | grep libcupti")
    assert result.returncode == 0, "libcupti.so not found - cuda-cupti package may be missing"


def test_libcusparselt_present(cuda_container):
    """Verify cuSPARSELt (structured sparsity) library is present.

    Used by PyTorch sparse operations for structured sparsity support.
    Installed via libcusparselt0 package.
    """
    result = cuda_container.run("ldconfig -p | grep libcusparseLt")
    assert result.returncode == 0, (
        "libcusparseLt.so not found - libcusparselt0 package may be missing"
    )


def test_libcudss_present(cuda_container):
    """Verify cuDSS (direct sparse solver) library is present.

    Used by scientific and ML solvers for sparse direct solving.
    Installed via libcudss0-cuda package.
    """
    result = cuda_container.run("ldconfig -p | grep libcudss")
    assert result.returncode == 0, "libcudss.so not found - libcudss0-cuda package may be missing"


# --- CUDA Label Tests ---


def test_cuda_version_label(cuda_container):
    """Verify CUDA version label is present."""
    assert "com.nvidia.cuda.version" in cuda_container.get_labels()


def test_uv_torch_backend(cuda_container):
    """Verify torch-backend is configured in uv.toml for CUDA wheel selection.

    Uses a specific backend (e.g. cu128, cu130) rather than "auto" because
    auto detects GPU drivers at runtime, which are absent during container builds.
    Configured via uv.toml (not ENV) to avoid uv erroring on empty values.
    """
    result = cuda_container.run("cat /etc/uv/uv.toml")
    assert result.returncode == 0, "Failed to read /etc/uv/uv.toml"
    assert "torch-backend" in result.stdout, (
        "torch-backend should be configured in /etc/uv/uv.toml for CUDA images"
    )
    # Verify it's set to a valid CUDA backend (cuNNN format), not "auto" or "cpu"
    match = re.search(r'torch-backend\s*=\s*"(cu\d+)"', result.stdout)
    assert match, f'Expected torch-backend = "cuNNN" in uv.toml, got:\n{result.stdout}'
    # If UV_TORCH_BACKEND is set in the test environment, verify the exact value matches
    expected_backend = os.environ.get("UV_TORCH_BACKEND")
    if expected_backend is not None:
        assert match.group(1) == expected_backend, (
            f'Expected torch-backend = "{expected_backend}", got "{match.group(1)}"'
        )


def test_accelerator_label_cuda(cuda_container):
    """Verify accelerator label is 'cuda' for CUDA image."""
    assert cuda_container.get_labels().get("com.opendatahub.accelerator") == "cuda"
