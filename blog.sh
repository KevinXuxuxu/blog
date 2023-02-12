while getopts sgpdn flag
do
    case "$flag" in
        s) docker run --rm -p 8000:8000 -v `pwd`/build:/build -w /build -it fzxu/blog python3 -m http.server;;
        g) docker run --rm -v `pwd`:/blog -w /blog -it fzxu/blog python3 generate.py;;
        p) pushd build && git add . && git commit -am "update" && git push && popd;;
        d) pushd build && git status && git diff && popd;;
        n) docker run --rm -v `pwd`:/blog -w /blog -it fzxu/blog python3 utils.py new "$2"
    esac
done
