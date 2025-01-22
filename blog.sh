while getopts sgpdnv flag
do
    case "$flag" in
        v) pushd build && uv run python3 -m http.server && popd;;
        s) OPENCODER_URL_PREFIX='/opencoder' uv run flask run -h 0.0.0.0 -p 8000;;
        g) OPENCODER_URL_PREFIX='/opencoder' uv run python3 generate.py;;
        p) pushd build && git add . && git commit -am "update" && git push && popd;;
        d) pushd build && git status && git diff && popd;;
        n) uv run python3 utils.py new "$2"
    esac
done
