# -*- coding: utf-8 -*-
import os
from binascii import unhexlify
import pytest
from bitarray import bitarray as ba, frozenbitarray
import iscc_core as ic


def test_main_type():
    assert isinstance(ic.MT.META, int)
    assert ic.MT.META == 0


def test_write_header():
    # with pytest.raises(AssertionError):
    #     ic.codec.write_header(0, 0, 0, 0)
    assert ic.encode_header(0, 0, 0, 0) == bytes([0b0000_0000, 0b0000_0000])
    assert ic.encode_header(1, 0, 0, 0) == bytes([0b0001_0000, 0b0000_0000])
    assert ic.encode_header(7, 1, 1, 1) == bytes([0b0111_0001, 0b0001_0001])
    assert ic.encode_header(8, 1, 1, 1) == bytes([0b1000_0000, 0b0001_0001, 0b0001_0000])
    assert ic.encode_header(8, 8, 1, 1) == bytes([0b1000_0000, 0b1000_0000, 0b0001_0001])


def test_read_header():
    rh = ic.codec.decode_header
    assert rh(bytes([0b0000_0000, 0b0000_0000])) == (0, 0, 0, 0, b"")
    assert rh(bytes([0b0000_0000, 0b0000_0000, 0b0000_0000])) == (0, 0, 0, 0, b"\x00")
    assert rh(bytes([0b0001_0000, 0b0000_0000])) == (1, 0, 0, 0, b"")
    assert rh(bytes([0b0111_0001, 0b0001_0001])) == (7, 1, 1, 1, b"")
    assert rh(bytes([0b1000_0000, 0b0001_0001, 0b0001_0000])) == (8, 1, 1, 1, b"")
    assert rh(bytes([0b1000_0000, 0b1000_0000, 0b0001_0001])) == (8, 8, 1, 1, b"")


def test_encode_base32():
    assert ic.encode_base32(b"") == ""
    assert ic.encode_base32(b"f") == "MY"
    assert ic.encode_base32(b"fo") == "MZXQ"
    assert ic.encode_base32(b"foo") == "MZXW6"
    assert ic.encode_base32(b"foob") == "MZXW6YQ"
    assert ic.encode_base32(b"fooba") == "MZXW6YTB"
    assert ic.encode_base32(b"foobar") == "MZXW6YTBOI"


def test_decode_base32():
    assert ic.decode_base32("") == b""
    assert ic.decode_base32("MY") == b"f"
    assert ic.decode_base32("My") == b"f"
    assert ic.decode_base32("my") == b"f"
    assert ic.decode_base32("MZXQ") == b"fo"
    assert ic.decode_base32("MZXW6") == b"foo"
    assert ic.decode_base32("MZXW6YQ") == b"foob"
    assert ic.decode_base32("MZXW6YTB") == b"fooba"
    assert ic.decode_base32("MZXW6YTBOI") == b"foobar"


def test_decode_base32_casefold():
    assert ic.decode_base32("MZXW6YTBOI") == ic.decode_base32("mZxW6ytBOI")


def test_decode_base_64():
    data = os.urandom(8)
    enc = ic.encode_base64(data)
    assert ic.decode_base64(enc) == data


def test_write_varnibble():
    with pytest.raises(ValueError):
        ic.encode_varnibble(-1)
    assert ic.encode_varnibble(0) == ba("0000")
    assert ic.encode_varnibble(7) == ba("0111")
    assert ic.encode_varnibble(8) == ba("10000000")
    assert ic.encode_varnibble(9) == ba("10000001")
    assert ic.encode_varnibble(71) == ba("10111111")
    assert ic.encode_varnibble(72) == ba("110000000000")
    assert ic.encode_varnibble(73) == ba("110000000001")
    assert ic.encode_varnibble(583) == ba("110111111111")
    assert ic.encode_varnibble(584) == ba("1110000000000000")
    assert ic.encode_varnibble(4679) == ba("1110111111111111")
    with pytest.raises(ValueError):
        ic.encode_varnibble(4680)
    with pytest.raises(TypeError):
        ic.encode_varnibble(1.0)


