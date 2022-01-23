def serve_media_file(environ, **kwargs):

    file_name = kwargs['file_name']

    # extension will be the "last element" when split by . so -1 is important in this to get extension always
    # becauses filename liek a.b.py "might" come

    # traveral_attack_check(file_name)

    directory = 'webapp/media/'

    file_directory = f'{directory}{file_name}'
    # reading only in binary format,
    # data is read and written in the form of bytes

    try:
        # assert False
        with open(file_directory, mode='rb') as f:
            static_file_data_in_bytes = f.read()
    except FileNotFoundError:

        from .views1 import view_404

        print("xdada")
        kwargs = {}
        # print(view_404(environ))
        # print("xdada")
        return view_404(environ)

    file_name = file_name.split("__")[-1]

    # js dont care about content type, works with text/css
    response_headers = [
        ('Content-type', "application/octet-stream"),
        ('Content-Disposition', f'inline; filename="{file_name}"'),
    ]
    # reponse_headers = {}

    # because assertion is done to ensure data received on app from view is always a string and a dict
    # static_file_data_in_bytes = static_file_data_in_bytes.decode()

    # print(static_file_data_in_bytes, {'status': '200 OK', 'response_headers': response_header_basic_value})
    return static_file_data_in_bytes, {'status': '200 OK', 'response_headers': response_headers}
