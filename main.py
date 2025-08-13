import math
import os


def get_input_path():
    """
    Returns the file path of an existing .tex file input by the user.
    """
    input_path = input("Enter file path of a .tex file: ")
    while True:
        if not input_path.endswith(".tex"):
            input_path = input("Not a .tex file; enter file path of a .tex file: ")
        elif not os.path.exists(os.path.dirname(input_path)):
            input_path = input("Invalid file path; enter a valid file path of a .tex file: ")
        else:
            break
    return input_path


def first_occurrence(text, substring):
    """
    Returns the index of the first character of the first occurrence of substring in text.
    Returns math.inf if none is found.
    """
    idx = text.find(substring)
    return math.inf if idx == -1 else idx


def extract_bracketed(s, bracket_left='{', bracket_right='}', return_unbracketed=True):
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
            return None, s
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


def get_shortcut(s):
    """
    Return the shortcut text and the remaining text where the shortcut
     has form '[backslash]shortcut' or {[backslash]shortcut} at the beginning of the text.
    """
    s = s.lstrip()
    if s.startswith('{'):
        return extract_bracketed(s)
    elif s.startswith('\\'):
        idx1 = first_occurrence(s, '{')
        idx2 = first_occurrence(s[1:], '\\') + 1
        idx3 = first_occurrence(s, '[')
        idx4 = first_occurrence(s, ' ')
        idx = min(idx1, idx2, idx3, idx4)
        if idx == math.inf:
            return s, ""
        return s[:idx], s[idx:]
    else:
        raise ValueError()


def get_num_args(s):
    """
    If there is a substring of form [n] at the beginning of s for an integer n, return n and rest of the string after ].
    Otherwise, return 0,s.
    """
    s = s.strip()
    if s[0] == '[':
        num_args, rest = extract_bracketed(s, '[', ']')
        return int(num_args), rest
    return 0, s


def get_optional_arg_name(s):
    """
    If there is an optional argument inside [], return it and the remaining text.
    Otherwise, return None, s.
    """
    if s[0] == '[':
        return extract_bracketed(s, '[', ']')
    return None, s


def parse_new_command(text):
    """
    Return a NewCommand object from the first latex newcommand in text.
    The text should be the string that follows [backslash]newcommand or [backslash]renewcommand
    """
    shortcut, rest = get_shortcut(text)
    num_args, rest2 = get_num_args(rest)
    optional_arg, rest3 = get_optional_arg_name(rest2)
    command, _ = extract_bracketed(rest3)
    return NewCommand(shortcut=shortcut, num_args=num_args, optional_arg=optional_arg, command_def=command)


def parse_commands(text):
    """
    Returns all commands in text
    """
    commands = []
    while True:
        idx1 = first_occurrence(text, '\\newcommand') + 11
        idx2 = first_occurrence(text, '\\renewcommand') + 13
        # todo - def, NewDocumentCommand, RenewDocumentCommand
        idx = min(idx1, idx2)
        if idx == math.inf:
            return commands
        text = text[idx:]
        commands.append(parse_new_command(text))


class NewCommand:
    def __init__(self, shortcut, num_args, optional_arg, command_def):
        self.shortcut = shortcut
        self.num_args = num_args
        self.optional_arg = optional_arg
        self.command_def = command_def


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
    rest = ' '.join(rest.split())  # convert all whitespaces to spaces
    return name, rest, text_content[end_idx + len(end_str):]


def get_optional_arg(optional_arg, curr_text):
    """
    Return the value entered for the optional argument in curr_text and the rest of the text.
    If there is none, return None, curr_text.
    """
    arg = None
    if curr_text[0] == '[':
        arg, rest = extract_bracketed(curr_text, '[', ']')
        curr_text = rest
    elif optional_arg is not None:
        arg = optional_arg
    return arg, curr_text


def get_arg(curr_text):
    """
    Return the following argument to a command shortcut in curr_text and the remaining text.
    """
    curr_text = curr_text.lstrip()
    c = curr_text[0]
    if c == '{':
        arg, rest = extract_bracketed(curr_text)
    elif c == '\\':
        arg = curr_text.split()[0]
        rest = curr_text[len(arg):]
    else:
        arg = c
        rest = curr_text[1:]
    return arg, rest


