"""
A small Python syntax highlighter shared by the code window and the diff viewer.

It is JavaScript text that the components embed in their own module. It colours
keywords, built-ins, strings, comments, numbers, decorators and the name after
def/class with the app's warm palette (the same classes the CSS of each component
styles). It escapes HTML before adding any markup.
"""

HIGHLIGHT_JS = r"""
const PY_KEYWORDS = new Set(["False","None","True","and","as","assert","async","await","break","class",
  "continue","def","del","elif","else","except","finally","for","from","global","if","import","in","is",
  "lambda","nonlocal","not","or","pass","raise","return","try","while","with","yield","self"])
const PY_BUILTINS = new Set(["len","str","int","float","dict","list","set","tuple","print","open","range",
  "isinstance","super","enumerate","zip","map","filter","sorted","any","all","min","max","sum","type"])

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
}

function highlightPython(line) {
  const pattern = /("{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3}|"{3}[\s\S]*$|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#.*$|@\w+|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b)/g
  let out = "", last = 0, previous = ""
  for (const match of line.matchAll(pattern)) {
    const token = match[0]
    out += escapeHtml(line.slice(last, match.index))
    let cls = ""
    if (token.startsWith("#")) cls = "tk-comment"
    else if (token.startsWith('"') || token.startsWith("'")) cls = "tk-string"
    else if (token.startsWith("@")) cls = "tk-decorator"
    else if (/^\d/.test(token)) cls = "tk-number"
    else if (previous === "def" || previous === "class") cls = "tk-name"
    else if (PY_KEYWORDS.has(token)) cls = token === "self" ? "tk-self" : "tk-keyword"
    else if (PY_BUILTINS.has(token)) cls = "tk-builtin"
    out += cls ? `<span class="${cls}">${escapeHtml(token)}</span>` : escapeHtml(token)
    if (/^[A-Za-z_]/.test(token)) previous = token
    last = match.index + token.length
  }
  return out + escapeHtml(line.slice(last))
}
"""

# Token colours, shared by both components' CSS.
SYNTAX_CSS = """
.tk-keyword { color: var(--accent-amber, #E8B339); }
.tk-builtin { color: var(--color-amber-400, #F0C35A); }
.tk-name { color: var(--text-strong, #FFFFFF); font-weight: 500; }
.tk-string { color: var(--color-success, #4CAF50); }
.tk-comment { color: var(--text-muted, #A59C8A); font-style: italic; }
.tk-number, .tk-decorator { color: var(--color-amber-400, #F0C35A); }
.tk-self { color: var(--text-muted, #A59C8A); }
"""
