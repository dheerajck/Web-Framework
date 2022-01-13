def render_template(template_name='test.html', context={}):
    from os import getcwd

    print(getcwd())

    '''
    this function returns html string
    '''
    html_string = ""

    with open(f'templates/{template_name}', mode='r') as template_file:

        html_string = template_file.read()

    # template tag regex template small engine

    return html_string
