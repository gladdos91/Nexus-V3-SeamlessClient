#!/usr/bin/env python3
"""Repair only the confirmed private-getter defect in the supplied 3.1.12.0 build.

Python 3, standard library only. Never runs the DLL or overwrites the input.
This is a metadata repair, not a compiled/tested transfer-readiness release.
"""
import argparse
import hashlib
from pathlib import Path
import struct

EXPECTED_SHA256 = '3189b59cc3897a681b62c0c4e4b22767a9bee7e6a26ab57aea36950b31ffb206'
FLAGS_OFFSET = 34448  # SectorTransferEngine.get_isSeamlessSwitching MethodDef.Flags
EXPECTED_FLAGS = 0x0891


def repair(data):
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise ValueError('Unsupported DLL: SHA256 does not match the inspected 3.1.12.0 build.')
    flags, = struct.unpack_from('<H', data, FLAGS_OFFSET)
    if flags != EXPECTED_FLAGS:
        raise ValueError('Unexpected getter flags; refusing to change the file.')
    output = bytearray(data)
    # ECMA-335 MemberAccessMask 0x7: Private=1, Assembly=3.
    # Preserve static, special-name, hide-by-signature and all other flags.
    struct.pack_into('<H', output, FLAGS_OFFSET, (flags & ~0x7) | 0x3)
    return bytes(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Input and output must be different files.')
    try:
        result = repair(args.input.read_bytes())
        # Exclusive creation protects any existing output/backup as well.
        with args.output.open('xb') as stream:
            stream.write(result)
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
    print('Changed only the getter access to assembly/internal; game validation still required.')
    print('Output SHA256:', hashlib.sha256(result).hexdigest())


if __name__ == '__main__':
    main()
