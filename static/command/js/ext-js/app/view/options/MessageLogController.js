Ext.define('command.view.option.MessageLogController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.message_log_controller',

    onMessageLogAfterRender: function ( me, eOpts ) {
        var paging = me.down('command_paging');
        var operation = 'read_message_log';
        var ws = command.current.ws;
        var request = me.getRequestObject(operation);
        paging.bindStore(me.store);
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                me.store.getProxy().setData(action.data);
                me.store.loadPage(action.request.page, {
                    start: 0
                });
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);

    },

    onCreateMessage: function(b) {
        Ext.create({
            xtype: 'window_new_message_log'
        });
    },

    onCreateNewMessageLog: function(b) {
        var win = b.findParentByType('[xtype="window_new_message_log"]');
        var request = win.getRequestObject('create_message_log');
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
    
    onDeleteMessage: function(b) {
        var grid = b.findParentByType('[xtype="message_log_grid"]');
        var message = grid.getSelection()[0].data;
        Ext.MessageBox.show({
            title: 'Delete message log',
            msg: 'Are you sure you want to delete this message log?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_message');
                    request.values = message.id;
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