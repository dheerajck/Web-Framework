def render_template(template_name='test.html', context={}):
    from os import getcwd

    print(getcwd())

    '''
    this function returns html string
    '''
    html_string = ""
    directory = 'webapp/templates/'
    print(f'{directory}{template_name}')

    with open(f'{directory}{template_name}', mode='r') as template_file:

        html_string = template_file.read()

    # template tag regex template small engine
    print()
    print()
    print(type(html_string))
    return html_string
