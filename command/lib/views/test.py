import json

#from IPython.terminal.ipapp import TerminalIPythonApp
from django.http import HttpResponse
from django.views import View

from command.lib.utils.decorators import forward_exception_to_http


class TestView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    def test(request, *args, **kwargs):

        #app = TerminalIPythonApp.instance()
        #app.initialize(argv=[])
        #a = app.code_to_run("print('hello')")
        #app.start()

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")