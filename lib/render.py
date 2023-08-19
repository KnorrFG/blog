from .html import h, s
from . import css
style = css.style

dark_brown = "#4e4a48"
light_brown = "#e8dccd"

def index(posts):
    html = h.html[
        _header(),
        _body(posts)
    ]
    return f"<!DOCTYPE html>{html}"


def _header():
    return h.head[
        s.meta(charset="UTF-8"),
        *(s.meta(name=x[0], content=x[1]) for x in (
            ("description", "A blog, mostly about programming"),
            ("keywords", "Programming, Rust, C, Python"),
            ("author", "Felix Knorr"),
            ("viewport", "width=device-width, initial-scale=1"),
            ("google-site-verification", "nPdJMJTDyxfD2nSz55VURwJWrAb-Pv1DH0EEWvUxFlI"))),
        *(s.link(rel="stylesheet", href=sheet) for sheet in "/common.css /index.css /code.css".split()),
        s.link(rel="icon", href="/assets/logo.png", type="image/png"),
        h.script(
            src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/startup.js",
            integrity="sha512-LZZ88buOWCaSouKg9UNiW3N/vhBCprp0tpG9uNp+r6maXLDeBddAaqTmDduadI+WghoGaNlZG4NgCX0Xsxlfxg==",
            crossorigin="anonymous", 
            referrerpolicy="no-referrer")
    ]

    
def _body(posts):
    return h.body[
        h.div(id="body_container")[
             _head_line(),
            h.p(id="welcome")["Welcome to my blog, where I write about programming (mostly) and other nerdy stuff (sometimes)."],
            h.div(id='cards')[
                *(_card_index(info["title"], info["link"], info["date"], info["tags"], info["excerpt"])
                    for info in posts.values())
            ]
        ]
    ]

def _card_index(title, link, date, tags, content):
    return h.div(klass="card")[
        h.div(klass="card-header")[
            h.div(klass="left-half")[
                h.a(klass="title", href=link)[title],
                h.p(klass="tags")[tags]
            ],
            h.p(klass="date")[date]
        ],
        *([h.div(klass="card-content")[
            h.p[content]
          ]] if content != "" else [])
    ]
    
def _head_line():
    return h.div(id="head_line")[
        h.div(id="outer_head_row")[
            s.img(src='/assets/logo.png', alt="Blog Logo", width="100"),
            h.div(id="text_row")[
                h.a(href="/index.html", id="title")["Felix Blog"],
                h.div(klass="spacer"),
                h.a(href='/about_me.html', id="about_me")["About Me"]
            ],
        ],
        s.hr
    ]
    
def about_me():
    return ""

def css_files():
    return {
        "common.css": _render_common_css(),
        "index.css": css.render({
            '#welcome': {
                "text-align": "center"
            },
            '#cards': {
                "display": "flex",
                "flex-direction": "column",
                "gap": "1.5em",
            }
        })
    }

def _render_common_css():
    return css.render({
        'body': {
            "line-height": "1.4",
            "font-size": "18px !important",
            "background-color": "#f0ebe4",
            "font-family": "Helvetica",
        },
        '#body_container': {
            "margin-inline": "auto",
            "max-width": "50em",
        },
        '#outer_head_row': {
            "width": "100%",
            "display": "flex",
            "align-items": "center"
        },
        '#text_row a': {
            "text-decoration": "none",
            "color": dark_brown,
            "display": "inline-block"
        },
        '#head_line': "width: 100%;",
        '#head_line img': {"display": "inline-block;"},
        '#text_row': {
            "width": "100%",
            "display": "flex",
            "align-items": "baseline",
            "margin-bottom": "-1em"
        },
        '.spacer': {
            "flex-grow": "1"
        },
        '#title': {
            'font-size': "32pt",
            'font-weight': "bold",
            'padding-inline': "0.5em"
        },
        '#about_me': {
            'font-weight': "bold"
        },
        '.card': {
            'display': 'flex',
            'flex-direction': "column",
            'box-shadow': "0.25em 0.25em 0.25em black"
        },
        '.card-header': {
            "line-height": "1",
            "background-color": dark_brown,
            "margin-bottom": "0",
            "color": light_brown,
            "display": "flex",
            "align-items": "center",
            'padding': '1em'
        },
        '.card-header .left-half': {
            'flex-grow': 1,
            "display": "flex",
            "flex-direction": "column",
            "gap": "0.7em",
            "width": "100%"
        },
        '.card-header .title': {
            "font-weight": "bold",
            "font-size": "22pt",
            'padding-right': "2em",
            "margin": "0"
        },
        'a.title': {
            "text-decoration": "none",
            "text-decoration": "none",
            "color": light_brown,
        },
        '.card-header .date': {
            "min-width": "6em",
            "text-align": "right"
        },
        '.card-header .tags': {
            'font-style': "oblique 10deg",
            "margin": "0",
            "font-size": "12pt"
        },
        '.card-content': {
            "margin-top": "0",
            "background-color": light_brown,
            "padding-inline": "1em"
        },
    })

def post(post):
    return ""