def test_read_varnibble():
    with pytest.raises(ValueError):
        ic.decode_varnibble(ba("0"))
    with pytest.raises(ValueError):
        ic.decode_varnibble(ba("1"))
    with pytest.raises(ValueError):
        ic.decode_varnibble(ba("011"))
    with pytest.raises(ValueError):
        ic.decode_varnibble(ba("100"))
    assert ic.decode_varnibble(ba("0000")) == (0, ba())
    assert ic.decode_varnibble(ba("000000")) == (0, ba("00"))
    assert ic.decode_varnibble(ba("0111")) == (7, ba())
    assert ic.decode_varnibble(ba("01110")) == (7, ba("0"))
    assert ic.decode_varnibble(ba("01111")) == (7, ba("1"))
    assert ic.decode_varnibble(ba("10000000")) == (8, ba())
    assert ic.decode_varnibble(ba("10000001")) == (9, ba())
    assert ic.decode_varnibble(ba("10000001110")) == (9, ba("110"))
    assert ic.decode_varnibble(ba("10111111")) == (71, ba())
    assert ic.decode_varnibble(ba("101111110")) == (71, ba("0"))
    assert ic.decode_varnibble(ba("110000000000")) == (72, ba())
    assert ic.decode_varnibble(ba("11000000000010")) == (72, ba("10"))
    assert ic.decode_varnibble(ba("110000000001")) == (73, ba())
    assert ic.decode_varnibble(ba("110000000001010")) == (73, ba("010"))
    assert ic.decode_varnibble(ba("110111111111")) == (583, ba())
    assert ic.decode_varnibble(ba("1101111111111010")) == (583, ba("1010"))
    assert ic.decode_varnibble(ba("1110000000000000")) == (584, ba())
    assert ic.decode_varnibble(ba("111000000000000001010")) == (
        584,
        ba("01010"),
    )
    assert ic.decode_varnibble(ba("1110111111111111")) == (4679, ba())
    assert ic.decode_varnibble(ba("1110111111111111101010")) == (
        4679,
        ba("101010"),
    )


def test_codec_clean():
    assert ic.iscc_clean("somecode") == "somecode"
    assert ic.iscc_clean("ISCC: SOME-CODE") == "SOMECODE"
    assert ic.iscc_clean(" SOMECODE ") == "SOMECODE"
    assert ic.iscc_clean("ISCC:") == ""


def test_codec_clean_raises_bad_scheme():
    with pytest.raises(ValueError):
        ic.iscc_clean("http://whatever")


def test_codec_clean_raises_multiple_colom():
    with pytest.raises(ValueError):
        ic.iscc_clean("ISCC:something:something")


def test_code_properties():
    c64 = ic.Code(ic.gen_meta_code("Hello World")["iscc"])
    c256 = ic.Code(ic.gen_meta_code("Hello World", bits=256)["iscc"])
    assert c64.code == "AAAWN77F727NXSUS"
    assert c256.code == "AADWN77F727NXSUSUVDFOUS64JFPMZ4GAR5NJ3O5P563LTMXWS5XNSQ"
    assert c64.bytes == unhexlify(c64.hex)
    assert c64.type_id == "META-NONE-V0-64"
    assert c64.explain == "META-NONE-V0-64-" + c64.hash_hex
    assert isinstance(c64.hash_ints[0], int)
    assert c64.hash_bits == "".join(str(i) for i in c64.hash_ints)
    assert c256.hash_bits == "".join(str(i) for i in c256.hash_ints)
    assert c64.hash_uint == 7421903593216395922
    assert (
        c256.hash_uint
        == 46588043924851280427026156359332814243502099936826263036193519252570625504970
    )

    assert c64.hash_base32 == "M376L7V63PFJE"
    assert c64.base32hex == "000MDVV5VQVDNIKI"
    assert c64.hash_base32 == "M376L7V63PFJE"
    assert c64.mf_base32hex == "vpg0g00b6vvivtfmrpa90"
    assert c64.maintype == ic.MT.META
    assert c64.maintype == 0
    assert c64.subtype == ic.ST.NONE
    assert c64.subtype == 0
    assert c64.version == ic.VS.V0
    assert c64.length == 64
    assert c256.length == 256
    assert c64 ^ c64 == 0
    with pytest.raises(ValueError):
        _ = c64 ^ c256
    assert c64 == ic.Code(c64.bytes)
    assert c64 == ic.Code(c64.code)
    assert c64 == ic.Code(tuple(c64))
    assert isinstance(c64.hash_ba, frozenbitarray)
    icode = ic.Code("KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY")
    assert icode.type_id == "ISCC-TEXT-V0-MCDI"


