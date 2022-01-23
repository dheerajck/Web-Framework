from urllib.parse import parse_qs
import cgi

from tempfile import TemporaryFile


def is_post_request(environ):
    if environ['REQUEST_METHOD'].upper() != 'POST':
        return False
    content_type = environ.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')
    # print(content_type)
    print(content_type.startswith('multipart/form-data'))
    return content_type.startswith('application/x-www-form-urlencoded') or content_type.startswith(
        'multipart/form-data'
    )


def read(environ):
    length = int(environ.get('CONTENT_LENGTH', 0))
    stream = environ['wsgi.input']
    body = TemporaryFile(mode='w+b')
    while length > 0:
        part = stream.read(min(length, 1024 * 200))  # 200KB buffer size
        if not part:
            break
        body.write(part)
        length -= len(part)
    body.seek(0)
    environ['wsgi.input'] = body
    return body


def form_with_file_parsing(environ):

    """
    works for normal form data

    # parse_qs
    # Parse a query string given as a string argument (data of type application/x-www-form-urlencoded)
    # Data are returned as a dictionary. The dictionary keys are the unique query variable names and
    # the values are lists of values for each name.

    The optional argument keep_blank_values is a flag indicating whether blank values in percent-encoded queries
    should be treated as blank strings. A true value indicates that blanks should be retained as blank strings.
    The default false value indicates that blank values are to be ignored and treated as if they were not included.
    """

    # assert is_post_request(environ)

    # body = read(environ)
    # print("bodye 1")
    # print(body)
    wsgi_input = environ['wsgi.input']

    post_form = environ.get('wsgi.post_form')
    if post_form is not None and post_form[0] is wsgi_input:
        return post_form[2]

    # This must be done to avoid a bug in cgi.FieldStorage
    environ.setdefault('QUERY_STRING', '')
    a = environ['wsgi.input']
    # print(1, environ['wsgi.input'])
    # print(environ['wsgi.input'])
    # better give variable instead of again taking environ['wsgi.input'] since wsgi
    form_field_storage = cgi.FieldStorage(fp=wsgi_input, environ=environ, keep_blank_values=True)
    # print(form_field_storage)

    wsgi_new_input = InputProcessed()
    # print(wsgi_new_input)

    post_form = (wsgi_new_input, wsgi_input, form_field_storage)
    environ['wsgi.post_form'] = post_form

    # currently wsgi.input will return b'' because its already consumed, a custom class is added which will throw
    # EOFError exception when trying to read wsgi.input after parsing, after parsing, the parsed data is stored in environ['wsgi.post_form'][2]

    environ['wsgi.input'] = wsgi_new_input

    # print(form_field_storage.getvalue("username")) => returns username
    # print(form_field_storage.getvalue("usernasame")) => returns none since field with that name is not present
    # print(form_field_storage)

    # fileitem = form_field_storage['file']
    # here 'file' should be name of html form field, not type
    # fileitem.name gives this name of the html form field which is 'file' in the html form now
    # fileitem.filename gives file name => xyz.fileformat
    # form_field_storage.getvalue('file') gives content of file in binary

    return form_field_storage


class InputProcessed(object):
    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')

    readline = readlines = __iter__ = read


def cgiFieldStorageToDict(fieldStorage):
    """Get a plain dictionary rather than the '.value' system used by the
    cgi module's native fieldStorage class."""
    params = {}
    for key in fieldStorage.keys():
        params[key] = fieldStorage[key].value
    return params
