import vim
import re


def escape_vim_text(text):
    """Escape single and double quotes."""
    return text.replace("'", "\\'").replace('"', '\\"')


def vim_find_match_info(text, to_find):
    """Find for vim.

    returns [test, match_content, start, end]
    """
    [test, to_replace] = to_find
    escaped_text = escape_vim_text(text)
    eval_match = 'match("%s", \'%s\')' % (escaped_text, test)
    eval_match_end = 'matchend("%s", \'%s\')' % (escaped_text, test)
    current_find_start = int(vim.eval(eval_match))
    return [
      test,
      to_replace,
      current_find_start,
      int(vim.eval(eval_match_end))
    ] \
        if current_find_start > -1 \
        else [test, to_replace, None, None]


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

    If last, use first and vice versa.
    """
    if decrement:
        return word_index - 1 \
            if word_index - 1 >= 0 else len_list_words - 1
    return word_index + 1 \
        if len_list_words != word_index + 1 else 0


def find_closest_matching_word_in_line(text, direction, decrement, end_case):
    """Find first matching word from a list of lists.

    Returns index, word instance and next word.
    """
    return_dict = {
      "index": -1 if direction else 10000000,
      "match_content": None,
      "next_word": None,
      "is_substitute": False,
      "original_regex": None,
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
                return_dict["next_word"] = list_words[next_index][1] \
                    if isinstance(list_words[next_index], list) \
                    else list_words[next_index]
                # break out of loop if found word is at cursor pos. 0
                # match_case = current_find_obj.end() if direction else index
                # print 'end_case: %s' % (end_case)
                # print 'match_case %s:' % (match_case)
                # if match_case == end_case:
                # return [index, word_to_change,
                # next_word, original_regex, is_substitute]
    return return_dict


def get_word_attr(word):
    """Get specific case details of the found word.

    Lower case = 0, upper case = 1, all caps = 2.
    """
    if word.upper() == word:
        return 2
    if word[0].upper() + word[1:] == word:
        return 1
    return 0


def format_next_word(original, new):
    """Mimic word format for replacement word."""
    word_attr = get_word_attr(original)
    if word_attr == 2:
        return new.upper()
    if word_attr == 1:
        return new[0].upper() + new[1:]
    return new


def beginning_of_word(line):
    """Get row and col for the beginning of word under cursor."""
    (row, col) = vim.current.window.cursor
    if line[col] != " " and col != 0 and line[col - 1] != " ":
        vim.command('normal! b')
        (row, col) = vim.current.window.cursor
    return (row, col)


def ending_of_word(line):
    """Get row and col for the ending of word under cursor."""
    (row, col) = vim.current.window.cursor

    if (len(line) > col + 1 and line[col] != " " and
            line[col] != "\n" and line[col + 1] != " "):
        vim.command('normal! e')
        (row, col) = vim.current.window.cursor
    return (row, col)


def construct_line_by_replacement(line, begin, new, original):
    """Construct a line to replace the original with indexing."""
    return line[:begin] + new + line[begin + len(original):]


def toggle_word(direction, decrement):
    """Main toggle words function.

    Checks the current line for sets of words so as to toggle the first
    matching word to the next or previous word in that set. Function
    performs action forward or backward from the current cursor position
    depending on the direction parameter.
    """
    current_line = vim.current.line

    if direction:
        (row, col) = ending_of_word(current_line)
        text = current_line[:col + 1]
    else:
        (row, col) = beginning_of_word(current_line)
        text = current_line[col:]

    # Execute iterate_words and get back all info to recreate line
    end_case = col + 1 if direction else 0
    match_info = find_closest_matching_word_in_line(
        text, direction, decrement, end_case)

    # perform line replacement
    if match_info["next_word"]:
        formatted_next_word = format_next_word(
            match_info["match_content"], match_info["next_word"])
        if match_info["is_substitute"]:
            eval_expr = 'substitute("%s", \'%s\', \'%s\', \'\')' \
                % (escape_vim_text(text), match_info["original_regex"], match_info["next_word"])
            replacement = vim.eval(eval_expr)
            vim.current.line = replacement + current_line[col:] \
                if direction \
                else current_line[:col] + replacement
        else:
            begin = match_info["index"] if direction else col + match_info["index"]
            vim.current.line = construct_line_by_replacement(
                current_line, begin, formatted_next_word, match_info["match_content"])
            vim.command("call cursor(%s, %s)" % (row, begin + 1))