def test_code_hashable():
    code = ic.Code.rnd(ic.MT.META)
    assert code in {code}


def test_Code_uri():
    mco = ic.Code(ic.gen_meta_code("This is an URI representation of a Meta-Code")["iscc"])
    assert mco.code == "AAAX334V4AMT2PP4"
    assert mco.uri == "ISCC:AAAX334V4AMT2PP4"


def test_Code_mf_base16():
    mco = ic.Code(ic.gen_meta_code("Hello base16")["iscc"])
    assert mco.code == "AAATKVHH3C7FOAAZ"
    assert mco.mf_base16 == "fcc0100013554e7d8be570019"
    assert ic.iscc_normalize("fcc0100013554e7d8be570019") == "ISCC:AAATKVHH3C7FOAAZ"


def test_Code_mf_base32():
    mco = ic.Code(ic.gen_meta_code("Hello base32")["iscc"])
    assert mco.code == "AAAQKV7H7K7VMAEL"
    assert mco.mf_base32 == "bzqaqaaifk7t7vp2wacfq"
    assert ic.iscc_normalize("bzqaqaaifk7t7vp2wacfq") == "ISCC:AAAQKV7H7K7VMAEL"


def test_Code_mf_base58btc():
    mco = ic.Code(ic.gen_meta_code("Hello base58btc")["iscc"])
    assert mco.code == "AAA2O57HTG7HMCO3"
    assert mco.mf_base58btc == "z4rHVQUrFdpfYWuGLa"
    assert ic.iscc_normalize("z4rHVQUrFdpfYWuGLa") == "ISCC:AAA2O57HTG7HMCO3"


def test_Code_mf_base64url():
    mco = ic.Code(ic.gen_meta_code("This is a base64url encoded Meta-Code")["iscc"])
    assert mco.code == "AAAYSN37BCO2L3O7"
    assert mco.mf_base64url == "uzAEAAYk3fwidpe3f"
    assert ic.iscc_normalize("uzAEAAYk3fwidpe3f") == "ISCC:AAAYSN37BCO2L3O7"


def test_Code_raises():
    with pytest.raises(ValueError):
        ic.Code(13)


def test_Code_Code():
    code = ic.Code.rnd(ic.MT.META)
    assert ic.Code(code) == code


def test_Code_str_repr():
    mco = ic.Code(ic.gen_meta_code("Hello str")["iscc"])
    assert mco.code == "AAAWH7PF7473PQ57"
    assert str(mco) == "AAAWH7PF7473PQ57"
    assert repr(mco) == 'Code("AAAWH7PF7473PQ57")'
    assert bytes(mco).hex() == "000163fde5ff3fb7c3bf" == mco.bytes.hex()


def test_decompose_single_component():
    mts = (
        ic.MT.META,
        ic.MT.CONTENT,
        ic.MT.DATA,
        ic.MT.INSTANCE,
    )
    for mt in mts:
        code = ic.Code.rnd(mt=mt)
        assert ic.iscc_decompose(code.code)[0] == code.code


def test_decompose_data_instance():
    data = "GABTMCHNLCHTI2NHZFXOLEB53KSPU"
    inst = "IAB3GN6WUSNSX3MJBT6PBTVFAQZ7G"
    code = ic.gen_iscc_code_v0([data, inst])["iscc"]
    assert code == "ISCC:KUADMCHNLCHTI2NHWM35NJE3FPWYS"
    assert ic.iscc_decompose(code) == ["GAATMCHNLCHTI2NH", "IAA3GN6WUSNSX3MJ"]


