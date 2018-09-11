import json

from channels import Channel, Group
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.parsing.parsing_experiment import ParsingExperiment
from command.lib.db.parsing.parsing_platform import ParsingPlatform
from command.lib.db.parsing.parsing_sample import ParsingSample
import command.lib.utils.decorators
from command.lib.utils.init_compendium import init_parsing


class MessageLogView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @command.lib.utils.decorators.forward_exception_to_http
    def create_message_log(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)
        message = MessageLog()
        message.title = values['title']
        message.message = values['message']
        message.source = message.SOURCE[0][0]
        message.save(using=compendium.compendium_nick_name)
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @command.lib.utils.decorators.forward_exception_to_http
    def delete_message(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        message = MessageLog.objects.using(compendium.compendium_nick_name).get(id=request.POST['values'])
        message.delete()
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @command.lib.utils.decorators.forward_exception_to_channel
    def read_message_log(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        query_response = MessageLog.objects.using(compendium.compendium_nick_name). \
            filter(Q(title__contains=request['filter']) |
                   Q(message__contains=request['filter'])
                   ).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        messages = []
        for message in query_response:
            msg = message.to_dict()
            messages.append(msg)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'messages': messages,
                        'total': total
                    }
                }
            })
        })
