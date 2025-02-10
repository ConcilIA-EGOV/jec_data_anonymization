"""

"""
import glob
import random
import re
import nltk
import tqdm
from nltk.corpus import stopwords

nltk.download('stopwords')


def powerset(some_list):
    # Returns all subsets of size 0 - len(some_list) for some_list
    if len(some_list) == 0:
        return [[]]

    subsets = []
    first_element = some_list[0]
    remaining_list = some_list[1:]
    # Strategy: get all the subsets of remaining_list. For each
    # of those subsets, a full subset list will contain both
    # the original subset as well as a version of the subset
    # that contains first_element
    for partial_subset in powerset(remaining_list):
        subsets.append(partial_subset)
        subsets.append([first_element] + partial_subset[:])

    return subsets


def get_powerset(vector):
    # Function to get all the subsets of a given vector.
    power_set = [" ".join(subset) for subset in powerset(vector)[1:]]
    stop_words_pt = stopwords.words('portuguese') + ["", "-", " e", "e"]
    power_set = [i for i in power_set if i not in stop_words_pt]
    power_set.reverse()
    return power_set

AUTHOR_TOKENS = [
    "autor:",
    "requerente:",
    "requerente(s):",
    "autora:",
    "requerentes:",
    "autores:",
    "autoras:",
    "exequente:"
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
    "réus:",
    "executado:"
]

NUMBER_TOKENS = [
    "autos n°",
    "processo n.",
    "autos n°",
    "procedimento do juizado especial cível nº",
    "autos n°"
]


def starts_with_any_token_from_list(text, list_token):
    return any(text.startswith(token) for token in list_token)


def find_proc_num(text):
    tokens_find = re.findall(r"[0-9]+-[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+",
                             text)
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
    """
    Function to anonymize the given line of text.
    Here we try to find the author name, defendant and process number.
    """

    # Flags to indicate whether we found a match or not for author, part
    found_author = False
    found_part = False

    # Convert text to lowercase and remove spaces
    # and newlines in the beginning and ending.
    text = text.replace("  ", " ").lower()
    proc_text = text.strip()
    
    tokens = text.split(":")
    tokens_replace = {}

    new_token = text

    # Remove the author from the text
    # TODO: Transformar esta parte em uma função separada
    if starts_with_any_token_from_list(proc_text, AUTHOR_TOKENS):
        new_token = tokens[0] + ": AUTOR\n\n"

        found_author = True
        
        tokens = [token.strip() for token in tokens[1:]]
        for token in tokens:
            subtokens = get_powerset(token.split(" "))
            for subtoken in subtokens:

                # Check whether the subtoken is a stopword
                # Important when these words appear in the name
                # Ex: João da Silva.
                # If we consider "da" as a subtoken,
                # the code will remove it from all the text.
                tokens_replace[subtoken] = "AUTOR"

    if starts_with_any_token_from_list(proc_text, PARTE_TOKENS):
        found_part = True
        new_token = tokens[0] + ": REU\n\n"
        
        tokens = [token.strip() for token in tokens[1:]]

        for token in tokens:
            subtokens = get_powerset(token.split(" "))
            for subtoken in subtokens:
                tokens_replace[subtoken] = "REU"

    # Here we try to find and replace the process number
    found_num_proc, text_new = find_proc_num(text)

    # if we found the process number,
    # we replace it with a token.
    if found_num_proc:
        new_token = text_new

    return found_author, found_part, found_num_proc, tokens_replace, new_token


def replace_pattern(input_string, pattern, replacement):
    # Create a case-insensitive
    # regular expression pattern
    regex_pattern = re.compile(re.escape(pattern), re.IGNORECASE)
    # Use sub() method to replace the pattern
    # with the specified replacement
    result_string = regex_pattern.sub(replacement, input_string, count=0)
    return result_string


def main():

    # List files
    list_files = glob.glob("data/raw/*.txt")

    # Shuffle the list of files, to avoid order bias issues.
    random.shuffle(list_files)

    for file_path in tqdm.tqdm(list_files):
        with open(file_path, "r", encoding="utf-8") as fp:
            with open(file_path.replace("raw", "anonymized"), "w+") as fp_out:

                f_author_doc = False
                f_part_doc = False
                f_num_proc = False
                replace_tokens = {}

                # Iterate over all lines of the file.
                # TODO: alterar para que leia todas as linhas de uma vez.
                for line in fp:

                    (found_author, found_part,
                     found_num_proc, replace_token, text) = anonymize(line)

                    replace_tokens.update(replace_token)

                    # Whether the author was found where
                    # or has already been found before.
                    f_author_doc = f_author_doc or found_author
                    f_part_doc = f_part_doc or found_part
                    f_num_proc = f_num_proc or found_num_proc

                    # For each of the tokens to replace (in the whole text)
                    # Try to replace in all cases (Uppercase,
                    # lowercase, capitalize, etc.)
                    ordered_keys = list(replace_tokens.keys())
                    ordered_keys.sort(key=len, reverse=True)
                    for key in ordered_keys:
                        text = replace_pattern(text, key,
                                               replace_tokens[key])

                    fp_out.write(text)

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