def test_decompose_content_data_instance():
    cont = "EMARIURG4CVZ3M7N"
    data = "GAA7ER72LMA6IOIO"
    inst = "IAAX3C2BUFV6XPQV"
    di = [cont, data, inst]
    code = ic.gen_iscc_code_v0([cont, data, inst])["iscc"]
    assert code == "ISCC:KMARIURG4CVZ3M7N6JD7UWYB4Q4Q47MLIGQWX256CU"
    assert ic.iscc_decompose(code) == di


def test_decompose_meta_content_data_instance():
    meta = "AAA4CPEJKZZ7A4HZ"
    cont = "EEAWM2CZ44CHDRHV"
    data = "GAA2F344YTSCRKBD"
    inst = "IAA4FWMY2ANPAYWJ"
    di = [meta, cont, data, inst]
    code = ic.gen_iscc_code_v0([meta, cont, data, inst])["iscc"]
    assert code == "ISCC:KEC4CPEJKZZ7A4HZMZUFTZYEOHCPLIXPTTCOIKFIEPBNTGGQDLYGFSI"
    assert ic.iscc_decompose(code) == di


def test_decompose_invalid():
    body = os.urandom(16)
    with pytest.raises(ValueError):
        ic.encode_component(ic.MT.ISCC, ic.ST_ISCC.TEXT, 0, 128, body)


def test_decompose_str_of_codes():
    mco = ic.Code.rnd(ic.MT.META)
    cco = ic.Code.rnd(ic.MT.CONTENT)
    dco = ic.Code.rnd(ic.MT.DATA)
    ico = ic.Code.rnd(ic.MT.INSTANCE)
    iscc = f"ISCC:{mco.code}-{cco.code}-{dco.code}-{ico.code}"
    codes = ic.codec.iscc_decompose(iscc)
    assert codes == [mco.code, cco.code, dco.code, ico.code]


def test_Code_rnd():
    cco = ic.Code.rnd(mt=ic.MT.CONTENT, st=ic.ST_CC.TEXT, bits=256)
    assert cco.maintype == ic.MT.CONTENT
    assert cco.subtype == ic.ST_CC.TEXT
    assert ic.Code.rnd(ic.MT.ISCC, bits=128).maintype == ic.MT.ISCC
    assert ic.Code.rnd(ic.MT.ID).maintype == ic.MT.ID
    assert ic.Code.rnd(ic.MT.DATA).maintype == ic.MT.DATA


def test_nomralize_roundtrip():
    code = "ISCC:IABTRD3EMDL2W74Z4ROZTOJTT3BDY"
    assert ic.iscc_normalize(code) == code


def test_noramlize_bad_prefix():
    with pytest.raises(ValueError):
        ic.iscc_normalize("ISCC:LA22222222")


def test_normalize_single_canonical():
    n = ic.iscc_normalize("ISCC:AAATTZCKVH3S42TP")
    assert n == "ISCC:AAATTZCKVH3S42TP"


def test_normalize_single_no_scheme():
    n = ic.iscc_normalize("AAATTZCKVH3S42TP")
    assert n == "ISCC:AAATTZCKVH3S42TP"


def test_normalize_single_lower():
    n = ic.iscc_normalize("aaattzckvh3s42tp")
    assert n == "ISCC:AAATTZCKVH3S42TP"


def test_normalize_single_mixed_case():
    n = ic.iscc_normalize("AaAtTzckVh3s42tP")
    assert n == "ISCC:AAATTZCKVH3S42TP"


def test_normalize_dual():
    n = ic.iscc_normalize("GAAW2PRCRS5LNVZVIAAUVACQKXE3V44W")
    assert n == "ISCC:KUAG2PRCRS5LNVZVJKAFAVOJXLZZM"


def test_normalize_dual_dash():
    n = ic.iscc_normalize("GAAW2PRCRS5LNVZV-IAAUVACQKXE3V44W")
    assert n == "ISCC:KUAG2PRCRS5LNVZVJKAFAVOJXLZZM"


def test_clean_dual_dash():
    assert ic.iscc_clean("GAAW2PRCRS5LNVZV-IAAUVACQKXE3V44W") == "GAAW2PRCRS5LNVZVIAAUVACQKXE3V44W"


