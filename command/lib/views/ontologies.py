import json

from django.http import HttpResponse
from django.views import View

from command.lib.utils.decorators import forward_exception_to_http


class OntologiesView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    def read_ontologies(request, *args, **kwargs):

        #app = TerminalIPythonApp.instance()
        #app.initialize(argv=[])
        #a = app.code_to_run("print('hello')")
        #app.start()

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def new_ontology(request, *args, **kwargs):
        # app = TerminalIPythonApp.instance()
        # app.initialize(argv=[])
        # a = app.code_to_run("print('hello')")
        # app.start()
        ontology = [
            {'data': {'id': 'a'}},
            {'data': {'id': 'b'}},
            {'data': {'id': 'c'}},
            {'data': {'id': 'ac', 'source': 'a', 'target': 'c'}},
            {'data': {'id': 'ab', 'source': 'a', 'target': 'b'}}
        ]
        return HttpResponse(json.dumps({'success': True, 'ontology': ontology}),
                            content_type="application/json")