" toggle_words.vim
" AUTHOR: Mike Bagwell
" Based on: ToggleWord by Vincent Wang, a Vimscript implementation w/ contributions by
" Fergus Bremner and Jeremy Cantrell
" This python version does forward and backward word search

if exists("g:load_toggle_words")
   finish
endif

let s:keepcpo= &cpo
set cpo&vim

let g:load_toggle_words = "1"
let g:_toggle_words_dict = {'*': [
    \ ['==', '!='], 
    \ ['if','else'], 
    \ ['min', 'max'], 
    \ ['start', 'stop'], 
    \ ['success', 'failure'], 
    \ ['true', 'false'],
    \ ['up', 'down'], 
    \ ['left', 'right'],
    \ ['yes', 'no'], 
    \ ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'], 
    \ ['january', 'march', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'], 
    \ ],  }

if exists('g:toggle_words_dict')
    for key in keys(g:toggle_words_dict)
        if has_key(g:_toggle_words_dict, key)
            call extend(g:_toggle_words_dict[key], g:toggle_words_dict[key])
        else
            let g:_toggle_words_dict[key] = g:toggle_words_dict[key]
        endif
    endfor
endif


function! ToggleWord()
python << EOD
import vim
import re

def iterate_words(text):
	"""find first matching word from a list of lists returning index,
		 word instance and next word"""
	word_to_change = ''
	next_word = ''
	lowest_index = 1000000
	toggle_words = vim.eval('g:_toggle_words_dict')
	for list_words in toggle_words['*']:
		for word_index, word in enumerate(list_words):
			# Perform actual find, ignoring case
			current_find_index_obj = re.search(word, text, re.IGNORECASE)
			current_find_index = current_find_index_obj.start() if current_find_index_obj != None else -1
			if current_find_index >= 0 and current_find_index < lowest_index:
				lowest_index = current_find_index
				word_to_change = current_find_index_obj.group()
				next_index = word_index + 1 if len(list_words) != word_index + 1 else 0
				next_word = list_words[next_index]
				# break out of loop if the found word is at cursor position 0
				if lowest_index == 0:
					return [ lowest_index, word_to_change, next_word ]
	return [ lowest_index, word_to_change, next_word ]

def get_word_attr(word):
	"""lower case = 0, upper case = 1, all caps = 2"""
	if word.upper() == word:
		return 2
	if word[0].upper() + word[1:] == word:
		return 1
	return 0

def get_new_word(original, new):
	"""mimic word format for replacement word"""
	word_attr = get_word_attr(original)
	if word_attr == 2:
		return new.upper()
	if word_attr == 1:
		return new[0].upper() + new[1:]
	return new

# Get current line, row and col
current_line = vim.current.line
(row, col) = vim.current.window.cursor
# Alter col if cursor is mid-word
if current_line[col] != " " and col != 0 and current_line[col - 1] != " ":
	vim.command('normal! b')
	(row, col) = vim.current.window.cursor
forward = current_line[col:]

# Execute iterate_words and get back all info to recreate line
[ lowest_index, word_to_change, next_word ] = iterate_words(forward)
new_word = get_new_word(word_to_change, next_word)

begin = col + lowest_index
vim.current.line = current_line[:begin] + new_word + current_line[begin + len(word_to_change):]
EOD
endfunction

command! ToggleWord :call ToggleWord()
command! ToggleWordReverse :call ToggleWord()

let &cpo= s:keepcpo
unlet s:keepcpo
