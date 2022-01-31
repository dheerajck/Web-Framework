from .views1 import api_view_404


def serve_media_file(environ, **kwargs):

    file_name = kwargs['file_name']

    directory = 'webapp/media/'

    file_directory = f'{directory}{file_name}'
    # reading only in binary format,
    # data is read and written in the form of bytes

    try:
        with open(file_directory, mode='rb') as f:
            static_file_data_in_bytes = f.read()
    except FileNotFoundError:
        kwargs = {}
        return api_view_404(environ)

    file_name = file_name.split("__")[-1]

    response_headers = [
        ('Content-type', "application/octet-stream"),
        ('Content-Disposition', f'inline; filename="{file_name}"'),
    ]

    return static_file_data_in_bytes, {'status': '200 OK', 'response_headers': response_headers}