def test_normalize_dual_scheme():
    n = ic.iscc_normalize("ISCC:GAAW2PRCRS5LNVZVIAAUVACQKXE3V44W")
    assert n == "ISCC:KUAG2PRCRS5LNVZVJKAFAVOJXLZZM"


def test_normalize_dual_scheme_dash():
    n = ic.iscc_normalize("ISCC:GAAW2PRCRS5LNVZV-IAAUVACQKXE3V44W")
    assert n == "ISCC:KUAG2PRCRS5LNVZVJKAFAVOJXLZZM"


def test_normalize_triple():
    n = ic.iscc_normalize("EMAZQGH26X5XQ5HAGAA5U77EOAU2NU4YIAAU4SKRQCZZEYQD")
    assert n == "ISCC:KMAZQGH26X5XQ5HA3J76I4BJU3JZQTSJKGALHETCAM"


def test_normalize_triple_dash():
    n = ic.iscc_normalize("EMAZQGH26X5XQ5HA-GAA5U77EOAU2NU4Y-IAAU4SKRQCZZEYQD")
    assert n == "ISCC:KMAZQGH26X5XQ5HA3J76I4BJU3JZQTSJKGALHETCAM"


def test_normalize_triple_scheme():
    n = ic.iscc_normalize("ISCC:EMAZQGH26X5XQ5HAGAA5U77EOAU2NU4YIAAU4SKRQCZZEYQD")
    assert n == "ISCC:KMAZQGH26X5XQ5HA3J76I4BJU3JZQTSJKGALHETCAM"


def test_normalize_triple_scheme_dash():
    n = ic.iscc_normalize("ISCC:EMAZQGH26X5XQ5HA-GAA5U77EOAU2NU4Y-IAAU4SKRQCZZEYQD")
    assert n == "ISCC:KMAZQGH26X5XQ5HA3J76I4BJU3JZQTSJKGALHETCAM"


def test_normalize_full_scheme():
    n = ic.iscc_normalize("ISCC:KACQMIRUW6L64O2CAZCVE2HHXGBO7EFCF3C4GRFCDPD2NM53NKUCXUY")
    assert n == "ISCC:KACQMIRUW6L64O2CAZCVE2HHXGBO7EFCF3C4GRFCDPD2NM53NKUCXUY"


def test_normalize_full_scheme_lower():
    n = ic.iscc_normalize("iscc:kacqmiruw6l64o2cazcve2hhxgbo7efcf3c4grfcdpd2nm53nkucxuy")
    assert n == "ISCC:KACQMIRUW6L64O2CAZCVE2HHXGBO7EFCF3C4GRFCDPD2NM53NKUCXUY"


def test_normalize_full_no_scheme():
    n = ic.iscc_normalize("KACQMIRUW6L64O2CAZCVE2HHXGBO7EFCF3C4GRFCDPD2NM53NKUCXUY")
    assert n == "ISCC:KACQMIRUW6L64O2CAZCVE2HHXGBO7EFCF3C4GRFCDPD2NM53NKUCXUY"


def test_normalize_full_lower_no_scheme():
    n = ic.iscc_normalize("kacqmiruw6l64o2cazcve2hhxgbo7efcf3c4grfcdpd2nm53nkucxuy")
    assert n == "ISCC:KACQMIRUW6L64O2CAZCVE2HHXGBO7EFCF3C4GRFCDPD2NM53NKUCXUY"


def test_normalize_iscc_id():
    assert ic.iscc_normalize("MAAGZTFQTTVIZPJR") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_lower():
    assert ic.iscc_normalize("maagztfqttvizpjr") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_mixed():
    assert ic.iscc_normalize("MaaGZTfqttvizpjr") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_scheme():
    assert ic.iscc_normalize("ISCC:MAAGZTFQTTVIZPJR") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_scheme_lower():
    assert ic.iscc_normalize("iscc:maagztfqttvizpjr") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_iscc_id_scheme_mixed():
    assert ic.iscc_normalize("Iscc:Maagztfqttvizpjr") == "ISCC:MAAGZTFQTTVIZPJR"


