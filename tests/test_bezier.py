"""Tests for bezier curve evaluation."""

import pytest

from curv.math.bezier import css_string, evaluate, get_y_at_x, hypr_string, sample_curve


class TestGetYAtX:
    """Tests for the get_y_at_x function."""

    def test_get_y_at_x_zero(self) -> None:
        """Test that x=0 returns y=0."""
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        assert get_y_at_x(0.0, (0.0, 0.0), p1, p2, (1.0, 1.0)) == pytest.approx(0.0)

    def test_get_y_at_x_one(self) -> None:
        """Test that x=1 returns y=1."""
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        assert get_y_at_x(1.0, (0.0, 0.0), p1, p2, (1.0, 1.0)) == pytest.approx(1.0)

    def test_get_y_at_x_linear(self) -> None:
        """Test that linear curve returns x for y."""
        p1 = (0.3333, 0.3333)
        p2 = (0.6666, 0.6666)
        # For a linear curve, y = x
        assert get_y_at_x(0.5, (0.0, 0.0), p1, p2, (1.0, 1.0)) == pytest.approx(
            0.5, abs=1e-3
        )

    def test_get_y_at_x_ease_in(self) -> None:
        """Test eased curve (ease-in like)."""
        p1 = (0.42, 0.0)
        p2 = (1.0, 1.0)
        # At x=0.5, y should be less than 0.5 for ease-in
        y = get_y_at_x(0.5, (0.0, 0.0), p1, p2, (1.0, 1.0))
        assert y < 0.5


class TestEvaluate:
    """Tests for the evaluate function."""

    def test_evaluate_at_t_zero(self) -> None:
        """Test that evaluate at t=0 returns p0."""
        p0 = (0.0, 0.0)
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        p3 = (1.0, 1.0)
        result = evaluate(0.0, p0, p1, p2, p3)
        assert result[0] == pytest.approx(p0[0])
        assert result[1] == pytest.approx(p0[1])

    def test_evaluate_at_t_one(self) -> None:
        """Test that evaluate at t=1 returns p3."""
        p0 = (0.0, 0.0)
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        p3 = (1.0, 1.0)
        result = evaluate(1.0, p0, p1, p2, p3)
        assert result[0] == pytest.approx(p3[0])
        assert result[1] == pytest.approx(p3[1])

    def test_evaluate_at_t_half(self) -> None:
        """Test that evaluate at t=0.5 produces reasonable results."""
        p0 = (0.0, 0.0)
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        p3 = (1.0, 1.0)
        result = evaluate(0.5, p0, p1, p2, p3)
        # Result should be between p0 and p3
        assert 0.0 <= result[0] <= 1.0
        assert 0.0 <= result[1] <= 1.0

    def test_evaluate_linear(self) -> None:
        """Test evaluate on a linear curve."""
        p0 = (0.0, 0.0)
        p1 = (0.0, 0.0)
        p2 = (1.0, 1.0)
        p3 = (1.0, 1.0)
        result = evaluate(0.5, p0, p1, p2, p3)
        # Linear curve should pass through (0.5, 0.5)
        assert result[0] == pytest.approx(0.5)
        assert result[1] == pytest.approx(0.5)


class TestSampleCurve:
    """Tests for the sample_curve function."""

    def test_sample_curve_returns_correct_length(self) -> None:
        """Test that sample_curve returns n samples."""
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        n = 50
        samples = sample_curve((0.0, 0.0), p1, p2, (1.0, 1.0), n=n)
        assert len(samples) == n

    def test_sample_curve_default_length(self) -> None:
        """Test that sample_curve returns 150 samples by default."""
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        samples = sample_curve((0.0, 0.0), p1, p2, (1.0, 1.0))
        assert len(samples) == 150

    def test_sample_curve_starts_at_origin(self) -> None:
        """Test that the first sample is at (0,0)."""
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        samples = sample_curve((0.0, 0.0), p1, p2, (1.0, 1.0), n=10)
        assert samples[0][0] == pytest.approx(0.0)
        assert samples[0][1] == pytest.approx(0.0)

    def test_sample_curve_ends_at_one_one(self) -> None:
        """Test that the last sample is at (1,1)."""
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        samples = sample_curve((0.0, 0.0), p1, p2, (1.0, 1.0), n=10)
        assert samples[-1][0] == pytest.approx(1.0)
        assert samples[-1][1] == pytest.approx(1.0)

    def test_sample_curve_points_in_bounds(self) -> None:
        """Test that all sampled points are within reasonable bounds."""
        p1 = (0.34, 1.56)
        p2 = (0.64, 1.0)
        samples = sample_curve((0.0, 0.0), p1, p2, (1.0, 1.0), n=50)
        for x, y in samples:
            assert 0.0 <= x <= 1.0
            # Y can exceed [0,1] for overshoot
            assert -0.5 <= y <= 1.5


class TestCssString:
    """Tests for the css_string function."""

    def test_css_string_format(self) -> None:
        """Test that css_string produces the correct format."""
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        result = css_string(p1, p2)
        assert result.startswith("cubic-bezier(")
        assert result.endswith(")")
        # Should have 4 numbers separated by commas and spaces
        assert result.count(",") == 3

    def test_css_string_rounding(self) -> None:
        """Test that css_string rounds to 3 decimal places."""
        p1 = (0.123456789, 0.987654321)
        p2 = (0.555555555, 0.111111111)
        result = css_string(p1, p2)
        # Check that the result contains properly rounded values
        assert "0.123" in result
        assert "0.988" in result
        assert "0.556" in result
        assert "0.111" in result

    def test_css_string_ease(self) -> None:
        """Test css_string with CSS ease preset."""
        p1 = (0.25, 0.1)
        p2 = (0.25, 1.0)
        result = css_string(p1, p2)
        assert result == "cubic-bezier(0.250, 0.100, 0.250, 1.000)"


class TestHyprString:
    """Tests for the hypr_string function."""

    def test_hypr_string_format(self) -> None:
        """Test that hypr_string produces the correct format."""
        p1 = (0.25, 0.1)
        p2 = (0.75, 0.9)
        result = hypr_string(p1, p2)
        # Should have 4 numbers separated by commas and spaces
        assert result.count(",") == 3
        # Should not have "cubic-bezier" prefix
        assert "cubic-bezier" not in result

    def test_hypr_string_rounding(self) -> None:
        """Test that hypr_string rounds to 3 decimal places."""
        p1 = (0.123456789, 0.987654321)
        p2 = (0.555555555, 0.111111111)
        result = hypr_string(p1, p2)
        assert "0.123" in result
        assert "0.988" in result
        assert "0.556" in result
        assert "0.111" in result

    def test_hypr_string_bounce(self) -> None:
        """Test hypr_string with bounce preset."""
        p1 = (0.34, 1.56)
        p2 = (0.64, 1.0)
        result = hypr_string(p1, p2)
        assert result == "0.340, 1.560, 0.640, 1.000"
