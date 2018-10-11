/**
 * This class is the controller for the main view for the application. It is specified as
 * the "controller" of the Main view class.
 *
 * TODO - Replace this content of this view to suite the needs of your application.
 */
Ext.define('command.view.normalization.jupyter_notebook.JupyterNotebookController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.jupyter_notebook',

    onDeleteNotebook: function(b, eOpts) {
        var me = this;
        var panel = b.findParentByType('[xtype="notebook_tree"]');
        var file = panel.getSelection()[0].data;
        var type = 'notebook';
        var msg = 'Are you sure you want to delete ' + file.text;
        if (file.leaf) {
            msg += ' ' + type + '?'
        } else {
            type = 'folder';
            msg += ' ' + type + ' and all its content?'
        }
        Ext.MessageBox.show({
            title: 'Delete ' + type,
            msg: msg,
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = panel.getRequestObject('delete_notebook_file_folder');
                    request.values = JSON.stringify({'file_name': file.path, 'type': type});
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

    onUpdateNotebook: function(b, eOpts) {
        var me = this;
        var panel = b.findParentByType('[xtype="notebook_tree"]');
        var request = panel.getRequestObject('update_notebook_file_folder');
        var file = panel.getSelection()[0].data;
        var type = 'notebook';
        if (!file.leaf) {
            type = 'folder';
        }
        Ext.MessageBox.prompt('Name', 'Please enter new ' + type + ' name:', function (btn, text) {
            if (btn != 'cancel') {
                request.values = JSON.stringify({'file_name': text,
                    'path': panel.getSelection()[0].data.path,
                    'type': type});
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
    },

    onCreateNotebook: function(b, eOpts) {
        var me = this;
        var panel = b.findParentByType('[xtype="notebook_tree"]');
        var request = panel.getRequestObject('create_notebook_file_folder');
        Ext.MessageBox.prompt('Name', 'Please enter notebook name:', function (btn, text) {
            request.values = JSON.stringify({'type': 'file', 'file_name': text, 'path': panel.getSelection()[0].data.path});
            Ext.Ajax.request({
                url: request.view + '/' + request.operation,
                params: request,
                success: function (response) {
                    command.current.checkHttpResponse(response);
                    me.resetEditor(b);
                },
                failure: function (response) {
                    console.log('Server error', reponse);
                }
            });
        });
    },

    onCreateFolder: function(b, eOpts) {
        var me = this;
        var panel = b.findParentByType('[xtype="notebook_tree"]');
        var request = panel.getRequestObject('create_notebook_file_folder');
        Ext.MessageBox.prompt('Name', 'Please enter folder name:', function (btn, text) {
            request.values = JSON.stringify({'type': 'folder', 'file_name': text, 'path': panel.getSelection()[0].data.path});
            Ext.Ajax.request({
                url: request.view + '/' + request.operation,
                params: request,
                success: function (response) {
                    command.current.checkHttpResponse(response);
                    me.resetEditor(b);
                },
                failure: function (response) {
                    console.log('Server error', reponse);
                }
            });
        });
    },

    onJupyterNotebookAfterRenderer: function ( me, eOpts ) {
        var main = Ext.ComponentQuery.query('#main_panel')[0];
        var request = main.getRequestObject('get_notebook_ip');
        request.view = 'jupyter_notebook';
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var resp = JSON.parse(response.responseText);
                me.getEl().dom.src = resp.jupyter_notebook_ip;
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onNotebookDoubleClick: function( me, record, item, index, e, eOpts ) {
        var main = Ext.ComponentQuery.query('#main_panel')[0];
        var request = main.getRequestObject('get_notebook_ip');
        request.view = 'jupyter_notebook';
        request.values = JSON.stringify(record.data);
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var resp = JSON.parse(response.responseText);
                console.log(resp.jupyter_notebook_ip);
                console.log(me.id);
                var notebook = me.up('#jupyter_notebook').down('notebook');
                notebook.getEl().dom.src = resp.jupyter_notebook_ip;
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onExpandCollapseAll: function(b) {
        var panel = b.findParentByType('[xtype="notebook_tree"]');
        if (b.itemId == 'expand_all_button') {
            panel.expandAll();
            b.setVisible(false);
            panel.down('#collapse_all_button').setVisible(true);
        }
        if (b.itemId == 'collapse_all_button') {
            panel.collapseAll();
            b.setVisible(false);
            panel.down('#expand_all_button').setVisible(true);
        }

    },

    onNotebookTreeAfterRender: function( me, eOpts ) {
        var ws = command.current.ws;
        var operation = 'read_notebook_tree';
        var request = me.getRequestObject(operation);
        ws.listen();
        ws.demultiplex(request.view, function (action, stream) {
            if (action.request.operation == request.operation) {
                me.getRootNode().removeAll();
                me.getRootNode().appendChild(action.data);
                if (action.request.filter !== '') {
                    me.expandAll();
                }
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);
    }
});