def test_normalize_mf_base16_single():
    assert ic.iscc_normalize("fcc0120016c017dac75fe4613") == "ISCC:EAAWYAL5VR274RQT"


def test_normalize_mf_base32_single():
    assert ic.iscc_normalize("bzqasaalmaf62y5p6iyjq") == "ISCC:EAAWYAL5VR274RQT"


def test_normalize_mf_base58btc_single():
    assert ic.iscc_normalize("z4rHXCkYCB2k4V7uuk") == "ISCC:EAAWYAL5VR274RQT"


def test_normalize_mf_base64_url_single():
    assert ic.iscc_normalize("uzAEgAWwBfax1_kYT") == "ISCC:EAAWYAL5VR274RQT"


def test_codec_normalize_raises():
    code = ic.Code(ic.gen_meta_code("Hello", "World")["iscc"])
    bad = "f" + (b"\xcc\xff" + code.bytes).hex()
    with pytest.raises(ValueError):
        ic.iscc_normalize(bad)


def test_codec_encode_length_std_type():
    assert ic.encode_length(ic.MT.META, 64) == 1


def test_codec_encode_length_std_type_raises():
    with pytest.raises(ValueError):
        ic.encode_length(ic.MT.META, 63)


def test_codec_encode_length_iscc_type():
    assert ic.encode_length(ic.MT.ISCC, 1) == 1


def test_codec_encode_length_iscc_type_raises():
    with pytest.raises(ValueError):
        ic.encode_length(ic.MT.ISCC, 8)


def test_codec_encode_length_iscc_id():
    assert ic.encode_length(ic.MT.ID, 64) == 0


def test_codec_encode_length_iscc_id_raises():
    with pytest.raises(ValueError):
        ic.encode_length(ic.MT.ID, 32)


def test_codec_encode_length_unknown_type_raises():
    with pytest.raises(ValueError):
        ic.encode_length(8, 64)


def test_codec_encode_component_invalid_type_raises():
    with pytest.raises(ValueError):
        ic.encode_component(8, 0, 0, 64, os.urandom(8))


def test_codec_decode_length_mt_iscc():
    assert ic.decode_length(ic.MT.ISCC, 3) == 256


def test_codec_decode_length_invaid_type_raises():
    with pytest.raises(ValueError):
        ic.decode_length(8, 3)


def test_codec_Code_rnd_mt_iscc():
    assert ic.Code.rnd(ic.MT.ISCC, bits=256).maintype == ic.MT.ISCC


def test_codec_validate_regex():
    valid = ic.gen_meta_code("Hello World", bits=32)["iscc"]
    assert ic.iscc_validate(valid) is True
    invalid = valid[:-1]
    assert ic.iscc_validate(invalid, strict=False) is False
    with pytest.raises(ValueError):
        ic.iscc_validate(invalid, strict=True)


def test_codec_validate_header_prefix():
    valid = ic.gen_meta_code("Hello World", bits=32)["iscc"]
    invalid = "ISCC:AE" + valid[7:]
    assert ic.iscc_validate(invalid, strict=False) is False
    with pytest.raises(ValueError):
        ic.iscc_validate(invalid)


def test_codec_validate_iscc_id():
    assert ic.iscc_validate("ISCC:MMAMRVPW22XVU4FR", strict=False) is True


def test_codecc_validate_wrong_version():
    assert ic.iscc_validate("ISCC:CE22222222", strict=False) is False
    with pytest.raises(ValueError):
        ic.iscc_validate("ISCC:CE22222222", strict=True)


def test_decode_iscc():
    assert ic.iscc_decode("AAAQCAAAAABAAAAA") == (0, 0, 0, 1, b"\x01\x00\x00\x00\x02\x00\x00\x00")


def test_type_id_maintype_meta():
    assert ic.iscc_type_id("AAAQCAAAAABAAAAA") == "META-NONE-V0-64"


def test_type_id_maintype_iscc_code():
    iscc = "KICQOCPJM46YUUCBMWS6FFXRGM3LJOU5MZOVPOUHIJOHPI324GKN67Q"
    assert ic.iscc_type_id(iscc) == "ISCC-AUDIO-V0-MCDI"