def apply_command(command, text):
    """
    Use command to replace all instances of the command shortcut with regular latex.
    """
    shortcut = command.shortcut
    num_args = command.num_args
    optional_arg = command.optional_arg
    command_def = command.command_def
    while True:
        curr_text = text
        idx = curr_text.find(shortcut)
        if idx == -1:
            break
        args = []
        prefix = text[:idx]
        curr_text = curr_text[idx + len(shortcut):].lstrip()
        opt_arg, curr_text = get_optional_arg(optional_arg, curr_text)
        if opt_arg is None:
            n = num_args
        else:
            args.append(opt_arg)
            n = num_args - 1
        for i in range(n):
            arg, curr_text = get_arg(curr_text)
            args.append(arg)
        actual_text = command_def
        for i in range(num_args):
            actual_text = replace_unescaped(f'#{i + 1}', args[i], actual_text)
        text = prefix + actual_text + curr_text
    return text


def apply_commands(commands, text):
    """
    Convert all shortcuts with regular latex in text using the provided commands.
    """
    new_text = text
    for command in commands:
        new_text = apply_command(command, new_text)
    return new_text

def replace_item_with_li(text):
    item_text = '\\item'
    idx1 = text.find(item_text)
    if idx1 == -1:
        return text
    pref = text[:idx1]
    middle = text[idx1+len(item_text):]
    idx2 = middle.find(item_text)
    end = ""
    if idx2 != -1:
        end = middle[idx2:]
        middle = middle[:idx2]
    if middle == '':
        raise ValueError("middle is empty")
    replaced_text = f'{pref}<li>{middle}</li>{end}'
    return replaced_text


def translate_list_with_env(text, env, list_tag):
    begin = '\\begin{' + env + '}'
    end = '\\end{' + env + '}'
    while begin in text:
        idx1 = text.find(begin)
        idx2 = text.find(end)
        pref = text[:idx1]
        inside = text[idx1 + len(begin):idx2]
        post = text[idx2 + len(end):]
        inside = f'<{list_tag}>{inside}</{list_tag}>'
        while '\\item' in inside:
            inside = replace_item_with_li(inside)
        text = pref + inside + post
    return text


def translate_lists(text):
    text = translate_list_with_env(text, 'enumerate', 'ol')
    text = translate_list_with_env(text, 'itemize', 'ul')
    return text


def translate(text, commands):
    """
    Uses commands to substitute shortcuts in text with regular latex.
    """
    text1 = apply_commands(commands, text)
    text2 = replace_dollar_signs(text1)
    text3 = translate_lists(text2)
    return text3


def parse_env(env, text_content, commands):
    """
    Return the content inside the first latex environment env in text_content which is translated using commands.
    """
    name, text, rest = text_in_env(env, text_content)
    translated_text = translate(text, commands)
    return translated_text, rest


def replace_unescaped(old, new, text):
    """
    Replace substring old with new in text if old is not escaped by a backslash.
    """
    idx = text.find(old)
    if idx == -1:
        return text
    if idx == 0 or text[idx - 1] != '\\':
        return text.replace(old, new)
    return replace_unescaped(old, new, text[idx + len(old):])


def replace_dollar_signs(text):
    """
    Replace dollar signs with latex delimiters.
    """
    balanced = True
    while "$$" in text:
        delimiter = "\\[" if balanced else "\\]"
        text = text.replace("$$", delimiter, 1)
        balanced = not balanced
    if not balanced:
        raise ValueError("$$ not balanced")
    replaced_str = ""
    while "$" in text:
        idx = text.find("$")
        if idx == 0 or text[idx] != '\\':
            delimiter = '\\(' if balanced else '\\)'
            replaced_str += text[:idx] + delimiter
            text = text[idx + 1:]
            balanced = not balanced
        else:
            replaced_str = text[:idx + 1]
            text = text[idx + 1:]
    return replaced_str + text


def compile_statements(commands, remaining_text, env_types):
    """
    Return a list of all (environment, statement) pairs present in remaining_text using commands for translation.
    The environment must be in env_types.
    """
    statements = []
    while True:
        indices = [first_occurrence(remaining_text, '\\begin{' + x + '}') for x in env_types]
        idx = min(indices)
        if idx == math.inf:
            break
        env = env_types[indices.index(idx)]
        statement, remaining_text = parse_env(env, remaining_text, commands)
        statements.append((env, statement))
    return statements


def count_unescaped(text, substring):
    """
    Count the number of unescaped instances of substring in text
    """
    return text.count(substring) - text.count('\\' + substring)


