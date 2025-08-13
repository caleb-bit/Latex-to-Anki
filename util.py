import math


def get_next_token(s):
    s = s.lstrip()
    if s.startswith('{'):
        return extract_bracketed(s)
    else:
        # the new command is not in brackets, starts with '\'
        idx1 = first_occurrence(s, '{')
        idx2 = first_occurrence(s[1:], '\\') + 1
        idx3 = first_occurrence(s, '[')
        idx = min(idx1, idx2, idx3)
        if idx == math.inf:
            return s, ""
        return s[:idx], s[idx:]


def get_num_args(s):
    s = s.strip()
    if s[0] == '[':
        num_args, rest = extract_bracketed(s, '[', ']')
        return int(num_args), rest
    return 0, s


def get_optional_arg(s):
    if s[0] == '[':
        return extract_bracketed(s, '[', ']')
    return None, s


def extract_bracketed(s, bracket_left='{', bracket_right='}', return_unbracketed = True):
    """
    Returns the stripped version of the content inside the first bracket group encountered and the remaining text outside the group.

    If return_unbracketed is true, if the bracket group does not appear, we return the first token and the rest. Otherwise, we return [None,s]
    """
    idx1 = s.find(bracket_left)
    if idx1 == -1:
        if return_unbracketed:
            token = s.split()[0]
            return token, s[len(token):]
        else:
            return None,s
    num_brackets = 1
    curr_idx = idx1 + 1
    while curr_idx < len(s) and num_brackets > 0:
        c = s[curr_idx]
        if c == bracket_left:
            num_brackets += 1
        elif c == bracket_right:
            num_brackets -= 1
        curr_idx += 1
    if num_brackets == 0:
        return s[idx1 + 1: curr_idx - 1], s[curr_idx:]
    return s[idx1 + 1:].strip(), ""


def text_in_env(env_name, text_content):
    """
    Finds the first instance of [env_name] environment and returns the name (if applicable), contained content, and the remainder of the text.
    """
    begin_str = "\\begin{" + env_name + "}"
    end_str = "\\end{" + env_name + "}"
    begin_idx = first_occurrence(text_content, begin_str) + len(begin_str)
    end_idx = first_occurrence(text_content, end_str)
    inside_text = text_content[begin_idx:end_idx].strip()
    if inside_text[0] == '[':
        name, rest = extract_bracketed(inside_text, '[', ']', False)
    else:
        name = None
        rest = inside_text
    return name, rest, text_content[end_idx + len(end_str):]


def first_occurrence(text, substring):
    idx = text.find(substring)
    if idx == -1:
        return math.inf
    return idx