def test_type_id_maintype_iscc_id():
    iscc = "MEAAO5JRN22FN2M2"
    assert ic.iscc_type_id(iscc) == "ID-BITCOIN-V0-64"


def test_explain_maintype_meta():
    assert ic.iscc_explain("AAAQCAAAAABAAAAA") == "META-NONE-V0-64-0100000002000000"


def test_explain_maintype_iscc_code():
    iscc = "KICQOCPJM46YUUCBMWS6FFXRGM3LJOU5MZOVPOUHIJOHPI324GKN67Q"
    assert (
        ic.iscc_explain(iscc)
        == "ISCC-AUDIO-V0-MCDI-0709e9673d8a504165a5e296f13336b4ba9d665d57ba87425c77a37ae194df7e"
    )


def test_explain_maintype_iscc_id_no_counter():
    iscc = "MEAAO5JRN22FN2M2"
    assert ic.iscc_explain(iscc) == "ID-BITCOIN-V0-64-0775316eb456e99a"


def test_explain_maintype_iscc_id_counter():
    iscc = "ISCC:MAASAJINXFXA2SQXAE"
    assert ic.iscc_explain(iscc) == "ID-PRIVATE-V0-72-20250db96e0d4a17-1"


def test_encode_base32hex():
    assert ic.encode_base32hex(b"hello world") == "D1IMOR3F41RMUSJCCG"


def test_base32hex_roundtrip_lower():
    data = bytes.fromhex("cc01cd9d2b7d247a8333f7b0b7d2cda8056c3d15eef738c1962e9148624feac1c14f")
    expected_b32hex = "PG0SR79BFKI7L0PJUUOBFKMDL02MOF8LTRRJHGCM5Q8KGOIFTB0S2JO"
    assert ic.encode_base32hex(data) == "PG0SR79BFKI7L0PJUUOBFKMDL02MOF8LTRRJHGCM5Q8KGOIFTB0S2JO"
    assert ic.decode_base32hex(expected_b32hex.lower()) == data


def test_decode_base32hex():
    assert ic.decode_base32hex("D1IMOR3F41RMUSJCCG") == b"hello world"


def test_Code_hash_base32hex():
    iscc = "KICQOCPJM46YUUCBMWS6FFXRGM3LJOU5MZOVPOUHIJOHPI324GKN67Q"
    code = ic.Code(iscc)
    assert code.hash_base32hex == "0S4UIPPTH9842PD5SABF2CPMMIT9QPITAUT8EGISEUHNLOCKRTV0"


def test_Code_rnd_iscc_320():
    co = ic.Code.rnd(ic.MT.ISCC, bits=320)
    assert co.code == "KMD54GZXFLJ7X5D2PZNR4744UVEZ2ACK4VC2AELL4WVQYFUBZD4OHUGTFEFEZNOTFMLA"
    assert (
        co.explain
        == "ISCC-VIDEO-V0-MSCDI-de1b372ad3fbf47a7e5b1e7f9ca5499d004ae545a0116be5ab0c1681c8f8e3d0d3290a4cb5d32b16"
    )


def test_Code_rnd_iscc_256():
    co = ic.Code.rnd(ic.MT.ISCC, bits=256)
    assert co.code == "KEDJCSDCJ7VMDQKPGDU4LTAQD66MZXWXGPULIIPK5NJUBF6KXLZYS6Q"
    assert (
        co.explain
        == "ISCC-IMAGE-V0-MSDI-9148624feac1c14f30e9c5cc101fbcccded733e8b421eaeb534097cabaf3897a"
    )


def test_Code_rnd_iscc_192():
    co = ic.Code.rnd(ic.MT.ISCC, bits=192)
    assert co.code == "KECHFLRCISFQCY6BZWOSW7JEPKBTH55QW7JM3KAFNQ"
    assert co.explain == "ISCC-IMAGE-V0-MDI-72ae22448b0163c1cd9d2b7d247a8333f7b0b7d2cda8056c"


