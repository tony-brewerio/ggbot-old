

def test_templates_renders():
    "ensure that template 'version/version' renders properly"
    from gbot.templates import render

    assert isinstance(render('ru/version/version'), basestring)
    assert "DotA bot | Garena | ver" in render('ru/version/version')