import vim
import re

# TODO: strange error if at beginning of line. for instance 50


def iterate_words(text, direction):
    """find first matching word from a list of lists returning index,
       word instance and next word
    """
    word_to_change = ''
    next_word = ''
    index = -1 if direction else 10000000
    toggle_words = vim.eval('g:default_toggle_words_dict')
    for list_words in toggle_words['*']:
        for word_index, word in enumerate(list_words):
            # Perform actual find, ignoring case
            current_find_obj = re.search(word, text, re.IGNORECASE)
            if current_find_obj is not None:
                current_find = current_find_obj.start()
                if (not direction and current_find < index) or (
                        direction and current_find > index):
                    index = current_find
                    word_to_change = current_find_obj.group()
                    next_index = word_index + \
                        1 if len(list_words) != word_index + 1 else 0
                    next_word = list_words[next_index]
                    # break out of loop if the found word is at cursor position
                    # 0
                    if not direction and index == 0:
                        return [index, word_to_change, next_word]
    return [index, word_to_change, next_word]


def get_word_attr(word):
    """lower case = 0, upper case = 1, all caps = 2"""
    if word.upper() == word:
        return 2
    if word[0].upper() + word[1:] == word:
        return 1
    return 0


def format_new_word(original, new):
    """mimic word format for replacement word"""
    word_attr = get_word_attr(original)
    if word_attr == 2:
        return new.upper()
    if word_attr == 1:
        return new[0].upper() + new[1:]
    return new


def beginning_of_word(line):
    """Get row and col for the beginning of word under cursor"""
    (row, col) = vim.current.window.cursor
    if line[col] != " " and col != 0 and line[col - 1] != " ":
        vim.command('normal! b')
        (row, col) = vim.current.window.cursor
    return (row, col)


def ending_of_word(line):
    """Get row and col for the ending of word under cursor"""
    (row, col) = vim.current.window.cursor
    if line[col] != " " and line[col] != "\n" and line[col + 1] != " ":
        vim.command('normal! e')
        (row, col) = vim.current.window.cursor
    return (row, col)


def construct_line_by_replacement(line, begin, new, original):
    return line[:begin] + new + line[begin + len(original):]


def toggle_word(direction):
    """Main toggle words function"""
    current_line = vim.current.line

    if direction:
        (row, col) = ending_of_word(current_line)
        text = current_line[:col]
    else:
        (row, col) = beginning_of_word(current_line)
        text = current_line[col:]

    # Execute iterate_words and get back all info to recreate line
    [index, original_word, new_word] = iterate_words(text, direction)
    formatted_new_word = format_new_word(original_word, new_word)

    begin = index if direction else col + index
    vim.current.line = construct_line_by_replacement(
        current_line, begin, formatted_new_word, original_word)
    vim.command("call cursor(%s, %s)" % (row, begin + 1))