import os


def traveral_attack_check(file_name):

    safe_dir = 'webapp/static/'

    # print(os.path.commonprefix((os.path.realpath(file_name), safe_dir)))
    if os.path.commonprefix((os.path.realpath(file_name), safe_dir)) != safe_dir:
        assert False, "directory traversal file name"


def serve_static_file(environ, **kwargs):

    file_name = kwargs['file_name']

    # extension/foldername in static => Content-type
    extension_directory = {
        'css': 'text/css',
        'js': 'text/javascript',
    }

    # extension will be the "last element" when split by . so -1 is important in this to get extension always
    # becauses filename like a.b.py "might" come
    extension = file_name.split('.')[-1]
    content_type_of_file = extension_directory[extension]

    # traveral_attack_check(file_name)

    directory = 'webapp/static/'
    file_relative_directory = f'{extension}/{file_name}'
    file_directory = f'{directory}{file_relative_directory}'
    # reading only in binary format,
    # data is read and written in the form of bytes

    with open(file_directory, mode='rb') as f:
        static_file_data_in_bytes = f.read()

    response_header_basic_value = [
        ('Content-type', content_type_of_file),
        ('Content-length', str(len(static_file_data_in_bytes))),
    ]

    static_file_data_in_bytes = static_file_data_in_bytes.decode()

    return static_file_data_in_bytes, {'status': '200 OK', 'response_headers': response_header_basic_value}
