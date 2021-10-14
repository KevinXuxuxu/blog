while getopts sgpd flag
do
    case "$flag" in
        s) flask run -h 0.0.0.0;;
        g) python3 generate.py;;
        p) pushd build && git add . && git commit -am "update" && git push && popd;;
        d) pushd build && git status && git diff && popd;;
    esac
done
