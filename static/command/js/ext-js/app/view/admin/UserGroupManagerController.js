Ext.define('command.view.admin.UserGroupManagerController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.user_group_manager',

    onCreateUser: function(b) {
        var win = Ext.create({
            xtype: 'window_new_user'
        });
        var height = win.getHeight();
        var groups = win.down('form').getForm().findField('groups');
        var ws = command.current.ws;
        var operation = 'read_groups';
        var request = win.getRequestObject(operation);
        request.view = '_' + request.view;
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                try {
                    action.data.groups.forEach(function (e) {
                        groups.add({
                            boxLabel: e.name,
                            name: 'group_id',
                            inputValue: e.id
                        });
                    });
                    win.setHeight(height + (20 * action.data.total));
                } catch(err) {}
            }
        });
        ws.stream(request.view).send(request);
    },

    onCreateNewUser: function(b) {
        var win = b.findParentByType('[xtype="window_new_user"]');
        var request = win.getRequestObject('create_user');
        request.values = JSON.stringify(win.down('form').getForm().getValues());
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    win.close();
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onUpdateUser: function(b) {
        var grid = b.findParentByType('[xtype="user"]');
        var user = grid.getSelection()[0].data;
        var win = Ext.create({
            xtype: 'window_new_user'
        });
        var height = win.getHeight();
        win.setTitle('Update user ' + user.username);
        win.down('form').getForm().setValues(user);
        var admin = win.down('form').getForm().findField('admin');
        var reset_password = win.down('form').getForm().findField('reset_password');
        var active = win.down('form').getForm().findField('active');
        var button = win.down('toolbar').down('button');
        var groups = win.down('form').getForm().findField('groups');
        var ws = command.current.ws;
        var operation = 'read_groups';
        var request = win.getRequestObject(operation);
        request.view = '_' + request.view;
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                try {
                    var group_names = [];
                    user.user_groups.forEach(function(e) {
                        group_names.push(e.id);
                    });
                    action.data.groups.forEach(function (e) {
                        groups.add({
                            boxLabel: e.name,
                            name: 'group_id',
                            inputValue: e.id,
                            checked: group_names.indexOf(e.id) != -1
                        });
                    });
                    win.setHeight(height + (20 * action.data.total));
                } catch(err) {}
            }
        });
        ws.stream(request.view).send(request);
        admin.setValue(user.is_superuser);
        active.setValue(user.is_active);
        reset_password.setDisabled(false);
        reset_password.setValue(false);
        button.setText('Update');
        button.clearListeners();
        button.el.on('click', function() {
            var request = win.getRequestObject('update_user');
            request.values = win.down('form').getForm().getValues();
            request.values.id = user.id;
            request.values = JSON.stringify(request.values);
            Ext.Ajax.request({
                url: request.view + '/' + request.operation,
                params: request,
                success: function (response) {
                    if (command.current.checkHttpResponse(response)) {
                        win.close();
                    }
                },
                failure: function (response) {
                    console.log('Server error', reponse);
                }
            });
        });
    },

    onDeleteUser: function(b) {
        var grid = b.findParentByType('[xtype="user"]');
        var user = grid.getSelection()[0].data;
        Ext.MessageBox.show({
            title: 'Delete user',
            msg: 'Are you sure you want to delete user ' + user.username,
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_user');
                    request.values = user.id;
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    });
                }
            }
        })
    },

    onCreateGroup: function() {
        Ext.create({
            xtype: 'window_new_group'
        });
    },

    onCreateNewGroup: function(b) {
        var win = b.findParentByType('[xtype="window_new_group"]');
        var request = win.getRequestObject('create_group');
        request.values = win.down('form').getForm().getValues();
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    win.close();
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onDeleteGroup: function(b) {
        var grid = b.findParentByType('[xtype="group"]');
        var group = grid.getSelection()[0].data;
        Ext.MessageBox.show({
            title: 'Delete group',
            msg: 'Are you sure you want to delete group ' + group.name,
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_group');
                    request.values = group.id;
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    });
                }
            }
        })
    },

    onUpdateGroup: function(b) {
        var grid = b.up('#group');
        var group = grid.getSelection()[0].data;
        var win = Ext.create({
            xtype: 'window_new_group'
        });
        win.setTitle('Update group ' + group.name);
        win.down('form').getForm().setValues(group);
        var button = win.down('toolbar').down('button');
        button.setText('Update');
        button.clearListeners();
        button.el.on('click', function() {
            var request = win.getRequestObject('update_group');
            request.values = win.down('form').getForm().getValues();
            request.values.id = group.id;
            request.values = JSON.stringify(request.values);
            Ext.Ajax.request({
                url: request.view + '/' + request.operation,
                params: request,
                success: function (response) {
                    if (command.current.checkHttpResponse(response)) {
                        win.close();
                    }
                },
                failure: function (response) {
                    console.log('Server error', reponse);
                }
            });
        });
    },

    onGroupSelection: function (dv, record, item, index, e) {
        var parent = dv.findParentByType('main');
        var compendiumGrid = parent.down('#compendium_privileges');
        console.log(compendiumGrid.id);
        compendiumGrid.setDisabled(false);
        compendiumGrid.setDisabled(true);
        compendiumGrid.setDisabled(false);
        var compendium = compendiumGrid.getSelection()[0];
        if (compendium) {
            this.onCompendiumSelection(dv.up('component'));
        }
    },

    onPrivilegesAfterRender: function ( me, eOpts ) {
        var ws = command.current.ws;
        var operation = 'read_privileges';
        var request = me.getRequestObject(operation);
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                me.getRootNode().removeAll();
                me.getRootNode().appendChild(action.data.privileges);
                console.log(action.data.privileges);
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);
    },

    onCompendiumAfterRender: function(me) {
        var paging = me.down('command_paging');
        paging.displayMsg = '';
        paging.doRefresh();
        var toolbar = me.down('toolbar');
        var filter = me.down('command_livefilter');
        var new_toolbar = me.addDocked({
            xtype:'toolbar',
            border: 0,
            style: {
                borderColor: 'white',
                borderStyle: 'solid'
            }
        });
        new_toolbar[0].add(filter);
        toolbar.remove(filter);
        var bottom_toolbar = me.getDockedItems().find(
            function(e) {
                if (e.dock=='bottom')
                    return e;
            });
        me.removeDocked(bottom_toolbar);
        me.setDisabled(false);
        me.setDisabled(true);
    },

    onPrivilegesCheckChange: function(node, checked, options){
        var parent = this.view;
        var groupGrid = parent.down('#group');
        var group = groupGrid.getSelection()[0];
        var compendiumGrid = parent.down('#compendium_privileges');
        var preferencesPanel = parent.down('#privileges');
        var compendium = compendiumGrid.getSelection()[0];
        var request = groupGrid.getRequestObject('update_group_privileges');
        if (node.data.leaf) {
            request.values = {'compendium_id': compendium.id, 'group_id': group.id,
                'permission_codename': [node.data.codename], 'select': checked};
        } else {
            request.values = {'compendium_id': compendium.id, 'group_id': group.id,
                'permission_codename': [], 'select': checked};
            node.cascadeBy(function(n){
                n.set('checked', checked);
                if (n.data.leaf) {
                    request.values.permission_codename.push(n.data.codename);
                }
            });
        }
        request.values = JSON.stringify(request.values);
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onCompendiumSelection: function ( dv, record, index, eOpts ) {
        var ws = command.current.ws;
        var operation = 'read_privileges';
        var parent = dv.view.findParentByType('main');
        var privileges = parent.down('#privileges');
        var groupGrid = parent.down('#group');
        var group = groupGrid.getSelection()[0];
        var compendiumGrid = parent.down('#compendium_privileges');
        var compendium = compendiumGrid.getSelection()[0];
        var request = privileges.getRequestObject(operation);
        request.values = JSON.stringify({'compendium_id': compendium.id, 'group_id': group.id});
        ws.stream(request.view).send(request);
        privileges.enable();
    }
});