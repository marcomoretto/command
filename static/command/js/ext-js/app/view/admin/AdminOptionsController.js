Ext.define('command.view.admin.AdminOptionsController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.admin_options_controller',

    onAdminOptionsAfterRender: function ( me, eOpts ) {
        var ws = command.current.ws;
        var operation = 'read_admin_options';
        var request = this.view.getRequestObject(operation);
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                action.data.admin_options.forEach(function (i) {
                    var option = me.down('#' + i.option_name);
                    option.setValue(i.option_value);
                });
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);
    },

    onClearDirectory: function(b) {
        var panel = b.up('#admin_options');
        var values = b.up('form').getForm().getValues();
        var request = panel.getRequestObject('clear_admin_options_directory');
        request.values = JSON.stringify(values);
        Ext.MessageBox.show({
            title: 'Clear directory',
            msg: 'You are about to DELETE ALL FILES in this directory. Do you want to continue?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            if (command.current.checkHttpResponse(response)) {
                                Ext.MessageBox.show({
                                    title: 'Directory is clear',
                                    msg: 'Directory successfully cleared',
                                    buttons: Ext.MessageBox.OK,
                                    icon: Ext.MessageBox.INFO,
                                    fn: function () {
                                    }
                                });
                            }
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    });
                }
            }
        })
    },

    onCheckDirectory: function(b) {
        var panel = b.up('#admin_options');
        var values = b.up('form').getForm().getValues();
        var request = panel.getRequestObject('update_admin_options_directory');
        request.values = JSON.stringify(values);
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    Ext.MessageBox.show({
                        title: 'Directory changed',
                        msg: 'Directory changed successfully',
                        buttons: Ext.MessageBox.OK,
                        icon: Ext.MessageBox.INFO,
                        fn: function () {
                        }
                    });
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    }
});