from textwrap import dedent

from .html import h, s
from . import css
import markdown as md


style = css.style

dark_brown = "#4e4a48"
light_brown = "#e8dccd"

def index(posts):
    html = h.html[
        _index_header(),
        _index_body(posts)
    ]
    return f"<!DOCTYPE html>{html}"


def redirect_page(link):
    html = h.html[
        h.head[
            s.meta(http_equiv="Refresh", content=f"0; url='../{link}'")
        ],
        h.body[
            f"redirecting to: {link}"
        ]
    ]
    return f"<!DOCTYPE html>{html}"
    
def _index_header():
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
        h.title["Felix' Blog"],
        h.script(
            src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/startup.js",
            integrity="sha512-LZZ88buOWCaSouKg9UNiW3N/vhBCprp0tpG9uNp+r6maXLDeBddAaqTmDduadI+WghoGaNlZG4NgCX0Xsxlfxg==",
            crossorigin="anonymous", 
            referrerpolicy="no-referrer")
    ]

    
def _index_body(posts):
    return h.body[
        h.div(id="body_container")[
             _head_line(),
            h.p(id="welcome")["Welcome to my blog, where I write about programming (mostly) and other nerdy stuff (sometimes)."],
            h.a(href="/about_me.html", id="secondary-aboutme")["About Me"],
            h.div(id='cards')[
                *(_card_index(info["title"], info["link"], info["date"], info["tags"], info["excerpt"])
                    for info in posts.values())
            ]
        ]
    ]

def _card_index(title, link, date, tags, content):
    return h.div(klass="card")[
        h.a(klass="header-a", href=link)[
            h.div(klass="card-header")[
                h.div(klass="left-half")[
                    h.p(klass="title")[title],
                    h.p(klass="tags")[*(tags if tags is not None else [])]
                ],
                h.p(klass="date")[date]
            ]
        ],
        *([h.div(klass="card-content")[
            h.p[content]
          ]] if content != "" else [])
    ]
    
def _head_line():
    return h.div(id="head_line")[
        h.div(id="outer_head_row")[
            h.a(href="/index.html", id="title")[s.img(src='/assets/logo.png', alt="Blog Logo", width="100")],
            h.div(id="text_row")[
                h.a(href="/index.html", id="title")["Felix Blog"],
                h.div(klass="spacer"),
                h.a(href='/about_me.html', id="about_me")["About Me"]
            ],
        ],
        s.hr
    ]
    
def about_me():
    html = h.html[
        _index_header(),
        _about_body()
    ]
    return f"<!DOCTYPE html>{html}"


