#!/usr/bin/env bash
# Bash completion for cyberium CLI

_cyberium_completion() {
    local cur prev opts commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="status current show q question list ls all questions submit submit-extra modules set-module programs switch set-program extra themes set-theme theme profile stats banner book video note notes search sync refresh logout login auth test tui"
    opts="--help -h --version -v --test"

    case "${prev}" in
        switch|set-program|program|track)
            local tracks="ZX310 ZX301 ZX305 ZX322 NX201 NX212 NX216 NX220 NX232 XE101 XE103 XE105 XE107 XE109"
            COMPREPLY=( $(compgen -W "${tracks}" -- "${cur}") )
            return 0
            ;;
        set-theme|theme)
            local themes="cyberium cyberpunk dracula tokyo-night catppuccin gruvbox everforest rose-pine kanagawa nord matrix synthwave84 monokai oxocarbon retro-fallout solarized classic"
            COMPREPLY=( $(compgen -W "${themes}" -- "${cur}") )
            return 0
            ;;
        book)
            local book_opts="-o --open -d --download -c --copy --out"
            COMPREPLY=( $(compgen -W "${book_opts}" -- "${cur}") )
            return 0
            ;;
        video)
            local vid_opts="-o --open -c --copy"
            COMPREPLY=( $(compgen -W "${vid_opts}" -- "${cur}") )
            return 0
            ;;
        submit)
            local submit_opts="-x --extra -i --index"
            COMPREPLY=( $(compgen -W "${submit_opts}" -- "${cur}") )
            return 0
            ;;
        note)
            local note_opts="clear -a --all"
            COMPREPLY=( $(compgen -W "${note_opts}" -- "${cur}") )
            return 0
            ;;
        login|auth)
            local login_opts="-m --manual"
            COMPREPLY=( $(compgen -W "${login_opts}" -- "${cur}") )
            return 0
            ;;
    esac

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        if [[ "${cur}" == -* ]]; then
            COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") )
        else
            COMPREPLY=( $(compgen -W "${commands} ${opts}" -- "${cur}") )
        fi
        return 0
    fi
}

complete -F _cyberium_completion cyberium
