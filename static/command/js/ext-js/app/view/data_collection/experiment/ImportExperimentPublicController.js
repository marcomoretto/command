Ext.define('command.view.data_collection.experiment.ImportExperimentPublicController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.import_experiment_public_controller',

    onExcludeExperiment: function(b) {
        var values = [];
        var panel = b.up('#experiment_search_result');
        b.up('#experiment_search_result').getSelection().forEach(function (i) {
            values.push(i.id)
        });
        var operation = 'exclude_experiment_public_db';
        var request = panel.getRequestObject(operation);
        request.values = JSON.stringify(values);
        Ext.MessageBox.prompt('Motivation', 'Why do you want to exlude this experiment?', function (btn, text) {
            request.message = text;
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
        });
    },

    onFocusPublicDatabase: function( me, event, eOpts ) {
        var panel = me.up('#experiment_search_options');
        var ws = command.current.ws;
        var operation = 'read_public_db';
        var request = panel.getRequestObject(operation);
        request.view = '_' + request.view;
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                me.getStore().loadData(action.data.public_dbs);
            }
        });
        ws.stream(request.view).send(request);
    },

    onSearchExperimentPublic: function(b) {
        var panel = b.up('#experiment_search_options');
        console.log(b.id);
        var grid = b.up('[xtype="import_experiment_public"]').down('#experiment_search_result');
        var operation = 'search_experiment_public_db';
        var request = panel.getRequestObject(operation);
        request.values = JSON.stringify(b.up('form').getForm().getValues());
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var win = Ext.create({
                        xtype: 'vanishing_confirm_message',
                        width: 500,
                    });
                    win.setMessage('Search process is scheduled and will start as soon as possible!');
                    win.show(win);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onStopSearchExperimentPublic: function(b) {
        var panel = b.up('#experiment_search_options');
        var operation = 'stop_search_experiment_public_db';
        var request = panel.getRequestObject(operation);
        request.values = 'search_experiment_public_db';
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

    onDownloadExperimentData: function(b) {
        var values = [];
        var panel = b.up('#experiment_search_result');
        b.up('#experiment_search_result').getSelection().forEach(function (i) {
            values.push(i.id)
        });
        var operation = 'download_experiment_public_db';
        var request = panel.getRequestObject(operation);
        request.values = JSON.stringify(values);
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

});