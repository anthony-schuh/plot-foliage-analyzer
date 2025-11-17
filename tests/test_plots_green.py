"""Unit tests for plots_green module."""

import pytest
import numpy as np
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plots_green import order_points, auto_output_size, rotate90


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
        assert h == 50


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
