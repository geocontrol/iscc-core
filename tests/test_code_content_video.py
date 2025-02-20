# -*- coding: utf-8 -*-
import pytest
import iscc_core


def test_hash_video_v0_features():
    assert (
        iscc_core.code_content_video.soft_hash_video_v0([tuple([0] * 380)], bits=256)
        == b"\x00" * 32
    )


def test_hash_video_v0_range():
    frame_vectors = [tuple(range(380))]
    assert (
        iscc_core.code_content_video.soft_hash_video_v0(frame_vectors, bits=256).hex()
        == "528f91431f7c4ad26932fc073a28cac93f21a3071a152fc2925bdaed1d190061"
    )


def test_hash_video_v0_multiple_framevectors():
    fa = tuple([0, 1, 0, 2, 1] * 76)
    fb = tuple([1, 2, 1, 0, 2] * 76)
    frame_vectors = [fa, fb]
    assert (
        iscc_core.code_content_video.soft_hash_video_v0(frame_vectors, bits=256).hex()
        == "9230d219501e00f42664b4bd206b000c98488635b0b03c010010ee00aaf93e43"
    )


def test_code_video_v0_features():
    assert iscc_core.code_content_video.gen_video_code_v0([tuple([0] * 380)]) == {
        "iscc": "ISCC:EMAQAAAAAAAAAAAA"
    }


def test_code_video_v0_range_128():
    frame_vectors = [tuple(range(380))]
    assert iscc_core.code_content_video.gen_video_code_v0(frame_vectors, bits=128) == {
        "iscc": "ISCC:EMBVFD4RIMPXYSWSNEZPYBZ2FDFMS"
    }


def test_code_video_v0_multiple_framevectors_256():
    fa = tuple([0, 1, 0, 2, 1] * 76)
    fb = tuple([1, 2, 1, 0, 2] * 76)
    frame_vectors = [fa, fb]
    assert iscc_core.code_content_video.gen_video_code_v0(frame_vectors, bits=256) == {
        "iscc": "ISCC:EMDZEMGSDFIB4AHUEZSLJPJANMAAZGCIQY23BMB4AEABB3QAVL4T4QY"
    }


def test_code_video_multiple_framevectors_256():
    fa = tuple([0, 1, 0, 2, 1] * 76)
    fb = tuple([1, 2, 1, 0, 2] * 76)
    frame_vectors = [fa, fb]
    assert iscc_core.code_content_video.gen_video_code(frame_vectors, bits=256) == {
        "iscc": "ISCC:EMDZEMGSDFIB4AHUEZSLJPJANMAAZGCIQY23BMB4AEABB3QAVL4T4QY"
    }


def test_gen_video_code_schema_confromance():
    fa = tuple([0, 1, 0, 2, 1] * 76)
    fb = tuple([1, 2, 1, 0, 2] * 76)
    frame_vectors = [fa, fb]
    iscc_obj = iscc_core.gen_video_code_v0(frame_vectors)
    assert iscc_obj == {"iscc": "ISCC:EMAZEMGSDFIB4AHU"}


def test_empty_frame_sigs():
    with pytest.raises(ValueError, match="frame_sigs cannot be empty"):
        iscc_core.code_content_video.soft_hash_video_v0([])
