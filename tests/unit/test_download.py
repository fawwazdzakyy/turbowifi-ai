"""
Unit tests for the Download Engine.
"""

import pytest
import os
import tempfile

from turbowifi.download.segment import create_segments, calculate_optimal_segments
from turbowifi.download.storage import StorageManager
from turbowifi.download.resume import ResumeManager
from turbowifi.download.verifier import verify_checksum
from turbowifi.download.exceptions import ChecksumMismatchError


def test_create_segments():
    segs = create_segments(1000, 4)
    assert len(segs) == 4
    assert segs[0].start_byte == 0
    assert segs[0].end_byte == 249
    assert segs[3].start_byte == 750
    assert segs[3].end_byte == 999


def test_calculate_optimal_segments():
    # Small file
    assert calculate_optimal_segments(500 * 1024, 8) == 1
    # 5MB file
    assert calculate_optimal_segments(5 * 1024 * 1024, 8) == 2
    # 50MB file
    assert calculate_optimal_segments(50 * 1024 * 1024, 8) == 8
    # 500MB file
    assert calculate_optimal_segments(500 * 1024 * 1024, 8) == 8


def test_storage_manager():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filepath = f.name

    try:
        storage = StorageManager(filepath)
        storage.allocate(100)
        assert os.path.getsize(filepath) == 100

        storage.write_chunk(50, b"TEST")
        storage.close()

        with open(filepath, "rb") as f2:
            f2.seek(50)
            assert f2.read(4) == b"TEST"
    finally:
        os.unlink(filepath)


def test_resume_manager():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filepath = f.name

    try:
        mgr = ResumeManager(filepath)
        segs = create_segments(1000, 2)
        segs[0].downloaded = 250
        segs[0].status = "DOWNLOADING"

        mgr.save_state("http://test", segs)

        loaded = mgr.load_state()
        assert loaded is not None
        assert loaded[0] == "http://test"
        assert len(loaded[1]) == 2
        assert loaded[1][0].downloaded == 250
        assert loaded[1][0].status == "DOWNLOADING"

        mgr.cleanup()
        assert not mgr.state_file.exists()
    finally:
        os.unlink(filepath)
        if os.path.exists(filepath + ".turbodownload"):
            os.unlink(filepath + ".turbodownload")


def test_verify_checksum():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filepath = f.name
        f.write(b"hello world")

    # sha256 of "hello world"
    expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    try:
        assert verify_checksum(filepath, expected)

        with pytest.raises(ChecksumMismatchError):
            verify_checksum(filepath, "badhash")
    finally:
        os.unlink(filepath)
