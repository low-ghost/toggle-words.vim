function! toggle_words#word(text)
  return ['\(^\|\A\)'.a:text.'\(\A\|$\)', '\1'.a:text.'\2', a:text]
endfunction

function! toggle_words#get_char(prompt)
  echo a:prompt
  let char = getchar()
  return [ char, nr2char(char) ]
endfunction
