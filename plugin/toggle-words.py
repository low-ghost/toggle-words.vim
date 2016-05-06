"""Toggle Words, ctrl-a for word pairs and sets.

Provides ctrl-a like toggling functionality to word pairs or sets.
TODO: Something a little off with reverse vim words.
"""
import vim
import re
from difflib import Differ


def escape_vim_text(text):
    """Escape single and double quotes."""
    return text.replace("'", "\\'").replace('"', '\\"')


def vim_match(text, test, method=None, unescaped=None):
    """Perform match or matchend in vim."""
    to_match = text if unescaped is None else escape_vim_text(text)

    if method == 'end':
        return int(vim.eval('matchend("%s", \'%s\')' % (to_match, test)))
    if method == 'list':
        return vim.eval('matchlist("%s", \'%s\')' % (to_match, test))
    return int(vim.eval('match("%s", \'%s\')' % (to_match, test)))


def vim_substitute(text, search, replace):
    """Perform actual vim substitution."""
    return vim.eval('substitute("%s", \'%s\', \'%s\', \'\')'
                    % (escape_vim_text(text), search, replace))


def vim_get_match_diff(escaped_text, test):
    """Diff of full match and match groups for capitalization reference."""
    match_list = vim_match(escaped_text, test, 'list')
    full_match, parts = match_list[0], ''.join(match_list[1:])
    diff = list(Differ().compare(parts, full_match))

    return ''.join([i[2:] if i[:1] == '+' else '' for i in diff
                    if not i[:1] in '-?'])


def vim_find_match_info(text, to_find):
    """Find for vim.

    returns [test, match_content, start, end]
    """
    test, to_replace = to_find[0], to_find[1]
    escaped = escape_vim_text(text)
    start = vim_match(escaped, test)

    if start > -1:
        match_content = vim_get_match_diff(escaped, test) \
            if len(to_find) > 2 else to_find[0]
        return [test, match_content, start, vim_match(escaped, test, 'end')]

    return [test, to_replace, None, None]


def python_find_match_info(text, to_find):
    """Find for python.

    returns [test, match_content, start, end]
    """
    # Perform actual find, ignoring case
    current_find_obj = re.search(re.escape(to_find), text, re.IGNORECASE)

    return [
        to_find,
        current_find_obj.group(),
        current_find_obj.start(),
        current_find_obj.end()
    ] \
        if current_find_obj is not None \
        else [to_find, to_find, None, None]


def get_next_index_wrap(decrement, word_index, len_list_words):
    """Wrap dec or inc around word index.

    If last, use first or vice versa.
    """
    if decrement:
        return word_index - 1 \
            if word_index - 1 >= 0 else len_list_words - 1

    return word_index + 1 \
        if len_list_words != word_index + 1 else 0


def find_closest_matching_word_in_line(text, direction, decrement, end_case):
    """Find first matching word from a list of lists.

    Returns index, word instance or next word.
    """
    return_dict = {
        "index": -1 if direction else 10000000,
        "match_content": None,
        "next_word": None,
        "is_substitute": False,
        "original_regex": None,
        "guide_word": None,
    }

    # Get toggle words dict from vim's global variables
    toggle_words = vim.eval('g:toggle_words_dict_current')

    for list_words in toggle_words:
        len_list_words = len(list_words)
        for word_index, to_find in enumerate(list_words):
            to_find_is_list = isinstance(to_find, list)

            # Get start and end of word, as well as regex and the word
            # with either python or vim functionality depending on list input
            [test, match_content, start, end] = \
                vim_find_match_info(text, to_find) \
                if to_find_is_list \
                else python_find_match_info(text, to_find)

            # Only replace index etc if closer to cursor (based on dir)
            if start is not None and (
                    (not direction and start < return_dict["index"]) or
                    (direction and start > return_dict["index"])):
                # Set all new values except next_word
                return_dict.update({
                    "index": start,
                    "match_content": match_content,
                    "is_substitute": to_find_is_list,
                    "original_regex": test,
                })
                next_index = get_next_index_wrap(
                    decrement, word_index, len_list_words)
                next_data = list_words[next_index]

                if isinstance(list_words[next_index], list):
                    return_dict["next_word"] = next_data[1]
                    return_dict["guide_word"] = next_data[2] \
                        if len(next_data) > 2 else None
                else:
                    return_dict["next_word"] = next_data

                # break out of loop if found word is at cursor pos. 0
                match_case = end if direction else start

                if match_case == end_case:
                    return return_dict

    return return_dict


def regex_obj_reducer(decrement):
    def regex_obj_reducer_inner(acc, list_words):
        len_list_words = len(list_words)
        for i, to_find in enumerate(list_words):
            next_word = get_next_index_wrap(decrement, i, len_list_words)
            if not isinstance(to_find, list):
                acc.update({to_find: list_words[next_word]})
            elif len(to_find) == 2:
                acc.update({to_find[0]: list_words[next_word][1]})

        return acc
    return regex_obj_reducer_inner


