from six.moves.http_cookiejar import CookieJar  # noqa
from six.moves.urllib_error import HTTPError, URLError  # noqa
from six.moves.urllib_parse import (  # noqa
    quote, urlencode, urljoin, urlparse,
)
from six.moves.urllib_request import (  # noqa
    HTTPBasicAuthHandler, HTTPCookieProcessor, HTTPDigestAuthHandler, Request,
    build_opener, install_opener, urlopen,
)

# pylama:skip=1