def _about_body():
    return h.body[
        h.div(id="body_container")[
             _head_line(),
             h.div(id="about-container")[
                 h.div(id="about")[
                    md2html("""
                        ## About Me

                        My name is Felix Knorr, currently I'm working as software developer for
                        [neuroloop](https://neuroloop.de/)
                    
                        I'm a Computer Science and programming enthusiast (and a huge nerd in many
                        other regards). Here you'll find my Blog, and my projects, and other
                        references. You can also find me on [Github](https://github.com/KnorrFG)
                        and [LinkedIn](https://www.linkedin.com/in/felix-knorr-197453213/),
                        or you can send me a mail: <span id="mailaddr">please enable js to see the mail address</span>

                        """)
                ],
                s.img(src="/assets/portrait.png", alt="Felix' Portrait", id='portrait'),
                h.div(id="projects")[
                    md2html("""
                        ## Opensource Projects

                        **Dotree** is a small interactive command runner. It wants to be a 
                        better home for your aliases and bash functions, especially those 
                        that you don't use that often, and an alternative to just.  
                        [GitHub](https://github.com/KnorrFG/dotree)

                        **Pyparadigm** is a Python library which allows to
                        arrange and display visual stimuli and react to user-input
                        with minimal amounts of source code in a declarative
                        manner.
                        [GitHub](https://github.com/knorrfg/pyparadigm)
                        [Documentation](https://pyparadigm.readthedocs.org)

                        **Datasheet** is a python library which easily generates
                        HTML pages containing Markdown text, pandas tables,
                        matplotlib figures and nifti images.  
                        [GitHub](https://github.com/knorrfg/datasheet)
                        [Documentation](https://datasheet.readthedocs.org)

                        **Markdown Note** is a small command line utility to
                        manage notes. It can be configured to use any editor and notes
                        can be viewed as html using a browser  
                        [GitHub](https://github.com/KnorrFG/markdown_note)
                        [Article](/posts/2021-04-28-mdn.html)
                    """)
                ],
                h.div(id="publications")[
                    md2html("""
            
                      ## Publications
        
                      I used to do a PhD, which I didn't finish, as I did it in
                      Neuro-Psychology, and the longer it was going on, the more I realized,
                      that this wasn't lining up with my interests. However, I produced a few
                      publications in that time:

                      [PyParadigm—A Python Library to Build Screens in a Declarative Way](https://www.frontiersin.org/articles/10.3389/fninf.2019.00059/full)  
                      <span class="authors">Knorr FG, Petzold J, Marxen M.</span>  
                      Frontiers in Neuroinformatics 2019


                      [A comparison of fMRI and behavioral models for predicting inter-temporal choices](https://www.sciencedirect.com/science/article/pii/S105381192030121X)  
                      <span class="authors"> Felix G. Knorr, Philipp T. Neukam, Juliane H. Fröhner, Holger
                      Mohr, Michael N.Smolka, Michael Marxen</span>  
                      NeuroImage 2020
                     """)
                ]
            ]
        ],
        h.script["""
            cmp1 = [4, 9, 7, 8, 4, 0, 5, 2, 1, 8, 5, 10, 10, 5, 10, 1, 4, 1]
            cmp2 = [111, 103, 104, 122, 118, 46, 99, 103, 109, 97, 125, 74, 109, 104, 114, 47, 96, 100]
            mail = cmp1
            for (let i = 0; i < cmp1.length; ++i) {
              mail[i] = String.fromCharCode(cmp1[i] ^ cmp2[i]);
            }
            ms = document.getElementById('mailaddr')
            ms.innerHTML = mail.join("")
        """]
     ]


def css_files():
    return {
        "common.css": _render_common_css(),
        "index.css": _render_index_css()
    }

def _render_index_css():
    return css.render({
            '#secondary-aboutme': {
                "display": "none",
                "color": dark_brown
            },
            '#welcome': {
                "text-align": "center"
            },
            '#cards': {
                "display": "flex",
                "flex-direction": "column",
                "gap": "1.5em",
            },
            "#portrait": {
                "width": "100%"
            },
            ".authors": {
                "font-style": "italic",
                "font-size": "100%",
            },
        }) + dedent("""
            @media all and (max-width: 50em) {
                #body_container > #secondary-aboutme {
                    text-decoration: none;
                    color: dark_brown;
                    display: block;
                    text-align: center;
                    font-weight: bold;
                    font-size: 18pt;
                    margin-bottom: 1em;
                }
            }
            @media all and (min-width: 50em) {
                #about-container {
                    display: grid;
                    grid-template-columns: repeat(8, 1fr);
                    gap: 30px;
                }

                #about {
                    grid-column: 1 / 5;
                }

                #portrait {
                    grid-column: 5 / 9;
                    padding-top: 30px;
                }

                #projects {
                    grid-column: 1 / 5;
                }

                #publications {
                    grid-column: 5 / 9;
                }
            }            
            """)
    
