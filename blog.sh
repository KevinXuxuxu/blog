while getopts sgpd flag
do
    case "$flag" in
        s) docker run --rm -p 5001:5001 -v `pwd`:/blog -w /blog -it fzxu/blog flask run -h 0.0.0.0 -p 5001;;
        g) docker run --rm -v `pwd`:/blog -w /blog -it fzxu/blog python3 generate.py;;
        p) pushd build && git add . && git commit -am "update" && git push && popd;;
        d) pushd build && git status && git diff && popd;;
    esac
done
