" Vim with all enhancements
"source $VIMRUNTIME/vimrc_example.vim

""""""""""""""""""
" BASIC EDITOR CUSTOMIZATIONS
""""""""""""""""""
set guifont=CascadiaCodePLRoman-SemiLight:h20
set encoding=utf-8
set fileencoding=utf-8
"set ttyfast
set laststatus=2
syntax enable

filetype plugin indent on
set number
"set number relativenumber
" Auto toggle of line numbers https://jeffkreeftmeijer.com/vim-number/
augroup numbertoggle
  autocmd!
  autocmd BufEnter,FocusGained,InsertLeave,WinEnter * if &nu && mode() != "i" | set rnu   | endif
  autocmd BufLeave,FocusLost,InsertEnter,WinLeave   * if &nu                  | set nornu | endif
augroup END

set hidden
set nocp

set t_Co=256
set cursorline
set conceallevel=2

""""""""""""""""""""""""""
" SETTING UP PLUGINS
""""""""""""""""""""""""""

set rtp+=/opt/homebrew/opt/fzf

call plug#begin('~/.vim/plugged')
Plug 'tpope/vim-surround'

Plug 'junegunn/fzf.vim'
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }

Plug 'sirver/ultisnips'
let g:UltiSnipsExpandTrigger = '<tab>'
let g:UltiSnipsJumpForwardTrigger = '<tab>'
let g:UltiSnipsJumpBackwardTrigger = '<s-tab>'

Plug 'lervag/vimtex'
filetype plugin indent on
let g:tex_flavor='latex'
let g:vimtex_view_method='skim'
let g:vimtex_quickfix_mode=0
let g:tex_conceal='abdmg'
let g:vimtex_complete_enabled=1
"let g:vimtex_fold_enabled=1

Plug 'sonph/onehalf', { 'rtp': 'vim' }
"Plug 'dylanaraps/wal.vim'

Plug 'preservim/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'https://github.com/ludovicchabant/vim-gutentags'
call plug#end()

" set statusline+=%{gutentags#statusline()}

" C-l in insert mode will auto fix spell error
set spell spelllang=en_us
inoremap <C-l> <c-g>u<Esc>[s1z=`]a<c-g>u

" :grep
set grepprg=rg\ --vimgrep\ --smart-case\ --follow

" \lt opens fzf
nnoremap <localleader>lt :call vimtex#fzf#run()<cr>


colorscheme onehalflight

" Supress VimTeX warnings in quickfix view (:copen)

let g:vimtex_quickfix_ignore_filters = [
    \"Underfull",
    \"Overfull",
    \"specifier changed to",
    \"You have requested",
    \"Missing number, treated as zero.",
    \"There were undefined references",
    \"Citation %.%# undefined",
    \"without twoside option",
    \]

" Shorten the begin and end statements
call matchadd('Conceal', '\\begin{[^}]\+}',    10, -1, {'conceal':'-'})
call matchadd('Conceal', '\\end{[^}]\+}',    10, -1, {'conceal':'-'})
"hi clear Conceal

""""""""""""""""""
" Inkscape Sync Scripts
""""""""""""""""""

inoremap <C-f> <Esc>: silent exec '.!inkscape-figures create "'.getline('.').'" "'.b:vimtex.root.'/figures/"'<CR><CR>:w<CR>
nnoremap <C-f> : silent exec '!inkscape-figures edit "'.b:vimtex.root.'/figures/" > /dev/null 2>&1'<CR><CR>:w<CR>
silent !find -L ~/univ/current_semester -type d | grep "figures$" > '/Users/xiaoyu/Library/Application Support/inkscape-figures/roots'
silent !inkscape-figures watch

""""""""""""""""""
" Quiver
""""""""""""""""""

function! ReplaceQuiverDiagram()
    " Save current cursor position
    let save_cursor = getpos(".")

    " this line solves the problem of not being able to select
    " when the cursor is on the first character of the first line
    if getline('.') != ''
        normal! l
    endif

    " Search for the URL start and diagram end
    let start = search('%\shttps\S\+\/\#q=', 'b')
    let end = search('\\end{tikzcd}', '')
    if save_cursor[1] >= start && save_cursor[1] <= end
    	" Extract the URL
    	let url_line = getline(start)
    	let matched_parts = matchlist(url_line, '\s\(https\S\+\)\/\#q=\(.\+\)$') 

	let first_part =  matched_parts[1]
	let second_part =  matched_parts[2]
	"echomsg first_part
	"echomsg  first_part . '/#q=' . second_part
	"echomsg shellescape(first_part . '/#q=' . second_part)
    	" Open the URL in the browser
    	silent execute '!firefox ' . shellescape(first_part . '/\#q=' . second_part)
    	call setpos('.', save_cursor)
	execute 'normal! ' . start . 'GV' . end . 'G'
    else
    	silent execute '!firefox  https://quiver.local:8080' 
    	call setpos('.', save_cursor)
    endif
    " Restore cursor position and visually select the diagram
endfunction

" Bind the function to a keyboard shortcut in TeX files
autocmd FileType tex nnoremap <buffer> <C-x><C-q> :call ReplaceQuiverDiagram()<CR>

" Quiver text objects
autocmd FileType tex xnoremap aq :<C-u>call QuiverTextObject()<CR>
autocmd FileType tex omap aq :normal vaq<CR>
autocmd FileType tex noremap tq :call search('%\s\S\+\/\#q=', '')<CR>
autocmd FileType tex noremap Fq :call search('%\s\S\+\/\#q=', 'b')<CR>
" To find the endpoint of the quiver, need to first find the start point. 
" Cannother directly search tikzcd because it is not unique
function! SearchTwoPatterns(pattern1, backward1, pattern2, backward2)
    call search(a:pattern1, a:backward1)
    call search(a:pattern2, a:backward2)
    normal! j^
endfunction
autocmd FileType tex noremap Tq :call SearchTwoPatterns('%\shttps\S\+\/\#q=', 'b', '\\end{tikzcd}', '')<CR>
autocmd FileType tex noremap fq :call SearchTwoPatterns('%\shttps\S\+\/\#q=', '', '\\end{tikzcd}', '')<CR>
function! QuiverTextObject()
    let save_cursor = getpos(".")

    " this line solves the problem of not being able to select
    " when the cursor is on the first character of the first line
    if getline('.') != ''
        normal! l
    endif

    let start = search('%\s\S\+\/\#q=', 'b')
    let end = search('\\end{tikzcd}', '')

    if save_cursor[1] >= start && save_cursor[1] <= end
        " select the lines (V for visual line mode, 5G for goto line number)
        execute 'normal! ' . start . 'GV' . end . 'G'
    endif
endfunction


