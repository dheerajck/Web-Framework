from template_functions.template_handlers import render_template


# only using kwargs since args might create unwanted problems and nkeyword arguments will be better its explicit
# changed to named parameters because its better to not accept unwanted keyword argument, this throws cant unpack error so avoiding for now
def root(environ, **kwargs):
    return render_template("root.html", context={})


def test(environ, **kwargs):
    return render_template("test.html", context={})


def view_404(environ, **kwargs):
    return render_template("HTTP404.html", context={})