def test_Code_rnd_iscc_128():
    co = ic.Code.rnd(ic.MT.ISCC, bits=128)
    assert co.code == "KUAFD3YZEL7EHRE6CSMBRUIXLHW4G"
    assert co.explain == "ISCC-SUM-V0-DI-51ef1922fe43c49e149818d11759edc3"


def test_Code_rnd_iscc_64_raises():
    with pytest.raises(ValueError):
        ic.Code.rnd(ic.MT.ISCC, bits=64)


def test_iscc_code_no_content_code():
    mco = ic.Code.rnd(ic.MT.META, bits=64)
    dco = ic.Code.rnd(ic.MT.DATA, bits=64)
    ico = ic.Code.rnd(ic.MT.INSTANCE, bits=64)
    co = ic.Code(ic.gen_iscc_code_v0((mco.code, dco.code, ico.code))["iscc"])
    assert co.code == "KYCE2K455MN6WNYRD7ZZQSNU4E2X33AYR355BAHGNY"
    assert co.explain == "ISCC-NONE-V0-MDI-4d2b9deb1beb37111ff39849b4e1357dec188efbd080e66e"


def test_models_Code_rnd_custom_subtype_raises():
    with pytest.raises(ValueError):
        ic.Code.rnd(ic.MT.ISCC, st=ic.ST_ISCC.TEXT)


def test_iscc_validate_base_encoding_error():
    sample = "ISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ4ORJGIVHDI"
    assert ic.iscc_validate(sample, strict=False) is True

    assert ic.iscc_validate(sample[:-1], strict=False) is False

    with pytest.raises(ValueError) as excinfo:
        ic.iscc_validate(sample[:-1], strict=True)
    assert str(excinfo.value) == "Incorrect padding"


def test_iscc_validate_bad_length():
    sample = "ISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ"
    assert ic.iscc_validate(sample, strict=False) is False

    with pytest.raises(ValueError) as excinfo:
        ic.iscc_validate(sample, strict=True)
    assert str(excinfo.value) == "Header expects 32 but got 26 bytes"


def test_iscc_validate_mf_valid():
    VALID_CANONICAL = "ISCC:EAAWFH3PX3MCYB6N"
    VALID_MF_B32H = "vpg0i00b2jtnrtm1c0v6g"
    VALID_MF_B32H_P = "iscc:vpg0i00b2jtnrtm1c0v6g"
    assert ic.iscc_validate_mf(VALID_CANONICAL, strict=False) is True
    assert ic.iscc_validate_mf(VALID_MF_B32H, strict=False) is True
    assert ic.iscc_validate_mf(VALID_MF_B32H_P, strict=False) is True
    assert ic.iscc_validate_mf(VALID_CANONICAL, strict=True) is True
    assert ic.iscc_validate_mf(VALID_MF_B32H, strict=True) is True
    assert ic.iscc_validate_mf(VALID_MF_B32H_P, strict=True) is True


def test_iscc_validate_mf_invalid():
    sample = "ISCC:KACT4EBWK27737D2AYCJRAL5Z36G76RFRMO4554RU26HZ"
    assert ic.iscc_validate_mf(sample, strict=False) is False

    with pytest.raises(ValueError) as excinfo:
        ic.iscc_validate_mf(sample, strict=True)
    assert str(excinfo.value) == "Header expects 32 but got 26 bytes"

    INVALID_MF_B32H = "vpg0i00b2jtnrtm1c0v6"
    assert ic.iscc_validate_mf(INVALID_MF_B32H, strict=False) is False


def test_iscc_validate_mscdi():
    sample = "ISCC:KEDRRHYRYJ7XELW7HAO5FFGQRX75HJUKSUSZVWTTRNHTF2YL5SKP7XIUFXM4KMKXEZZA"
    assert ic.iscc_validate(sample, strict=False) is True
    assert ic.iscc_validate(sample, strict=True) is True
    with pytest.raises(ValueError) as excinfo:
        ic.iscc_validate(sample + "A", strict=True)
    assert str(excinfo.value) == "ISCC string does not match ^ISCC:[A-Z2-7]{10,68}$"
