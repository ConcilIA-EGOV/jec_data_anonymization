"""

"""
import glob
import random
import re
import time

AUTHOR_TOKENS = [
    "autor:",
    "requerente:",
    "requerente(s):",
    "autora:",
    "requerentes:",
    "autores:",
    "autoras:"
]

PARTE_TOKENS = [
    "réu:",
    "ré:",
    "requerida:",
    "requerido:",
    "requeridas:",
    "requeridos:",
    "requerido(a)(s):",
    "rés:",
    "réus:"
]

NUMBER_TOKENS = [
    "autos n°",
    "processo n.",
    "autos n°",
    "procedimento do juizado especial cível nº",
    "autos n°"
]


def start_with_token_list(text, list_token):
    for token in list_token:
        if text.startswith(token):
            return True

    return False


def find_proc_num(text):
    tokens_find = re.findall(r"[0-9]+-[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", text)
    tokens_find2 = re.findall(r"[0-9]+\.[0-9]+\.[0-9]+-[0-9]+", text)
    # 090.09.003319-1
    if len(tokens_find) > 0 or len(tokens_find2) > 0:
        # print("&&&", tokens_find, tokens_find2)
        # return True
        for found_token in tokens_find + tokens_find2:
            text = text.replace(found_token, "NUMERO_PROC")
        # print(text)
        return True, text

    return False, text


def anonymize(text):
    found_author = False
    found_part = False
    proc_text = text.lower().strip()

    tokens = text.split(":")
    tokens_replace = {}

    new_token = text
    if start_with_token_list(proc_text, AUTHOR_TOKENS):
        new_token = tokens[0] + ": AUTOR\n\n"

        found_author = True
        tokens = [token.strip() for token in tokens[1:]]
        for token in tokens:
            tokens_replace[token] = "AUTOR"

    if start_with_token_list(proc_text, PARTE_TOKENS):
        found_part = True
        new_token = tokens[0] + ": REU\n\n"
        tokens = [token.strip() for token in tokens[1:]]
        for token in tokens:
            tokens_replace[token] = "REU"

    found_num_proc, text_new = find_proc_num(text)

    if found_num_proc:
        new_token = text_new

    return found_author, found_part, found_num_proc, tokens_replace, new_token


def main():
    list_files = glob.glob("data/raw/*.txt")
    random.shuffle(list_files)

    for file_path in list_files:
        with open(file_path, "r", encoding="utf-8") as fp:
            with open(file_path.replace("raw", "anonymized"), "w+") as fp_out:

                f_author_doc = False
                f_part_doc = False
                f_num_proc = False
                replace_tokens = {}

                for line in fp:
                    found_author, found_part, found_num_proc, replace_token, text = anonymize(line)

                    replace_tokens.update(replace_token)

                    f_author_doc = f_author_doc or found_author
                    f_part_doc = f_part_doc or found_part
                    f_num_proc = f_num_proc or found_num_proc

                    for key in replace_tokens:
                        text = text.replace(key.lower(), replace_tokens[key])
                        text = text.replace(key.upper(), replace_tokens[key])
                        text = text.replace(key.capitalize(), replace_tokens[key])
                        text = text.replace(key.title(), replace_tokens[key])

                    if not text.lower().strip().startswith("trato"):
                        fp_out.write(text)

                # time.sleep(0.2)
                if not f_author_doc:
                    print("-" * 10, file_path, "-" * 10)
                    print("not found author")
                if not f_part_doc:
                    print("-" * 10, file_path, "-" * 10)
                    print("not found part")
                if not f_num_proc:
                    print("-" * 10, file_path, "-" * 10)
                    print("not found num_proc")


if __name__ == '__main__':
    main()
