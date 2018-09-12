import json
import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render

import command
from command.consumers import GroupCompendiumPermission
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.models import init_database_connections


def index(request):
    return render(request, 'command/index.html', None)


def do_logout(request):
    logout(request)
    return HttpResponse(json.dumps({'error': False, 'login': False}), content_type="application/json")


def reset_password(request):
    try:
        request.user.set_password(request.POST['password'])
        request.user.save()
    except Exception as e:
        pass
    return do_logout(request)


def update_permission(request):
    user = request.user
    if user.is_authenticated() and user.is_active:
        views = GroupCompendiumPermission.get_permitted_views(user)
        return HttpResponse(
            json.dumps({
                'login': True,
                'views': views
            }), content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({
                'login': False,
                'views': []
            }), content_type="application/json")


def check_bio_features(request):
    comp = json.loads(request.POST['compendium'])
    init_database_connections()
    compendium = CompendiumDatabase.objects.get(id=comp['id'])
    bio_features = BioFeature.objects.using(compendium.compendium_nick_name).count() > 0
    return HttpResponse(
        json.dumps({
            'bio_features': bio_features
        }), content_type="application/json")


def check_login(request):
    try:
        build_file = os.path.join(settings.BASE_DIR, 'build')
        build = "0"
        if os.path.exists(build_file) and os.path.isfile(build_file):
            with open(build_file, 'r') as content_file:
                build = content_file.read()
        version = command.__version__ + "." + build
        user = request.user
        current_compendium = {'id': None, 'compendium_name': None, 'compendium_nick_name': None}
        if user.is_authenticated() and user.is_active:
            reset_password = user.check_password(user.username)
            views = GroupCompendiumPermission.get_permitted_views(user)
            return HttpResponse(
                json.dumps({
                        'current_compendium': current_compendium,
                        'reset_password': reset_password,
                        'error': False,
                        'login': True,
                        'username': user.username,
                        'version': version,
                        'is_admin': user.is_staff and user.is_superuser,
                        'views': views
                    }), content_type="application/json")
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            reset_password = user.check_password(user.username)
            views = GroupCompendiumPermission.get_permitted_views(user)
            return HttpResponse(
                json.dumps({
                    'current_compendium': current_compendium,
                    'reset_password': reset_password,
                    'error': False,
                    'login': True,
                    'username': user.username,
                    'version': version,
                    'is_admin': user.is_staff and user.is_superuser,
                    'views': views
                }), content_type="application/json")
    except Exception as e:
        pass
    return HttpResponse(
        json.dumps({
            'current_compendium': None,
            'reset_password': False,
            'error': False,
            'login': False,
            'username': '',
            'version': None,
            'is_admin': False,
            'views': []
        }), content_type="application/json")