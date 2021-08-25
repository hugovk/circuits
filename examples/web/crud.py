#!/usr/bin/env python
from circuits.web import Controller, Logger, Server


class Root(Controller):

    def GET(self, *args, **kwargs):
        """GET Request Handler

        The default Dispatcher in circuits.web also looks for GET, POST,
        PUT, DELETE and HEAD Request handlers on registered Controller(s).

        These can be used to implement RESTful resources with CRUD operations.
        """

        return "GET({:s}, {:s})".format(repr(args), repr(kwargs))

    def POST(self, *args, **kwargs):
        return "POST({:s}, {:s})".format(repr(args), repr(kwargs))

    def PUT(self, *args, **kwargs):
        return "PUT({:s}, {:s})".format(repr(args), repr(kwargs))

    def DELETE(self, *args, **kwargs):
        return "DELETE({:s}, {:s})".format(repr(args), repr(kwargs))

    def HEAD(self, *args, **kwargs):
        return "HEAD({:s}, {:s})".format(repr(args), repr(kwargs))


app = Server(("0.0.0.0", 8000))
Logger().register(app)
Root().register(app)
app.run()
