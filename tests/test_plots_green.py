"""Unit tests for plots_green module."""

import pytest
import numpy as np
import sys
import os
import json
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plots_green import (
    order_points,
    auto_output_size,
    rotate90,
    load_progress,
    save_progress,
    get_existing_results,
    main,
)


class TestGeometry:
    """Test geometry functions."""
    
    def test_order_points(self):
        """Test corner point ordering."""
        pts = [(100, 100), (200, 100), (200, 200), (100, 200)]
        ordered = order_points(pts)
        assert ordered.shape == (4, 2)
        # TL should have smallest sum
        assert ordered[0][0] < ordered[2][0]
        assert ordered[0][1] < ordered[2][1]
    
    def test_auto_output_size(self):
        """Test automatic output size calculation."""
        pts = np.array([[0, 0], [100, 0], [100, 50], [0, 50]], dtype="float32")
        w, h = auto_output_size(pts)
        assert w == 100
        assert h == 100  # minimum enforced by auto_output_size


class TestOrientation:
    """Test orientation functions."""
    
    def test_rotate90_clockwise(self):
        """Test 90° clockwise rotation."""
        img = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        rotated = rotate90(img, 1)
        assert rotated.shape == (2, 2)
    
    def test_rotate90_full_cycle(self):
        """Test that 4 rotations return to original."""
        img = np.random.randint(0, 255, (10, 20, 3), dtype=np.uint8)
        result = img.copy()
        for _ in range(4):
            result = rotate90(result, 1)
        assert np.array_equal(result, img)


class TestProgressTracking:
    """Test progress tracking and resume functionality."""
    
    def test_save_and_load_progress(self):
        """Test saving and loading progress."""
        with tempfile.TemporaryDirectory() as tmpdir:
            processed = {"img1.jpg", "img2.jpg", "img3.jpg"}
            save_progress(tmpdir, processed)
            
            loaded = load_progress(tmpdir)
            assert loaded == processed
    
    def test_load_progress_empty(self):
        """Test loading progress when no file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loaded = load_progress(tmpdir)
            assert loaded == set()
    
    def test_get_existing_results(self):
        """Test loading existing CSV results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            with open(csv_path, 'w') as f:
                f.write("image,percent_green,rect_width,rect_height\n")
                f.write("img1.jpg,45.2,800,600\n")
                f.write("img2.jpg,52.1,800,600\n")
            
            results = get_existing_results(csv_path)
            assert len(results) == 2
            assert "img1.jpg" in results
            assert results["img1.jpg"]["percent_green"] == "45.2"
    
    def test_get_existing_results_empty(self):
        """Test loading results when no file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "nonexistent.csv")
            results = get_existing_results(csv_path)
            assert results == {}


class TestAutoSkipBehavior:
    """Test automatic skipping of already processed images."""

    def test_main_skips_images_with_existing_outputs(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        image_names = ["plot1.jpg", "plot2.jpg", "plot3.jpg"]
        for name in image_names:
            (input_dir / name).write_bytes(b"fake")

        # Pretend the first two images were already processed
        (output_dir / "plot1_rectified.jpg").write_bytes(b"")
        (output_dir / "plot2_mask.png").write_bytes(b"")

        processed_calls = []

        def fake_process_image(img_path, args, thresholds_store, allow_prev=False):
            processed_calls.append(os.path.basename(img_path))
            return "success", {
                "image": os.path.basename(img_path),
                "percent_green": "12.3",
                "rect_width": "800",
                "rect_height": "600",
            }

        monkeypatch.setattr("plots_green.process_image", fake_process_image)
        monkeypatch.setattr(sys, "argv", [
            "plots_green.py",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ])

        main()

        assert processed_calls == ["plot3.jpg"], "Only unprocessed images should run"

        csv_lines = (output_dir / "foliage_results.csv").read_text().strip().splitlines()
        assert csv_lines[0] == "image,percent_green,rect_width,rect_height"
        assert any("plot3.jpg" in line for line in csv_lines[1:])

    def test_main_processes_entire_folder(self, tmp_path, monkeypatch):
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        image_names = ["plotA.jpg", "plotB.jpg", "plotC.jpg"]
        for name in image_names:
            (input_dir / name).write_bytes(b"fake")

        processed_calls = []

        def fake_process_image(img_path, args, thresholds_store, allow_prev=False):
            processed_calls.append(os.path.basename(img_path))
            base = os.path.splitext(os.path.basename(img_path))[0]
            for suffix in ("_rectified.jpg", "_mask.png", "_overlay.jpg", "_corners.json"):
                (output_dir / f"{base}{suffix}").write_text("dummy")
            return "success", {
                "image": os.path.basename(img_path),
                "percent_green": "42.0",
                "rect_width": "640",
                "rect_height": "480",
            }

        monkeypatch.setattr("plots_green.process_image", fake_process_image)
        monkeypatch.setattr(sys, "argv", [
            "plots_green.py",
            "--input",
            str(input_dir),
            "--output",
            str(output_dir),
        ])

        main()

        assert processed_calls == image_names
        csv_lines = (output_dir / "foliage_results.csv").read_text().strip().splitlines()
        assert len(csv_lines) == len(image_names) + 1
        for name in image_names:
            assert any(name in line for line in csv_lines[1:])

