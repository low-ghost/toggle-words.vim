" toggle_words.vim
" AUTHOR: Mike Bagwell
" Based on: ToggleWord by Vincent Wang, a Vimscript implementation w/ contributions by
" Fergus Bremner and Jeremy Cantrell
" This python version does forward and backward word search on the current
" line and allows both incrementing and decrementing words based on
" commands and mappings (via plug, no default mappings provided)

"if exists("g:load_toggle_words")
   "finish
"endif

let s:keepcpo= &cpo
set cpo&vim

let g:load_toggle_words = "1"
let s:toggle_words_dict = {'*': [
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
    \ ], }

if exists('g:toggle_words_dict')
  for key in keys(g:toggle_words_dict)
    if has_key(s:toggle_words_dict, key)
      call extend(s:toggle_words_dict[key], g:toggle_words_dict[key])
    else
      let s:toggle_words_dict[key] = g:toggle_words_dict[key]
    endif
  endfor
endif

exe 'py3file ' . escape(escape(expand('<sfile>:p:h'), '\'), ' ').'/toggle-words.py'

function! s:toggle_word(dir, dec)
  let cur_filetype = &filetype
  if !has_key(s:toggle_words_dict, cur_filetype)
    let g:toggle_words_dict_current = s:toggle_words_dict['*']
  else
    let g:toggle_words_dict_current = s:toggle_words_dict[cur_filetype] + s:toggle_words_dict['*']
  endif
	if (a:dir)
    if (a:dec)
      python toggle_word(True, True)
      silent! call repeat#set("\<Plug>ToggleWordReverseDecrement")
    else
      python toggle_word(True, False)
      silent! call repeat#set("\<Plug>ToggleWordReverse")
    endif
	else
    if (a:dec)
      python toggle_word(False, True)
      silent! call repeat#set("\<Plug>ToggleWordDecrement")
    else
      python toggle_word(False, False)
      silent! call repeat#set("\<Plug>ToggleWord")
    endif
	endif
endfunction

command! ToggleWord :call <SID>toggle_word(0, 0)
command! ToggleWordDecrement :call <SID>toggle_word(0, 1)
command! ToggleWordReverse :call <SID>toggle_word(1, 0)
command! ToggleWordReverseDecrement :call <SID>toggle_word(1, 1)
nnoremap <unique> <Plug>ToggleWord :<C-U>call <SID>toggle_word(0, 0)<CR>
nnoremap <unique> <Plug>ToggleWordDecrement :<C-U>call <SID>toggle_word(0, 1)<CR>
nnoremap <unique> <Plug>ToggleWordReverse :<C-U>call <SID>toggle_word(1, 0)<CR>
nnoremap <unique> <Plug>ToggleWordReverseDecrement :<C-U>call <SID>toggle_word(1, 1)<CR>

let &cpo= s:keepcpo
unlet s:keepcpo
