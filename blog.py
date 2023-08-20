import sys
from importlib import reload
from pathlib import Path
import subprocess as sp
import atexit
import shutil
import time
import datetime as dt

import markdown as md

from lib import render


files_to_watch = [Path("lib/render.py")] + list(Path().glob("posts/*.md"))

def main():
    print(repr(files_to_watch))
    match sys.argv[1:]:
        case ["serve"]:
            serve()
        case _: 
            raise "Invalid argument"


def serve():
    dist_dir = Path("/tmp/bloghost")
    post_infos = parse_posts()
    make_dist(dist_dir, post_infos)

    change_tss = { file: file.stat().st_mtime
            for file in files_to_watch }

    while True:
        for file, last_updt in change_tss.items():
            last_updt_new = file.stat().st_mtime 
            if last_updt_new > last_updt:
                if file.name == "render.py":
                    print("rerendering because render.py changed")
                    reload(render)
                    make_dist(dist_dir, post_infos)
                else:
                    post_info = parse_post(file.read_text(), file)
                    post_infos.update(post_info)
                    post_infos.sort(key=lambda d: int(dt.datetime.timestamp(d["dt"])), 
                                    reverse=True)
                    render_and_write_post(dist_dir, post_info)
                    
                change_tss[file] = last_updt_new
        time.sleep(0.3)
            

def parse_posts():
    res = {}
    for post in Path().glob("posts/*.md"):
        res.update(parse_post(post.read_text(), post))
    return dict(sorted(res.items(), key=lambda d: int(dt.datetime.timestamp(d[1]["dt"])), 
                    reverse=True))


def make_dist(dist_dir, posts):
    dist_dir.joinpath("posts").mkdir(exist_ok=True, parents=True)
    dist_dir.joinpath("index.html").write_text(render.index(posts))
    dist_dir.joinpath("about_me.html").write_text(render.about_me())
    shutil.copytree("assets", dist_dir/"assets", dirs_exist_ok=True)
    shutil.copy("code.css", dist_dir/"code.css")

    for infos in posts.values():
        render_and_write_post(dist_dir, infos)

    for path, content in render.css_files().items():
        dist_dir.joinpath(path).write_text(content)


def render_and_write_post(dist_dir, infos):
    dist_dir.joinpath(infos["link"]).write_text(render.post(infos))


def parse_post(s: str, path):
    lines = s.splitlines()
    stripped_lines = list(map(str.strip, lines))
    header_start = stripped_lines.index("---")
    header_end = stripped_lines.index("---", header_start + 1)
    header = stripped_lines[header_start + 1: header_end]

    keys = "title excerpt_sep excerpt categories tags".split()
    result = {k: None for k in keys}
    for line in header:
        [key, _, value] = line.partition(":")
        match [key.strip(), value.strip()]:
            case ['title', t]:
                result["title"] = t
            case ['excerpt_separator', e]:
                result['excerpt_sep'] = e.strip()
            case ["categories", c]:
                result['categories'] = c.split()
            case ["tags", t]:
                result["tags"] = t.split()

    if result['excerpt_sep'] is not None:
        print(path)
        excerpt_end = lines.index(result['excerpt_sep'])
        excerpt_md = "\n".join(l for l in lines[header_end + 1: excerpt_end]
                if not l.strip().startswith('#'))
        result['excerpt'] = md_2_html(excerpt_md)

    result['post'] = md_2_html('\n'.join(lines[header_end + 1:]))
    result['dt'] = dt.datetime.strptime(path.name[:10], "%Y-%m-%d")
    result['link'] = str(path.with_suffix(".html"))
    result['date'] = result['dt'].date()
    return {path: result}


def md_2_html(s):
    return md.markdown(s, extensions=["extra", "codehilite", "mdx_math"])


if __name__ == "__main__":
    main()
