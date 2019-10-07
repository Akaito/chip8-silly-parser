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
                    #assert num >= 0x200, "Memory below 0x200 is reserved.  Attempt to address it seen in [{}].".format(line)
                    assert num <= 0xFFF, "Attempt to address outside end of system memory at 0xFFF.  Seen in [{}].".format(line)
                part = ('{:0>' + str(len(key)) + '}').format(hex(num)[2:]).upper()
            result = result.replace(key, part)
        return result


assembly_instructions = [
        # TODO : 0NNN (maybe; unofficial)
        # TODO : 00E0 (maybe; unofficial)
        AssemblyInstruction('00EE', r'^[\s]*[Rr][Ee][Tt]([Uu][Rr][Nn]){0,1}'),
        AssemblyInstruction('1NNN', r'^[\s]*[Gg][Oo]([Tt][Oo]){0,1}[:;]{0,1}[\s]*(?P<NNN>(h|0x){0,1}[a-fA-F\d]+)'),
        AssemblyInstruction('2NNN', r'^[\s]*[Dd][Oo][\s]+(?P<NNN>(h|0x){0,1}[a-fA-F\d]+)'),
        AssemblyInstruction('3XNN', r'^[\s]*[Ss][Kk][Ii][Pp][\s;:]+[Vv](?P<X>[a-fA-F\d]{1})[\s]*([Ee][Qq]([Uu][Aa][Ll](-{0,1}[Tt][Oo]){0,1}){0,1}|={1,2})[\s]*(?P<NN>(h|0x){0,1}[a-fA-F\d]+)'),
        AssemblyInstruction('4XNN', r'^[\s]*[Ss][Kk][Ii][Pp][\s;:]+[Vv](?P<X>[a-fA-F\d]{1})[\s]*([Nn][Ee]|!=)[\s]*(?P<NN>(h|0x){0,1}[a-fA-F\d]+)'),
        AssemblyInstruction('5XY0', r'^[\s]*[Ss][Kk][Ii][Pp][\s;:]+[Vv](?P<X>[a-fA-F\d]{1})[\s]*([Ee][Qq]([Uu][Aa][Ll](-{0,1}[Tt][Oo]){0,1}){0,1}|={1,2})[\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        AssemblyInstruction('6XNN', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*=[\s]*(?P<NN>(h|0x){0,1}[a-fA-F\d]+)'),
        AssemblyInstruction('7XNN', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*\+=[\s]*(?P<NN>(h|0x){0,1}[a-fA-F\d]+)'),
        AssemblyInstruction('7XNN', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*=[\s]*[Vv]\1[\s]*\+[\s]*(?P<NN>(h|0x){0,1}[a-fA-F\d]+)'),
        AssemblyInstruction('8XY0', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*=[\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        AssemblyInstruction('8XY1', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*\|=[\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        AssemblyInstruction('8XY2', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*&=[\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        AssemblyInstruction('8XY3', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*\^=[\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        AssemblyInstruction('8XY4', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*\+=[\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        AssemblyInstruction('8XY5', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*-=[\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        AssemblyInstruction('8XY6', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*>>=[\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        # TODO : 8XY6 (maybe; unofficial)
        # TODO : 8XY7 (maybe; unofficial)
        # TODO : 8XYE (maybe; unofficial)
        # TODO : 9XY0 (maybe; unofficial)
        AssemblyInstruction('ANNN', r'^[\s]*[Ii][\s]*=[\s]*(?P<NNN>(h|0x){0,1}[a-fA-F\d]+)'),
        # TODO : BNNN (maybe; unofficial)
        AssemblyInstruction('CXNN', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*=[\s]*[Rr][Aa]{0,1}[Nn][Dd]([Oo][Mm]){0,1}[\s]*&{0,1}[\s]*(?P<NN>(h|0x){0,1}[a-fA-F\d]+)'),
        AssemblyInstruction('DXYN', r'^[\s]*[Ss][Hh][Oo][Ww][\s]+(?P<N>(h|0x){0,1}[a-fA-F\d]+)[\s\w]*@[\s]*[Vv](?P<X>[a-fA-F\d]{1})[Xx,\s]*[Vv](?P<Y>[a-fA-F\d]{1})'),
        AssemblyInstruction('EX9E', r'^[\s]*[Ss][Kk][Ii][Pp][\s;:]+[Vv](?P<X>[a-fA-F\d]{1})[\s]*([Ee][Qq]([Uu][Aa][Ll](-{0,1}[Tt][Oo]){0,1}){0,1}|={1,2})[\s]*[Kk]([Ee][Yy]){0,1}'),
        AssemblyInstruction('EXA1', r'^[\s]*[Ss][Kk][Ii][Pp][\s;:]+[Vv](?P<X>[a-fA-F\d]{1})[\s]*([Nn][Ee]|!=)[\s]*[Kk]([Ee][Yy]){0,1}'),
        AssemblyInstruction('FX07', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*=[\s]*([Tt][Ii][Mm][Ee][Rr]{0,1}|[Dd][Ee][Ll][Aa][Yy])'),
        AssemblyInstruction('FX0A', r'^[\s]*[Vv](?P<X>[a-fA-F\d]{1})[\s]*=[\s]*[Kk]([Ee][Yy]){0,1}'),
        AssemblyInstruction('FX15', r'^[\s]*([Tt][Ii][Mm][Ee][Rr]{0,1}|[Dd][Ee][Ll][Aa][Yy])[\s]*=[\s]*[Vv](?P<X>[a-fA-F\d]{1})'),
        AssemblyInstruction('FX18', r'^[\s]*([Tt][Oo][Nn][Ee])[\s]*=[\s]*[Vv](?P<X>[a-fA-F\d]{1})'),
        AssemblyInstruction('FX1E', r'^[\s]*[Ii][\s]\+=[\s]*[Vv](?P<X>[a-fA-F\d]{1})'),
        AssemblyInstruction('FX29', r'^[\s]*[Ii][\s]*=[\s]*[Ss][Pp][Rr][Ii][Tt][Ee][\s]+[Vv](?P<X>[a-fA-F\d]{1})'),
        # order of FX33 and FX55 deliberately swapped since they're attempted in order
        AssemblyInstruction('FX55', r'^[\s]*[Mm][Ii][\s]*=[\s]*[Vv]0:[Vv](?P<X>[a-fA-F\d]{1})'),
        AssemblyInstruction('FX33', r'^[\s]*[Mm][Ii][\s]*=[\s]*[Vv](?P<X>[a-fA-F\d]{1})'),
        AssemblyInstruction('FX65', r'^[\s]*[Vv]0:[Vv](?P<X>[a-fA-F\d]{1})[\s]*=[\s]*[Mm][Ii]'),
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

