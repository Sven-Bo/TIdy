#@title TI Class
from defaults import DEFAULT_OUTDIR, DEFAULT_TAB


def is_comment(line):
    """
    Determine if a line is a comment
    """
    strip = line.strip()
    if len(strip) > 0:
        if strip[0] == '#':
            return True
    else:
        return False


def is_blank(line):
    """
    Determine if a line is a comment
    """
    if line.strip() == '':
        return True
    else:
        return False

def is_hash(line):
    """
    Determine if a line is entirely hash. E.g. ###############
    Line must have at least one hash, but not no other characters
    :param line:
    :return:
    """
    import re
    if '#' in line:
        if re.sub('#', '', line).strip() == '':
            return True
    return False


class TI(object):
    """
    A python class for tidying up TM1 TurboIntegrator Processes
    """

    def __init__(self, intext, tab = DEFAULT_TAB, outdir = DEFAULT_OUTDIR, outfile = 'out.ti', part = 'Unknown'):
        """
        Initialize TI object in python
        """
        self.intext = intext
        self.outtext = self.intext
        self.tab = tab
        self.outdir = outdir
        self.outfile = outfile
        self.part = part

    def set_tab(self, tab_str):
        self.tab = tab_str

    def set_outdir(self, outdir_str):
        self.outdir = outdir_str

    def set_outfile(self, outfile_str):
        self.outfile = outfile_str

    def capitalize_keywords(self):
        """
        Capitalize 7 control keywords if found at the start of a line
        """
        from defaults import KEYWORDS
        out = []
        for line in self.outtext:
            if is_comment(line) is True:
                out.append(line)
            else:
                for keyword in KEYWORDS:
                    idx = line.upper().find(keyword)
                    if idx != -1:
                        if line.strip().upper().find(keyword) == 0:
                            line = line[:idx] + keyword + line[idx + len(keyword):]
                out.append(line)
        self.outtext = out

    def capitalize_functions(self):
        """
        Capitalize ~150 reserved TI function names
        """
        from defaults import FUNCTION_NAMES
        out = []
        for line in self.outtext:
            if is_comment(line) is True:
                out.append(line)
            else:
                for keyword in FUNCTION_NAMES:
                    idx = line.upper().find(keyword.upper())
                    # Keyword must be preceded by a space if not at start of line:
                    if idx != -1 and line[idx-1] == ' ':
                        line = line[:idx] + keyword + line[idx + len(keyword):]
                    # Else keyword must be followed closely by '('
                    if idx == 1 and '(' in line[idx+len(keyword) : idx+len(keyword)+3]:
                        line = keyword + line[idx + len(keyword):]
                out.append(line)
        self.outtext = out

    def indent(self):
        """
        Add indentation
        """
        level = 0
        out = []
        tab = self.tab
        for line in self.outtext:
            line = line.lstrip()
            if line.startswith('END') or line.startswith('ENDIF') or line.startswith('ELSE'):
                level -= 1
            out.append(tab * level + line)
            if line.startswith('WHILE') or line.startswith('IF') or line.startswith('ELSEIF') or line.startswith('ELSE'):
                level += 1
        self.outtext = out

    def remove_trailing_whitespace(self):
        self.outtext = [x.rstrip() for x in self.outtext]


    def space_operators(self):
        """
        Disabled: Need to make sure "<>" doesn't return "< >" nor "@=" returns "@ =", etc.
        :return:
        """
        from defaults import OPERATORS
        out = []
        for line in self.outtext:
            if is_comment(line) is True:
                out.append(line)
            else:
                idx_list = [line.find(operator) for operator in OPERATORS]
                if sum(idx_list) != len(OPERATORS)*-1:
                    # Determine the correct operator
                    operator = ""
                    for i in range(len(OPERATORS)):
                        if idx_list[i] >= 0 and len(OPERATORS[i]) > len(operator):
                            operator = OPERATORS[i]
                    # Add spacing
                    idx = line.find(operator)
                    if idx != -1:
                        if line[idx + len(operator)] != ' ':
                            line = line[:idx] + operator + ' ' + line[idx + len(operator):]
                        if line[idx - 1] != ' ':
                            line = line[:idx] + ' ' + operator + line[idx + len(operator):]
                out.append(line)
        self.outtext = out

    def enforce_max_blank_lines(self):
        from defaults import MAX_CONSECUTIVE_BLANK_LINES
        out = []
        consecutive_blanks = 0
        for line in self.outtext:
            if is_blank(line):
                consecutive_blanks += 1
                if consecutive_blanks <= MAX_CONSECUTIVE_BLANK_LINES:
                    out.append(line)
            else:
                consecutive_blanks = 0
                out.append(line)
        self.outtext = out


    def remove_hash_lines(self):
        out = []
        for line in self.outtext:
            if is_hash(line) is False:
                out.append(line)
        self.outtext = out


    def tidy(self):
        self.capitalize_keywords()
        self.capitalize_functions()
        self.remove_trailing_whitespace()
        self.space_operators()
        self.indent()
        self.enforce_max_blank_lines()
        self.remove_hash_lines()


    def generate_output(self):
        """
        Write out_text to outfile
        """
        with open(self.outdir + '/' + self.outfile, 'w') as f:
            for line in self.outtext:
                f.write("%s\n" % line)

    def print_output(self):
        """
        Print output
        """
        for line in self.outtext:
            print(line)