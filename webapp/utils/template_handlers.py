def render_template(template_name='test.html', context={}):
    from os import getcwd

    print(getcwd())

    '''
    this function returns html string
    '''
    html_string = ""
    directory = 'webapp/templates/'
    # print("\n\n__________________Template directory_________________\n\n")
    # print(f'{directory}{template_name}')
    # print(context)
    # print("\n\n__________________ COMPLETED _________________\n\n")

    with open(f'{directory}{template_name}', mode='r') as template_file:

        html_string = template_file.read()
    html_string = html_string.format(**context)
    return html_string
