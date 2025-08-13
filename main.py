import math
import os
import util
from util import first_occurrence


class Command:
    def __init__(self, shortcut, optional_args, command):
        self.shortcut = shortcut
        self.optional_args = optional_args
        self.command = command


def parse_newcommand(text):
    shortcut, rest = util.get_next_token(text)
    num_args, rest2 = util.get_num_args(rest)
    optional_arg, rest3 = util.get_optional_arg(rest2)
    command, _ = util.extract_bracketed(rest3)
    # print(f"shortcut: {shortcut}, numargs: {num_args}, optional_arg: {optional_arg}, command: {command} ")
    return Command(shortcut=shortcut, optional_args=[optional_arg], command=command)


def parse_commands(text):
    commands = []
    while True:
        idx1 = first_occurrence(text, '\\newcommand') + 11
        idx2 = first_occurrence(text, '\\renewcommand') + 13
        # todo - def, NewDocumentCommand, RenewDocumentCommand
        idx = min(idx1, idx2)
        if idx == math.inf:
            return commands
        text = text[idx:]
        commands.append(parse_newcommand(text))


def handle_env(env, text_content):
    name, text, rest = util.text_in_env(env, text_content)
    print(f"{env.capitalize()}: {text}")
    print("-------------------------")
    return rest


def main():
    input_path = input("Enter file path of a .tex file: ")
    while True:
        if not input_path.endswith(".tex"):
            input_path = input("Not a .tex file; enter file path of a .tex file: ")
        elif not os.path.exists(os.path.dirname(input_path)):
            input_path = input("Invalid file path; enter a valid file path of a .tex file: ")
        else:
            break
    output_path = input_path[:-4] + ".txt"
    with open(input_path, "r") as f:
        text_content = f.read()
        # lines = text_content.split("\n")
        commands = parse_commands(text_content)
        begin_text = '\\begin{document}'
        end_text = '\\end{document}'
        idx1 = text_content.index(begin_text) + len(begin_text)
        idx2 = text_content.index(end_text)
        text_content = text_content[idx1:idx2]  # text inside document
        env_types = ['definition', 'lemma', 'proposition', 'corollary', 'theorem']
        while True:
            indices = [util.first_occurrence(text_content, '\\begin{' + x + '}') for x in env_types]
            idx = min(indices)
            if idx == math.inf:
                break
            text_content = handle_env(env_types[indices.index(idx)], text_content)


if __name__ == "__main__":
    main()
