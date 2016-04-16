" toggle_words.vim
" AUTHOR: Mike Bagwell
" Based on: ToggleWord by Vincent Wang, a Vimscript implementation w/ contributions by
" Fergus Bremner and Jeremy Cantrell
" This python version does forward and backward word search

"if exists("g:load_toggle_words")
   "finish
"endif

let s:keepcpo= &cpo
set cpo&vim

let g:load_toggle_words = "1"
let g:default_toggle_words_dict = {'*': [
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
    \ ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'], 
    \ ],  }

if exists('g:toggle_words_dict')
    for key in keys(g:toggle_words_dict)
        if has_key(g:default_toggle_words_dict, key)
            call extend(g:default_toggle_words_dict[key], g:toggle_words_dict[key])
        else
            let g:default_toggle_words_dict[key] = g:toggle_words_dict[key]
        endif
    endfor
endif

pyfile ./toggle-words.py

function! ToggleWord(dir)
	if (a:dir)
    python toggle_word(True)
		silent! call repeat#set("\<Plug>ToggleWordReverse")
	else
    python toggle_word(False)
		silent! call repeat#set("\<Plug>ToggleWord")
	endif
endfunction

command! ToggleWord :call ToggleWord(0)
command! ToggleWordReverse :call ToggleWord(1)
nnoremap <unique> <Plug>ToggleWord :<C-U>call ToggleWord(0)<CR>
nnoremap <unique> <Plug>ToggleWordReverse :<C-U>call ToggleWord(1)<CR>

let &cpo= s:keepcpo
unlet s:keepcpo