class Card:
    def __init__(self, is_cloze, front_text, back_text):
        self.is_cloze = is_cloze
        self.front_text = front_text
        self.back_text = back_text

def anki_bold(text):
    return f'<b>{text}</b>'


def generate_definition_cards(definition):
    """
    Return a list of cards that includes:
    1. A cloze card with all terms clozed.
    2. For each term, a basic card that requests the definition of the term.
    """
    terms = []
    cards = []
    tag = '\\textbf'
    pref = ""
    post = definition
    num_open_brackets = 0
    while tag in post:
        instance_idx = post.find(tag)
        new_pref = post[:instance_idx]
        num_open_brackets += (count_unescaped(new_pref, '\\(')
                              + count_unescaped(new_pref, '\\[')
                              - count_unescaped(new_pref, '\\)')
                              - count_unescaped(new_pref, '\\]'))
        pref += new_pref
        post = post[instance_idx + len(tag):].strip()
        if num_open_brackets != 0:
            continue  # inside math env
        if post[0] == '{':
            term, rest = extract_bracketed(post)
            post = rest
        elif post[0] == '\\':
            post = post[1:]
            term = post.split()[0]
            post = post[len(term):]
        else:
            post = post.strip()
            term = post[0]
            post = post[1:]
        terms.append(term)
        pref += anki_bold(term)
    full_def = pref + post
    for term in terms:
        cards.append(Card(False, f"Define {term}.", full_def))
    clozed = full_def
    for i in range(len(terms)):
        term = terms[i]
        cloze_text = f'c{i + 1}::{term}'
        clozed = clozed.replace(anki_bold(term), '{{' + cloze_text + '}}')
    cards.append(Card(True, clozed, ""))
    return cards


def generate_theorem_cards(theorem, proof):
    """
    Returns a list with a single basic card that requests the proof of the given theorem.
    """
    front = f"Prove the following: {theorem}"
    return [Card(False, front, proof)]


def generate_cards(statements, env_types):
    """
    :param statements: list of tuples (env type, content)
    :param env_types: list of environment types
    :return: list of strings, each representing an Anki card
    """
    idx = 0
    cards = []
    while idx < len(statements):
        env = statements[idx][0]
        if env == 'definition':
            cards += generate_definition_cards(statements[idx][1])
            idx += 1
        elif env in env_types:
            if env != 'proof':
                if idx + 1 < len(statements) and statements[idx + 1][0] == 'proof':
                    cards += generate_theorem_cards(statements[idx][1], statements[idx + 1][1])
                    idx += 2
                else:
                    idx += 1
        else:
            raise ValueError()
    return cards


def split_cards(cards):
    """
    Given cards, a list of Card objects, return (basic_cards, cloze_cards).
    basic_cards and cloze_cards contain the basic and cloze cards from cards in text form, respectively.
    """
    basic_cards = []
    cloze_cards = []
    for card in cards:
        card_text = f'\"{card.front_text}\"|\"{card.back_text}\"'
        if card.is_cloze:
            cloze_cards.append(card_text)
        else:
            basic_cards.append(card_text)
    return basic_cards, cloze_cards


def write_cards(path, cards):
    with open(path, "w") as f:
        for card in cards:
            f.write(f'{card}\n')


def main():
    """
    Given the input path name.tex, output to name_basic.txt and name_cloze.txt the basic and cloze cards generated by the input path.
    """
    input_path = get_input_path()
    basic_card_path = input_path[:-4] + "_basic.txt"
    cloze_card_path = input_path[:-4] + "_cloze.txt"
    env_types = ['definition', 'lemma', 'proposition', 'corollary', 'theorem', 'proof']
    with open(input_path, "r") as f:
        file_text = f.read()
        begin_text = '\\begin{document}'
        end_text = '\\end{document}'
        idx1 = file_text.index(begin_text)
        idx2 = file_text.index(end_text)
        commands = parse_commands(file_text[:idx1])
        remaining_text = file_text[idx1 + len(begin_text):idx2]  # text inside document
        statements = compile_statements(commands, remaining_text, env_types)
        cards = generate_cards(statements, env_types)
        basic_cards, cloze_cards = split_cards(cards)
    write_cards(basic_card_path, basic_cards)
    write_cards(cloze_card_path, cloze_cards)


if __name__ == "__main__":
    main()
