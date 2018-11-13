Ext.define('command.view.normalization.norm_manager.NormalizationManagerController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.normalization_manager_controller',

    onDeleteNormalization: function (me) {
        var panel = me.up('normalization_manager').down('normalization_experiment_list');
        var grid = me.up('normalization_manager').down('normalization_list');
        Ext.MessageBox.show({
            title: 'Remove normalization',
            msg: 'Are you sure you want to remove this normalization?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = panel.getRequestObject('remove_normalization');
                    request.values = grid.getSelection()[0].id;
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

    onNormalizeExperiment: function (me) {
        var panel = me.up('#normalization_manager').down('#normalization_experiment_list');
        var exp = panel.getSelection()[0];
        command.current.onShowPanel('normalization_experiment', exp.data.id);
    },

    AddExperimentAfterRender: function (me) {
        var ws = command.current.ws;
        var operation = 'read_experiments';
        var panel = me.up('#add_experiment_panel');
        var win = panel.up('window');
        var experimentPanel = me.up('#add_experiment_panel')
        var request = experimentPanel.getRequestObject(operation);
        var requestEmpty = experimentPanel.getRequestObject(operation);
        ws.listen();
        ws.demultiplex(request.view, function (action, stream) {
            if (action.request.operation == request.operation) {
                if (me.store) {
                    if (me.getValue()) {
                        me.store.getProxy().setData(action.data.experiments);
                        me.store.suspendEvents();
                        me.store.clearFilter();
                        me.store.resumeEvents();
                        me.store.filter({
                            property: 'experiment_access_id',
                            anyMatch: true,
                            value: me.getValue()
                        });
                    } else {
                        me.store.setData(action.data.experiments);
                    }
                }
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        requestEmpty.values = {'normalization_id': win.normalization_id, 'text': null};
        ws.stream(requestEmpty.view).send(requestEmpty);
    },

    onChangeAddExperiment: function (me, newValue, oldValue, eOpts) {
        var panel = me.up('#add_experiment_panel');
        var win = panel.up('window');
        var ws = command.current.ws;
        var operation = 'read_experiments';
        var request = panel.getRequestObject(operation);
        request.values = {'normalization_id': win.normalization_id, 'text': newValue};
        ws.stream(request.view).send(request);
    },

    onAddSingleExperiment: function (me) {
        var panel = me.up('#add_experiment_panel');
        var win = panel.up('window');
        var request = panel.getRequestObject('add_experiment');
        var valid = panel.down('#experiment').getSelection().data.valid;
        var form = panel.down('form').getForm();
        request.view = 'normalization_manager';
        if (valid) {
            request.values = form.getValues();
            request.values.id = win.normalization_id
            if (form.isValid()) {
                form.submit({
                    url: request.view + '/' + request.operation,
                    waitMsg: null,
                    params: {
                        values: JSON.stringify(request)
                    },
                    success: function (f, response) {
                        command.current.checkHttpResponse(response.response);
                        win.close();
                    },
                    failure: function (f, response) {
                        win.close();
                    }
                });
            }
        } else {
            Ext.MessageBox.show({
                title: 'Invalid experiment',
                msg: 'Please select a valid experiment from the dropdown menu',
                buttons: Ext.MessageBox.OK,
                icon: Ext.MessageBox.ERROR,
                fn: function () {
                }
            });
        }
    },

    onUseExperimentCheckChange: function (me, rowIndex, checked, record, e, eOpts) {
        var experimentPanel = me.up('#normalization_experiment_list');
        var request = experimentPanel.getRequestObject('update_use_experiment');
        request.values = JSON.stringify({
            'normalization_experiment_id': record.id,
            'checked': checked
        });
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

    onRemoveAllExperiments: function (me) {
        var panel = me.up('#normalization_manager').down('#normalization_list');
        var experimentPanel = me.up('#normalization_manager').down('#normalization_experiment_list');
        var ws = command.current.ws;
        Ext.MessageBox.show({
            title: 'Remove experiments',
            msg: 'Are you sure you want to remove all experiments from the normalization?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = experimentPanel.getRequestObject('remove_all_experiment');
                    request.values = panel.getSelection()[0].id;
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                            ws.stream(request.view).send(request);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    });
                }
            }
        })
    },

    onRemoveSelectedExperiment: function (me) {
        var panel = me.up('#normalization_manager').down('#normalization_list');
        var experimentPanel = me.up('#normalization_manager').down('#normalization_experiment_list');
        var exp = experimentPanel.getSelection()[0];
        Ext.MessageBox.show({
            title: 'Remove experiment ' + exp.data.experiment.experiment_access_id,
            msg: 'Are you sure you want to remove experiment ' + exp.data.experiment.experiment_access_id + ' from the normalization?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = experimentPanel.getRequestObject('remove_experiment');
                    request.values = exp.id;
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

    onAddAllExperiments: function (me) {
        var panel = me.up('#normalization_manager').down('#normalization_list');
        var experimentPanel = me.up('#normalization_manager').down('#normalization_experiment_list');
        request = experimentPanel.getRequestObject('add_all_experiment');
        request.values = panel.getSelection()[0].id;
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

    onAddExperiment: function (me) {
        var panel = me.up('#normalization_manager').down('#normalization_list');
        var win = command.current.createWin({
            xtype: 'window_add_experiment',
            normalization_id: panel.getSelection()[0].id
        });
    },

    onSelectNormalization: function (me, record, item, index, e) {
        var experimentPanel = me.up('#normalization_manager').down('#normalization_experiment_list');
        var buttonAdd = experimentPanel.down('#add_experiment_button');
        var buttonRemove = experimentPanel.down('#remove_experiment_button');
        buttonAdd.setDisabled(false);
        buttonRemove.setDisabled(false);
        experimentPanel.setTitle('Experiments for normalization ' + record.data.name);
        var ws = command.current.ws;
        var request = experimentPanel.getRequestObject('read_normalization_experiments');
        request.values = record.data.id;
        experimentPanel.down('command_livefilter').values = record.data.id;
        experimentPanel.down('command_paging').values = record.data.id;
        ws.stream(request.view).send(request);
    },

    onUpdateNormalization: function (me) {
        var grid = me.up('normalization_manager').down('normalization_list');
        var norm = grid.getSelection()[0];
        var win = command.current.createWin({
            xtype: 'window_new_normalization',
            title: 'Update normalization ' + norm.data.name
        });
        var form = win.down('form');
        var panel = win.down('#new_normalization_panel');
        var combo = panel.down('#normalization_type');
        request = panel.getRequestObject('get_normalization_type');
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    combo.store.loadData(resp.normalization_type, false);
                    form.getForm().setValues(norm.data);
                    combo.setValue(norm.data.normalization_type.id);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
        var button = panel.down('#create_normalization_button');
        button.setText('Update normalization');
        button.clearListeners();
        button.el.on('click', function() {
            var updateRequest = panel.getRequestObject('update_normalization');
            updateRequest.values = form.getValues();
            updateRequest.values.normalization_id = norm.id;
            if (form.isValid()) {
                form.submit({
                    url: updateRequest.view + '/' + updateRequest.operation,
                    waitMsg: null,
                    params: {
                        request: JSON.stringify(updateRequest)
                    },
                    success: function (f, response) {
                        if (command.current.checkHttpResponse(response.response)) {
                            win.close();
                        }
                    },
                    failure: function (f, response) {
                        command.current.checkHttpResponse(response.response);
                    }
                });
            }
        });
        console.log(norm);
    },

    onCreateNormalization: function (me) {
        var panel = me.up('#new_normalization_panel');
        var win = me.up('window_new_normalization');
        var operation = 'create_normalization';
        var request = panel.getRequestObject(operation);
        var form = me.up('form');
        request.values = form.getValues();
        if (form.isValid()) {
            form.submit({
                url: request.view + '/' + request.operation,
                waitMsg: null,
                params: {
                    request: JSON.stringify(request)
                },
                success: function (f, response) {
                    if (command.current.checkHttpResponse(response.response)) {
                        win.close();
                    }
                },
                failure: function (f, response) {
                    command.current.checkHttpResponse(response.response);
                }
            });
        }
    },

    onFocusNormalizationType: function (me, eOpts) {
        var panel = me.up('#new_normalization_panel');
        request = panel.getRequestObject('get_normalization_type');
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    me.store.loadData(resp.normalization_type, false);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onNewNormalization: function (me) {
        var win = command.current.createWin({
            xtype: 'window_new_normalization'
        });
    }
});
