#!/usr/bin/env python3

# Copyright (C) 2020-2020 The btclib developers
#
# This file is part of btclib. It is subject to the license terms in the
# LICENSE file found in the top-level directory of this distribution.
#
# No part of btclib including this file, may be copied, modified, propagated,
# or distributed except according to the terms contained in the LICENSE file.

"Tests for the `btclib.tx_in` module."

import json
from os import path

import pytest

from btclib.exceptions import BTClibValueError
from btclib.tx import Tx
from btclib.tx_in import _TX_IN_COMPARES_WITNESS, OutPoint, TxIn
from btclib.utils import bytes_from_octets
from btclib.witness import Witness


def test_out_point() -> None:
    out_point = OutPoint()
    assert out_point.tx_id == b"\x00" * 32
    assert out_point.vout == 0xFFFFFFFF
    assert out_point.hash == int.from_bytes(out_point.tx_id, "big")
    assert out_point.n == out_point.vout
    assert out_point.is_coinbase()
    assert out_point == OutPoint.deserialize(out_point.serialize())

    tx_id = bytes.fromhex(
        "d5b5982254eebca64e4b42a3092a10bfb76ab430455b2bf0cf7c4f7f32db1c2e"
    )
    vout = 0
    out_point = OutPoint(tx_id, vout)
    assert out_point.tx_id == tx_id
    assert out_point.vout == vout
    assert out_point.hash == int.from_bytes(out_point.tx_id, "big")
    assert out_point.n == out_point.vout
    assert not out_point.is_coinbase()
    assert out_point == OutPoint.deserialize(out_point.serialize())


def test_dataclasses_json_dict_outpoint() -> None:
    fname = "d4f3c2c3c218be868c77ae31bedb497e2f908d6ee5bbbe91e4933e6da680c970.bin"
    filename = path.join(path.dirname(__file__), "test_data", fname)
    with open(filename, "rb") as binary_file_:
        temp = Tx.deserialize(binary_file_.read())

    prev_out_data = temp.vin[0].prev_out

    # dataclass
    assert isinstance(prev_out_data, OutPoint)

    # Tx to/from dict
    tx_in_dict = prev_out_data.to_dict()
    assert isinstance(tx_in_dict, dict)
    assert prev_out_data == OutPoint.from_dict(tx_in_dict)

    datadir = path.join(path.dirname(__file__), "generated_files")

    # Tx dict to/from dict file
    filename = path.join(datadir, "out_point.json")
    with open(filename, "w") as file_:
        json.dump(tx_in_dict, file_, indent=4)
    with open(filename, "r") as file_:
        tx_dict2 = json.load(file_)
    assert isinstance(tx_dict2, dict)
    assert tx_in_dict == tx_dict2


def test_invalid_outpoint() -> None:

    op = OutPoint(b"\x01" * 31, 18, check_validity=False)
    with pytest.raises(BTClibValueError, match="invalid OutPoint tx_id: "):
        op.assert_valid()

    op = OutPoint(b"\x01" * 32, -1, check_validity=False)
    with pytest.raises(BTClibValueError, match="invalid vout: "):
        op.assert_valid()

    op = OutPoint(b"\x01" * 32, 0xFFFFFFFF + 1, check_validity=False)
    with pytest.raises(BTClibValueError, match="invalid vout: "):
        op.assert_valid()

    op = OutPoint(b"\x00" * 31 + b"\x01", 0xFFFFFFFF, check_validity=False)
    with pytest.raises(BTClibValueError, match="invalid OutPoint"):
        op.assert_valid()

    op = OutPoint(b"\x00" * 32, 0, check_validity=False)
    with pytest.raises(BTClibValueError, match="invalid OutPoint"):
        op.assert_valid()