def _render_common_css():
    return dedent("""
        @media all and (max-width: 50em) {
            .card-header .date {
                display: none;
            }
            #head_line > #outer_head_row > #text_row > #about_me {
                display: none;
            }
        }
        """) + css.render({
        'body': {
            "line-height": "1.4",
            "font-size": "18px !important",
            "background-color": "#f0ebe4",
            "font-family": "Helvetica",
        },
        "pre": {
            "overflow-x": "auto"
        },
        "img": {
            "max-width": "100%"
        },
        '#body_container': {
            "margin-inline": "auto",
            "max-width": "50em",
        },
        '#outer_head_row': {
            "width": "100%",
            "display": "flex",
            "align-items": "center",
        },
        '#head_line': {
            "width": "100%",
            'img': {
                  "display": "inline-block",
                  "margin-top": "0.5em",
                  "margin-bottom": "-0.25em"
              }
        },
        '#text_row': {
            "width": "100%",
            "display": "flex",
            "align-items": "baseline",
            "margin-bottom": "-1em",
            'a:not(:hover)': {
                "text-decoration": "none",
            },
            'a': {
                "color": dark_brown,
                "display": "inline-block"
            }
        },
        '.spacer': {
            "flex-grow": "1"
        },
        '#title': {
            'font-size': "30pt",
            'font-weight': "bold",
            'padding-inline': "0.5em"
        },
        '#title:hover': {"text-decoration-color": dark_brown}, 
        '#about_me': { 'font-weight': "bold" },
        '#about_me:hover': {"text-decoration-color": dark_brown},
        '.card': {
            'display': 'flex',
            'flex-direction': "column",
            'box-shadow': "0.25em 0.25em 0.5em grey"
        },
        '.card-header': {
            "line-height": "1",
            "background-color": dark_brown,
            "margin-bottom": "0",
            "color": light_brown,
            "display": "flex",
            "align-items": "center",
            'padding': '1em',
            '.left-half': {
                'flex-grow': 1,
                "display": "flex",
                "flex-direction": "column",
                "gap": "0.7em",
                "width": "100%"
            },
            '.title': {
                "font-weight": "bold",
                "font-size": "22pt",
                'padding-right': "2em",
                "margin": "0"
            },
            '.date': {
                "min-width": "6em",
                "text-align": "right"
            },
            '.tags': {
                'font-style': "oblique 10deg",
                "margin": "0",
                "font-size": "12pt"
            },
        },
        'a.header-a:not(:hover)': {"text-decoration": "none"},
        'a.header-a:hover': {"text-decoration-color": light_brown},
        'a.title': {
            "color": light_brown,
        },
        '.card-content': {
            "margin-top": "0",
            "background-color": light_brown,
            "padding-inline": "1em"
        },
    })

def post(post):
    html = h.html[
        _post_header(post),
        _post_body(post)
    ]
    return f"<!DOCTYPE html>{html}"


def _post_header(post):
    return h.head[
        s.meta(charset="UTF-8"),
        *(s.meta(name=x[0], content=x[1]) for x in (
            ("description", "A blog, mostly about programming"),
            ("keywords", "Programming, Rust, C, Python"),
            ("author", "Felix Knorr"),
            ("viewport", "width=device-width, initial-scale=1"),
            ("google-site-verification", "nPdJMJTDyxfD2nSz55VURwJWrAb-Pv1DH0EEWvUxFlI"))),
        *(s.link(rel="stylesheet", href=sheet) for sheet in "/common.css /code.css".split()),
        s.link(rel="icon", href="/assets/logo.png", type="image/png"),
        h.title[f"Felix' Blog - {post['title']}"],
        h.script(
            src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/startup.js",
            integrity="sha512-LZZ88buOWCaSouKg9UNiW3N/vhBCprp0tpG9uNp+r6maXLDeBddAaqTmDduadI+WghoGaNlZG4NgCX0Xsxlfxg==",
            crossorigin="anonymous", 
            referrerpolicy="no-referrer")
    ]   

def _post_body(post):
    return h.body[
        h.div(id="body_container")[
            _head_line(),
            _card_post(post["title"], post["date"], post["tags"], post["post"])
        ]
    ]   

def _card_post(title, date, tags, content):
    return h.div(klass="card")[
        h.div(klass="card-header")[
            h.div(klass="left-half")[
                h.p(klass="title")[title],
                h.p(klass="tags")[*(tags if tags is not None else [])]
            ],
            h.p(klass="date")[date]
        ],
        *([h.div(klass="card-content")[
            h.p[content]
          ]] if content != "" else [])
    ]
    
def md2html(s):
    return md.markdown(dedent(s), extensions=["extra", "codehilite", "mdx_math"])

