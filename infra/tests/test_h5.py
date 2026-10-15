"""Tests for galleria.h5.list_frames: which files of an output directory are frames."""

import pytest

from galleria.h5 import list_frames


def _touch(directory, names):
    for name in names:
        (directory / name).write_bytes(b"")


def _names(paths):
    return [p.rsplit("/", 1)[-1] for p in paths]


def test_orders_ite_frames_numerically_with_init_first(tmp_path):
    _touch(tmp_path, ["kh_hllc_ite_10.h5", "kh_hllc_ite_2.h5", "kh_hllc_init.h5", "kh_hllc_ite_0.h5"])
    assert _names(list_frames(str(tmp_path), "kh_hllc")) == [
        "kh_hllc_init.h5",
        "kh_hllc_ite_0.h5",
        "kh_hllc_ite_2.h5",
        "kh_hllc_ite_10.h5",
    ]


def test_orders_zero_padded_frames(tmp_path):
    _touch(tmp_path, ["advection_2d_0002.h5", "advection_2d_0000.h5", "advection_2d_0001.h5"])
    assert _names(list_frames(str(tmp_path), "advection_2d")) == [
        "advection_2d_0000.h5",
        "advection_2d_0001.h5",
        "advection_2d_0002.h5",
    ]


def test_ignores_restart_dumps_and_diagnostics(tmp_path):
    # samurai-euler writes a restart dump next to every frame since Sep 2026.
    _touch(
        tmp_path,
        [
            "kh_hllc_init.h5",
            "kh_hllc_ite_0.h5",
            "kh_hllc_restart_init.h5",
            "kh_hllc_restart_ite_0.h5",
            "kh_hllc_restart.h5",
            "kh_hllc_diverged.h5",
        ],
    )
    assert _names(list_frames(str(tmp_path), "kh_hllc")) == ["kh_hllc_init.h5", "kh_hllc_ite_0.h5"]


def test_digits_inside_the_prefix_do_not_count(tmp_path):
    _touch(tmp_path, ["riemann2d_config3_hllc_ite_1.h5", "riemann2d_config3_hllc_ite_0.h5"])
    assert _names(list_frames(str(tmp_path), "riemann2d_config3_hllc")) == [
        "riemann2d_config3_hllc_ite_0.h5",
        "riemann2d_config3_hllc_ite_1.h5",
    ]


def test_another_prefix_is_not_a_frame(tmp_path):
    # "kh" must not pick up the frames of "kh_hllc".
    _touch(tmp_path, ["kh_hllc_ite_0.h5"])
    with pytest.raises(FileNotFoundError):
        list_frames(str(tmp_path), "kh")