def test_tx_in() -> None:
    tx_in = TxIn()
    assert tx_in.prev_out == OutPoint()
    assert tx_in.script_sig == b""
    assert tx_in.sequence == 0
    assert tx_in.outpoint == tx_in.prev_out
    assert tx_in.scriptSig == tx_in.script_sig
    assert tx_in.nSequence == tx_in.nSequence
    assert tx_in.is_coinbase()
    assert not tx_in.is_segwit()
    tx_in2 = TxIn.deserialize(tx_in.serialize())
    assert not tx_in2.is_segwit()
    assert tx_in == tx_in2

    tx_id = bytes.fromhex(
        "d5b5982254eebca64e4b42a3092a10bfb76ab430455b2bf0cf7c4f7f32db1c2e"
    )
    vout = 0
    prev_out = OutPoint(tx_id, vout)
    script_sig = b""
    sequence = 0
    tx_in = TxIn(prev_out, script_sig, sequence)
    assert tx_in.prev_out == prev_out
    assert tx_in.script_sig == script_sig
    assert tx_in.sequence == sequence
    assert tx_in.outpoint == tx_in.prev_out
    assert tx_in.scriptSig == tx_in.script_sig
    assert tx_in.nSequence == tx_in.nSequence
    assert not tx_in.is_coinbase()
    assert not tx_in.is_segwit()
    tx_in2 = TxIn.deserialize(tx_in.serialize())
    assert not tx_in2.is_segwit()
    assert tx_in == tx_in2

    prev_out = OutPoint(
        bytes.fromhex(
            "9dcfdb5836ecfe146bdaa896605ba21222f83cd014dd47adde14fab2aba7de9b"
        ),
        1,
    )
    script_sig = b""
    sequence = 0xFFFFFFFF
    tx_in = TxIn(prev_out, script_sig, sequence)
    stack = [
        "",
        "30440220421fbbedf2ee096d6289b99973509809d5e09589040d5e0d453133dd11b2f78a02205686dbdb57e0c44e49421e9400dd4e931f1655332e8d078260c9295ba959e05d01",
        "30440220398f141917e4525d3e9e0d1c6482cb19ca3188dc5516a3a5ac29a0f4017212d902204ea405fae3a58b1fc30c5ad8ac70a76ab4f4d876e8af706a6a7b4cd6fa100f4401",
        "52210375e00eb72e29da82b89367947f29ef34afb75e8654f6ea368e0acdfd92976b7c2103a1b26313f430c4b15bb1fdce663207659d8cac749a0e53d70eff01874496feff2103c96d495bfdd5ba4145e3e046fee45e84a8a48ad05bd8dbb395c011a32cf9f88053ae",
    ]
    tx_in.witness = Witness([bytes_from_octets(v) for v in stack])
    assert tx_in.prev_out == prev_out
    assert tx_in.script_sig == script_sig
    assert tx_in.sequence == sequence
    assert tx_in.outpoint == tx_in.prev_out
    assert tx_in.scriptSig == tx_in.script_sig
    assert tx_in.nSequence == tx_in.nSequence
    assert not tx_in.is_coinbase()
    assert tx_in.is_segwit()
    tx_in2 = TxIn.deserialize(tx_in.serialize())
    assert not tx_in2.is_segwit()
    assert tx_in == tx_in2 or _TX_IN_COMPARES_WITNESS

    assert tx_in != OutPoint()

    tx_in.sequence = 0xFFFFFFFF + 1
    with pytest.raises(BTClibValueError, match="invalid sequence: "):
        tx_in.assert_valid()


def test_dataclasses_json_dict() -> None:
    fname = "d4f3c2c3c218be868c77ae31bedb497e2f908d6ee5bbbe91e4933e6da680c970.bin"
    filename = path.join(path.dirname(__file__), "test_data", fname)
    with open(filename, "rb") as binary_file_:
        temp = Tx.deserialize(binary_file_.read())

    tx_in = temp.vin[0]

    # TxIn dataclass
    assert isinstance(tx_in, TxIn)
    assert tx_in.is_segwit()
    assert tx_in.witness
    assert tx_in.witness.stack

    # TxIn dataclass to dict
    tx_in_dict = tx_in.to_dict()
    assert isinstance(tx_in_dict, dict)
    assert tx_in_dict["txinwitness"]["stack"]  # type: ignore

    # TxIn dataclass dict to file
    datadir = path.join(path.dirname(__file__), "generated_files")
    filename = path.join(datadir, "tx_in.json")
    with open(filename, "w") as file_:
        json.dump(tx_in_dict, file_, indent=4)

    # TxIn dataclass dict from file
    with open(filename, "r") as file_:
        tx_dict2 = json.load(file_)
    assert isinstance(tx_dict2, dict)
    assert tx_in_dict["txinwitness"]["stack"]  # type: ignore

    assert tx_in_dict == tx_dict2

    # TxIn dataclass from dict
    tx_in2 = TxIn.from_dict(tx_in_dict)
    assert isinstance(tx_in2, TxIn)
    assert tx_in2.is_segwit()
    assert tx_in2.witness
    assert tx_in2.witness.stack

    assert tx_in == tx_in2
