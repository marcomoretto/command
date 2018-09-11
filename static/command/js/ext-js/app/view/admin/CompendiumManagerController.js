Ext.define('command.view.admin.CompendiumManagerController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.compendium_manager_controller',

    onSelectDbEngine: function(combo, record, opts) {
        var form = combo.up('form');
        form.down('#db_user').enable();
        form.down('#db_password').enable();
        form.down('#db_host').enable();
        form.down('#db_port').enable();
        if (record.data.db_engine == 'SQLite') {
            form.down('#db_user').disable();
            form.down('#db_password').disable();
            form.down('#db_host').disable();
            form.down('#db_port').disable();
        }
    },

    onInitCompendium: function(b) {
        var grid = b.findParentByType('[xtype="compendium"]');
        var compendium = grid.getSelection()[0].data;
        Ext.MessageBox.show({
            title: 'Inintialize compendium',
            msg: 'You are about to intialize compendium ' + compendium.compendium_nick_name + ' this will erase any existing data. Do you want to continue?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('init_compendium');
                    request.values = compendium.id;
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

    onCreateCompendium: function() {
        var win = Ext.create({
            xtype: 'window_new_compendium'
        });
        var combo = win.down('form').getForm().findField('compendium_type');
        combo.setStore(new command.store.CompendiumType());
        var ws = command.current.ws;
        var operation = 'read_compendium_types';
        var request = win.getRequestObject(operation);
        request.view = '_' + request.view;
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                if (combo.getStore()) {
                    combo.getStore().loadData(action.data.compendium_types);
                }
            }
        });
        ws.stream(request.view).send(request);
    },

    onCreateNewCompendium: function(b) {
        var dbs = [];
        var win = b.findParentByType('[xtype="window_new_compendium"]');
        var formValues = win.down('form').getForm().getValues();
        var request = win.getRequestObject('get_db_list');
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var rep = JSON.parse(response.responseText);
                    if (rep['dbs'].indexOf(formValues['compendium_nick_name']) != -1) {
                        var requestCreate = win.getRequestObject('create_compendium');
                        formValues['create_db'] = false;
                        requestCreate.values = JSON.stringify(formValues);
                        Ext.Ajax.request({
                            url: requestCreate.view + '/' + requestCreate.operation,
                            params: requestCreate,
                            success: function (response) {
                                if (command.current.checkHttpResponse(response)) {
                                    command.current.updatePermission();
                                    win.close();
                                }
                            },
                            failure: function (response) {
                                console.log('Server error', reponse);
                            }
                        });
                    } else {
                        var suWin = Ext.create({
                            title: 'Database admin',
                            xtype: 'login'
                        });
                        suWin.down('form').down('panel').setHtml("<p align='center'>The database doesn't exist. Please provide login <br> and password for a database admin user</p>")
                        suWin.down('form').down('panel').setHidden(false);
                        var suWinButton = suWin.down('form').down('button')
                        suWinButton.clearListeners();
                        suWinButton.el.on('click', function() {
                            var requestCreate = win.getRequestObject('create_compendium');
                            formValues['admin'] = suWin.down('form').getForm().getValues();
                            formValues['create_db'] = true;
                            requestCreate.values = JSON.stringify(formValues);
                            Ext.Ajax.request({
                                url: requestCreate.view + '/' + requestCreate.operation,
                                params: requestCreate,
                                success: function (response) {
                                    if (command.current.checkHttpResponse(response)) {
                                        command.current.updatePermission();
                                        win.close();
                                        suWin.close();
                                    }
                                },
                                failure: function (response) {
                                    console.log('Server error', reponse);
                                }
                            });
                        });
                    }
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });

    },

    onUpdateCompendium: function(b) {
        var grid = b.findParentByType('[xtype="compendium"]');
        var compendium = grid.getSelection()[0].data;
        var win = Ext.create({
            xtype: 'window_new_compendium'
        });
        win.setTitle('Modify compendium ' + compendium.compendium_nick_name);
        win.down('form').getForm().setValues(compendium);
        var button = win.down('toolbar').down('button');
        button.setText('Modify');
        button.clearListeners();
        button.el.on('click', function() {
            var request = win.getRequestObject('update_compendium');
            request.values = win.down('form').getForm().getValues();
            request.values.id = compendium.id;
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
        var db_engine = win.down('form').getForm().findField('db_engine');
        db_engine.setValue(compendium.db_engine);
        db_engine.fireEvent('select', db_engine, db_engine.getSelectedRecord());
        var combo = win.down('form').getForm().findField('compendium_type');
        combo.setStore(new command.store.CompendiumType());
        var ws = command.current.ws;
        var operation = 'read_compendium_types';
        var request = win.getRequestObject(operation);
        request.view = '_' + request.view;
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                if (combo.getStore()) {
                    combo.getStore().loadData(action.data.compendium_types);
                    combo.setValue(compendium.compendium_type.id);
                }
            }
        });
        ws.stream(request.view).send(request);
    },

    onDeleteCompendium: function(b) {
        var grid = b.findParentByType('[xtype="compendium"]');
        var compendium = grid.getSelection()[0].data;
        Ext.MessageBox.show({
            title: 'Delete compendium',
            msg: 'Are you sure you want to delete compendium ' + compendium.compendium_nick_name,
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_compendium');
                    request.values = compendium.id;
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

    onCreateCompendiumType: function() {
        Ext.create({
            xtype: 'window_new_compendium_type'
        });
    },

    onCreateNewCompendiumType: function(b) {
        var win = b.findParentByType('[xtype="window_new_compendium_type"]');
        var ws = command.current.ws;
        var operation = 'create_compendium_type';
        var request = win.getRequestObject(operation);
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

    onUpdateCompendiumType: function(b) {
        var grid = b.findParentByType('[xtype="compendium_type"]');
        var compendiumType = grid.getSelection()[0].data;
        var win = Ext.create({
            xtype: 'window_new_compendium_type'
        });
        win.setTitle('Update Compendium Type ' + compendiumType.name);
        win.down('form').getForm().setValues(compendiumType);
        var button = win.down('toolbar').down('button');
        button.setText('Update');
        button.clearListeners();
        button.el.on('click', function() {
            var request = win.getRequestObject('update_compendium_type');
            request.values = win.down('form').getForm().getValues();
            request.values.id = compendiumType.id;
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

    onDeleteCompendiumType: function(b) {
        var grid = b.findParentByType('[xtype="compendium_type"]');
        var compendiumType = grid.getSelection()[0].data;
        Ext.MessageBox.show({
            title: 'Delete Compendium Type',
            msg: 'Are you sure you want to delete Compendium Type ' + compendiumType.name,
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_compendium_type');
                    request.values = compendiumType.id;
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
    }
});