def format_next(before, after):
    word_attr = get_word_attr(before)
    if word_attr == 2:
        return after.upper()
    if word_attr == 1:
        return after[0].upper() + after[1:]
    return after


def inner_multiple_replace(mo, before, after):
    """ Returns index, word instance or next word. start stop"""
    return format_next(before, after)


def multiple_replace(dict, text):
    regex = re.compile("|".join(dict.keys()), re.I)
    return regex.finditer(text)


def delete_match(match='toggle_words_match'):
    vim.command('call matchdelete(%s) | redraw!' % (match))


def replace_all_matching_words(toggle_words, text, decrement):
    """Find first matching word from a list of lists.

    Returns index, stop, up, word instance and next word. stop start
    this and next word. stop start
    """
    # TODO: re.sub("r'([^a-zA-Z])orr'([^a-zA-Z])", '\1and\2', text)
    offset = 0
    finish_rest = None
    regex_object = reduce(regex_obj_reducer(decrement), toggle_words, {})
    for i in multiple_replace(regex_object, text):
        print i.re.pattern
        orig = i.group(0)
        (row, c) = vim.current.window.cursor
        col = i.start() + offset
        len_match = len(orig)
        if finish_rest is None:
            # TODO: Highlight link ToggleWords IncSearch
            vim.command('let toggle_words_match = matchaddpos("ToggleWords", \
                        [[%s, %s, %s]])| redraw!"' % (row, col + 1, len_match))
            char, to_replace_orig = vim.eval('toggle_words#get_char( \
                                        "replace match [Y/n/a/q/l]? ")')
            response = to_replace_orig.lower()

        if (finish_rest is not None or response == "\r" or response == 'y'):
            new = i.expand(regex_object[orig.lower()])
            cl = vim.current.line
            vim.current.line = construct_line(cl, col, new, orig)
            # Update accumulating offset as needed
            offset += len(new) - len(orig)
        elif char == '27' or response == 'q':
            # Exit loop early if key is esc or q
            return delete_match()

        if finish_rest is None:
            delete_match()
        if response == 'a':
            finish_rest = True


def get_word_attr(word):
    """Get specific case details of the found word.

    Lower case = 0, upper case = 1, all caps = 2.
    """
    if word.upper() == word:
        return 2
    if word[0].upper() + word[1:] == word:
        return 1
    return 0


def format_next_word(match_content, next_word, is_substitute, guide_word,
                     **kwargs):
    """Mimic word format for replacement word."""
    if is_substitute and not guide_word:
        return next_word
    word_attr = get_word_attr(match_content)
    new = guide_word or next_word
    if word_attr == 2:
        return new.upper()
    if word_attr == 1:
        return new[0].upper() + new[1:]
    return new


def beginning_of_word():
    """Get row and col for the beginning of word under cursor."""
    vim.command('normal! "_yiw')
    return vim.current.window.cursor


def ending_of_word():
    """Get row and col for the ending of word under cursor."""
    vim.command('normal! "viw\<Esc>"')
    return vim.current.window.cursor


def construct_line(line, begin, new, original):
    """Construct a line to replace the original with indexing."""
    return line[:begin] + new + line[begin + len(original):]


def get_init_data(direction):
    """Get current_line, row, col, text or end_case."""
    current_line = vim.current.line

    if direction:
        (row, col) = ending_of_word()
        return [current_line, row, col, current_line[:col + 1], col + 1]

    (row, col) = beginning_of_word()
    return [current_line, row, col, current_line[col:], 0]


def toggle_word(direction, decrement):
    """Main toggle words function.

    Checks the current line for sets of words so as to toggle the first
    matching word to the next and previous word in that set. Function
    performs action forward and backward from the current cursor position
    depending on the direction parameter.
    """
    [current_line, row, col, text, end_case] = get_init_data(direction)
    match_info = find_closest_matching_word_in_line(
        text, direction, decrement, end_case)

    # perform line replacement
    if match_info["next_word"]:
        formatted_next_word = format_next_word(**match_info)
        begin = match_info["index"] if direction else col + match_info["index"]
        if match_info["is_substitute"]:
            first_sub = vim_substitute(text, match_info["original_regex"],
                                       match_info["next_word"])
            second_sub = vim_substitute(first_sub, match_info["next_word"],
                                        formatted_next_word)
            vim.current.line = second_sub + current_line[col:] \
                if direction else current_line[:col] + second_sub
        else:
            vim.current.line = construct_line(
                current_line, begin, formatted_next_word,
                match_info["match_content"])

        vim.command("call cursor(%s, %s)" % (row, begin + 1))


def toggle_line(decrement=None):
    toggle_words = vim.eval('g:toggle_words_dict_current')
    replace_all_matching_words(toggle_words, vim.current.line, decrement)


def toggle_all_matches_in_range(decrement):
    toggle_words = vim.eval('g:toggle_words_dict_current')
    replace_all_matching_words(toggle_words, vim.current.range, decrement)
