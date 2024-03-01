while getopts sgpdn flag
do
    case "$flag" in
        s) docker run --rm -p 8000:8000 -v `pwd`:/blog -w /blog -e OPENCODER_URL_PREFIX='/opencoder' -it fzxu/blog flask run -h 0.0.0.0 -p 8000;;
        g) docker run --rm -v `pwd`:/blog -w /blog -e OPENCODER_URL_PREFIX='/opencoder' -it fzxu/blog python3 generate.py;;
        p) pushd build && git add . && git commit -am "update" && git push && popd;;
        d) pushd build && git status && git diff && popd;;
        n) docker run --rm -v `pwd`:/blog -w /blog -it fzxu/blog python3 utils.py new "$2"
    esac
done
