import string
class URL:
    __slots__ = [
            'protocol',
            'host',
            'port',
            'file',
            'query',
            'authority',
            'userInfo',
            'path',
            'ref',
            'hostAddress',
            'handler',
            'hashCode',
            ]

    def __init__(self, spec, handler=None):
        original = spec
        i, limit, c = 0, 0, 0
        start = 0
        self.protocol = None
        self.authority = None
        self.userInfo = None
        self.host = None
        self.port = None
        self.ref = None
        self.query = None
        self.path = None
        self.file = None

        limit = len(spec)
        while limit > 0 and spec[limit -1] <= ' ':
            limit -= 1 # eliminate trailing whitespace

        while start < limit and spec[start] <= ' ':
            start += 1        # eliminate leading whitespace

        if spec.lower()[start:start+5] == "url:":
            start += 4

        i = start

        newProtocol, start = self.parseProtocol(spec, start, i)

        # Only use our context if the protocols match.
        self.protocol = newProtocol
        if not self.protocol:
            raise Exception("no protocol: "+original)

        # Get the protocol handler if not specified or the protocol
        # of the context could not be used
        i = spec.find('#', start)
        v = limit if i < 0 else i
        newspec = spec[start:v]
        (protocol, host, port, authority, userInfo, path) =  self.parseURL(newspec)
        i = spec.find('#', start)
        ref = None
        if i >= 0:
            ref = spec[i + 1:]
            limit = i

        # Strip off the query part
        queryStart = spec.find('?')
        queryOnly = queryStart == start
        query=''
        if (queryStart != -1):
             query = spec[queryStart+1:limit]
        self.setURL(protocol, host, port, authority, userInfo, path, query, ref)


    def parseURL(self, spec):
        protocol = self.protocol
        authority = self.authority
        userInfo = self.userInfo
        host = self.host
        port = self.port
        path = self.path
        query = self.query

        isRelPath = False
        queryOnly = False
        start = 0
        limit = len(spec)

        if start < limit:
            queryStart = spec.find('?')
            if queryStart != -1 and limit > queryStart:
                limit = queryStart

        i = 0

        # Parse the authority part if any
        isUNCName = (start <= limit - 4) and \
                        (spec[start] == '/') and \
                        (spec[start + 1] == '/') and \
                        (spec[start + 2] == '/') and \
                        (spec[start + 3] == '/')
        if (not isUNCName):
            if spec[start:] =='' or spec[start] != '/':
                raise Exception('/ REQUIRED')
            start += 1
            if spec[start:] =='' or spec[start] != '/':
                raise Exception('// REQUIRED')
            start += 1
            i = spec.find('/', start)
            if (i < 0) :
                i = spec.find('?', start)
                if (i < 0):
                    i = limit

            host = authority = spec[start:i]

            ind = authority.find('@')
            if (ind != -1):
                userInfo = authority[0:ind]
                host = authority[ind+1:]
            else:
                userInfo = None
            port = -1
            if host:
                # If the host is surrounded by [ and ] then its an IPv6
                # literal address as specified in RFC2732
                if (len(host) >0 and (host[0] == '[')):
                    ind = host.find(']')
                    if (ind  > 2):

                        nhost = host
                        host = nhost[0,ind+1]
                        if (not isIPv6LiteralAddress(host[1: ind])):
                            raise Exception("Invalid host: "+ host)
                        port = -1
                        if (len(nhost) > ind+1):
                            if (nhost[ind+1] == ':'):
                                ind += 1
                                # port can be null according to RFC2396
                                if (len(nhost) > (ind + 1)):
                                    port = int(nhost[ind+1:])
                            else:
                                raise Exception("Invalid authority field: " + authority)
                    else:
                        raise Exception( "Invalid authority field: " + authority)
                else:
                    ind = host.find(':')
                    port = -1
                    if (ind >= 0):
                        # port can be null according to RFC2396
                        if (len(host) > (ind + 1)):
                            port = int(host[ind + 1:])
                        host = host[0: ind]
            else:
                host = ""
            if (port < -1):
                raise Exception("Invalid port number :" + port)
            start = i
            # If the authority is defined then the path is defined by the
            # spec only; See RFC 2396 Section 5.2.4.
            if (authority and len(authority) > 0):
                path = ""

        if not host:
            host = ""

        # Parse the file path if any
        if (start < limit):
            if (spec[start] == '/') :
                path = spec[start: limit]
            elif (path and len(path) > 0):
                isRelPath = True
                ind = path.rfind('/')
                seperator = ""
                if (ind == -1 and authority):
                    seperator = "/"
                path = path[0: ind + 1] + seperator + spec[start: limit]

            else:
                seperator =  "/" if authority else ""
                path = seperator + spec[start: limit]
        if not path:
            path = ""

        return (protocol, host, port, authority, userInfo, path)


    def setURL(self, protocol, host, port, authority, userInfo, path, query, ref):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.authority = authority
        self.userInfo = userInfo
        self.path = path
        self.query = query
        self.ref = ref

    def isValidProtocol(self, protocol):
        _len = len(protocol)
        if _len < 1:
            return False
        c = protocol[0]
        v = c.in_(string.ascii_letters)
        if not c:
            return False
        i = 1
        while i < _len:
            c = protocol[i]
            if (not c.in_(string.ascii_letters + string.digits)) and c != '.' and c != '+' and c != '-' :
                return False
            i+= 1
        return True

    def parseProtocol(self, spec, start, i):
        c = spec[0]
        if not c.in_(string.ascii_letters):
            raise Exception("no protocol: "+spec)

        while spec[i:] != '' and spec[i] != '/':
            c = spec[i]
            if c == ':':
                s = spec[start: i].lower()
                return s, i+1
            elif (not c.in_(string.ascii_letters + string.digits)) and c != '.' and c != '+' and c != '-' :
                raise Exception("no protocol: "+spec)
            i += 1
        raise Exception("no protocol: "+spec)

    def __repr__(self):
        try:
            return ("protocol:%s host:%s port:%s file:%s path:%s query:%s ref:%s" % (
                repr(self.protocol), repr(self.host), repr(self.port), repr(self.file), repr(self.path), repr(self.query), repr(self.ref)))
        except Exception as e:
            return str(e)

class Parts:
    __slots__ = [
            'path',
            'query',
            'ref',
            ]
    def __init__(self, file):
        ind = file.find('#')
        ref = null if ind < 0 else file[ind:]
        file = file if ind < 0 else file[0:ind]
        q = file.rfind('?')
        if q != -1:
            query = file[q+1:]
            path = file[0:q]
        else:
            path = file

    def getPath(self): return self.path
    def getQuery(self): return self.query
    def getRef(self): return self.ref

def main(arg):
    u = URL(arg)
    print(u)

def inputs():
    import os.path
    if os.path.exists('tests/urljava.input'):
        return [l.strip() for l in open('tests/urljava.input') if not l[0] == '#']
    INPUTS = ['http://www.google.com',
            'https://alaska.com:8080/me?you=this',
            'http://pages.com/new#fragment',
            'http://mynews.com/query?a=b,c=d#fragment',
            'ftp://me:mexico@alaska.com']
    return INPUTS

def skip_classes():
    return ['.*JSONStream.*']


if __name__ == '__main__':
    import sys
    s = sys.argv[1]
    main(s)
