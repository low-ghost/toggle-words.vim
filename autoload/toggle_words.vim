function! toggle_words#word(text)
  return ['\(^\|\A\)'.a:text.'\(\A\|$\)', '\1'.a:text.'\2', a:text]
endfunction
