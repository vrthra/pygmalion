import induce.mystring as string
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
        newProtocol = None
        self.protocol = None
        aRef = False
        isRelative = False
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

        if start < len(spec) and spec[start] == '#':
            # we're assuming this is a ref relative to the context URL.
            # This means protocols cannot start w/ '#', but we must parse
            # ref URL's like: "hello:there" w/ a ':' in them.
            aRef=true;
        i = start

        while (not aRef) and spec[i:] != '' and spec[i] != '/':
            c = spec[i]
            if c == ':':
                s = spec[start: i].lower()
                if self.isValidProtocol(s):
                    newProtocol = s
                    start = i + 1
                break
            i += 1
        # Only use our context if the protocols match.
        self.protocol = newProtocol
        if not self.protocol:
            raise Exception("no protocol: "+original)

        # Get the protocol handler if not specified or the protocol
        # of the context could not be used
        i = spec.find('#', start)
        if i >= 0 :
            self.ref = spec[i + 1: limit]
            limit = i
        self.parseURL(spec, start, limit)


    def parseURL(self, spec, start, limit):
        protocol = self.protocol
        authority = self.authority
        userInfo = self.userInfo
        host = self.host
        port = self.port
        path = self.path
        query = self.query

        #This field has already been parsed
        ref = self.ref

        isRelPath = False
        queryOnly = False
        # FIX: should not assume query if opaque

        # Strip off the query part
        if start < limit:
            queryStart = spec.find('?')
            queryOnly = queryStart == start
            if (queryStart != -1) and (queryStart < limit):
                query = spec[queryStart+1:limit]
                if limit > queryStart:
                    limit = queryStart
                spec = spec[0: queryStart]

        i = 0
        # Parse the authority part if any
        isUNCName = (start <= limit - 4) and \
                        (spec[start] == '/') and \
                        (spec[start + 1] == '/') and \
                        (spec[start + 2] == '/') and \
                        (spec[start + 3] == '/')
        if (not isUNCName) and (start <= limit - 2) and (spec[start] == '/') and (spec[start + 1] == '/') :
            start += 2
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
                        port = ''
                        if (len(nhost) > ind+1):
                            if (nhost[ind+1] == ':'):
                                ind += 1 
                                # port can be null according to RFC2396
                                if (len(nhost) > (ind + 1)):
                                    port = nhost[ind+1:]
                            else:
                                raise Exception("Invalid authority field: " + authority)
                    else:
                        raise Exception( "Invalid authority field: " + authority)
                else:
                    ind = host.find(':')
                    port = ''
                    if (ind >= 0):
                        # port can be null according to RFC2396
                        if (len(host) > (ind + 1)):
                            port = host[ind + 1:]
                        host = host[0: ind]
            else:
                host = ""
            if (port and int(port) < -1):
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
        elif queryOnly and path :
            ind = path.rfind('/')
            if (ind < 0):
                ind = 0
            path = path[0: ind] + "/"
        if not path:
            path = ""

        if (isRelPath):
            # Remove embedded /./
            i = path.find("/./")
            while (i >= 0) :
                path = path[0: i] + path[i + 2:]
                i = path.find("/./")

            # Remove embedded /../ if possible
            i = 0
            i = path.find("/../", i)
            while (i >= 0):
                # A "/../" will cancel the previous segment and itself,
                # unless that segment is a "/../" itself
                # i.e. "/a/b/../c" becomes "/a/c"
                # but "/../../a" should stay unchanged
                limit = path.rfind('/', i - 1)
                if (i > 0 and limit >= 0 and (path.find("/../", limit) != 0)):
                    path = path[0: limit] + path[i + 3:]
                    i = 0
                else:
                    i = i + 3
                i = path.find("/../", i)
            # Remove trailing .. if possible
            while (path.ends_with("/..")):
                i = path.find("/..")
                limit = path.rfind('/', i - 1)
                if (limit >= 0):
                    path = path[0: limit+1]
                else:
                    break
            # Remove starting .
            if (path.starts_with("./") and len(path) > 2):
                path = path[2:]

            # Remove trailing .
            if path.ends_with("/."):
                path = path[0: len(path)-1]

        self.setURL(protocol, host, port, authority, userInfo, path, query, ref)

    
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
        v = c in string.ascii_letters
        if c not in string.ascii_letters:
            return False
        i = 1
        while i < _len:
            c = protocol[i]
            if c not in (string.ascii_letters + string.digits) and c != '.' and c != '+' and c != '-' :
                return False
            i+= 1
        return True

    def __repr__(self):
        try:
            return ("protocol:%s host:%s port:%s file:%s path:%s query:%s ref:%s" % (
                repr(self.protocol), repr(self.host), repr(self.port), repr(self.file), repr(self.path), repr(self.query), repr(self.ref)))
        except Exception as e:
            return "Error: %s" % str(e)

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

def inputs():
    return ['http://www.google.com',
            'https://alaska.com:8080/me?you=this',
            'http://pages.com/new#fragment',
            'http://mynews.com/query?a=b,c=d#fragment',
            'ftp://me:mexico@alaska.com']

def skip_classes():
    return []

def main(arg):
    u = URL(arg)
    print(u)

if __name__ == '__main__':
    import sys
    s = sys.argv[1]
    main(s)
