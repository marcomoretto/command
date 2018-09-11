import json


class Message:

    def __init__(self, type='info', title='', message=''):
        self.type = type
        self.title = title
        self.message = message

    def to_dict(self):
        return {'success': False, 'type': self.type, 'title': self.title, 'message': self.message}

    def send_to(self, channel):
        channel.send({
            'text': json.dumps({
                'stream': 'message',
                'payload': {
                    'request': {
                        'type': self.type
                    },
                    'data': {
                        'title': self.title,
                        'message': self.message
                    }
                }
            })
        })
