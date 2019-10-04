#!/usr/bin/python3

import argparse
import re

# FUTURE: Label support for subroutine call.
#         While walking assembly, store 'label refs' (positions to overwrite)
#         and 'label positions' (positions where labels appear)
#         Once completely done, overwrite all label refs with label positions

class AssemblyInstruction(object):
    def __init__(self, format, pattern):
        self._format = format
        self._pattern = re.compile(pattern)

    def convert(self, args, line):
        match = self._pattern.match(line)
        if not match:
            return None
        result = self._format
        print(result)
        for key in self._pattern.groupindex.keys():
            part = match.group(self._pattern.groupindex[key])
            # convert to number
            if key.startswith('N'):
                num = None
                if part.lower().startswith('0x'):
                    num = int(part[2:], 16)
                elif part.lower().startswith('h'):
                    num = int(part[1:], 16)
                else:
                    num = int(part, 10)
                # validate number range
                assert num >= 0, "Negative numbers aren't allowed.  Seen in [{}].".format(line)
                if len(key) == 1:
                    assert num <= 0xF, "Overflow of 4-bit constant.  Seen in [{}].".format(line)
                elif len(key) == 2:
                    assert num <= 0xFF, "Overflow of 8-bit constant.  Seen in [{}].".format(line)
                elif len(key) == 3:
                    assert num >= 0x200, "Memory below 0x200 is reserved.  Attempt to address it seen in [{}].".format(line)
                    assert num <= 0xFFF, "Attempt to address outside end of system memory at 0xFFF.  Seen in [{}].".format(line)
                part = ('{:0>' + str(len(key)) + '}').format(hex(num)[2:]).upper()
            result = result.replace(key, part)
        return result


assembly_instructions = [
        AssemblyInstruction('6XNN', r'^[\s]*V(?P<X>[0-9a-fA-F]{1,2})[\s]*=[\s]*(?P<NN>(h|0x){0,1}[a-fA-F\d]+)'),
        ]


def bytes_from_pseudocode_line(args, line):
    for instruction in assembly_instructions:
        result = instruction.convert(args, line)
        if result is None:
            continue
        print(result)
        return result
    if args.verbose:
        print('Line matched no assembly instruction: {}'.format(line))
    return None


def bytes_from_opcode_line(args, line):
    if len(line) != 4:
        return None, None
    try:
        opcode = line.strip().upper()
        high = int(line[:2], 16)
        low  = int(line[2:], 16)
    except:
        return None, None
    if args.verbose:
        print('{}: {:>3} {:>3}'.format(opcode, high, low))
    return high, low


def main(args):
    program = bytearray()
    with open(args.infile, 'rt') as infile:
        for line in infile.readlines():
            high, low = bytes_from_opcode_line(args, line.strip())
            if high is None or low is None:
                opline = bytes_from_pseudocode_line(args, line)
                if args.verbose:
                    print('Got {} from {}'.format(opline, line))
                high, low = bytes_from_opcode_line(args, opline.strip())
            # chip-8 VM expects big-endian
            program.append(high)
            program.append(low)

    with open(args.outfile, 'wb') as outfile:
        outfile.write(program)


parser = argparse.ArgumentParser(description='')
parser.add_argument('infile')
parser.add_argument('outfile')
parser.add_argument('-v', '--verbose', action='store_true')

args = parser.parse_args()
main(args)
