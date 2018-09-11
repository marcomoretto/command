Ext.define('command.view.data_collection.experiment.ParseExperimentEditorController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.parse_experiment_editor_controller',

    editorKeyHandler: function (event, x, y, z) {
        if (event.ctrlKey && !event.shiftKey && event.getKey() == event.S) {
            event.stopEvent();
            var panel = Ext.getCmp(this.id);
            var editorPanel = panel.findParentByType('[xtype="python_editor"]');
            var pythonPanel = editorPanel.down('#ace_python_editor');
            var save_script_button = pythonPanel.down('#save_script_button');
            panel.controller.onSaveScript(save_script_button);
        }
    },

    onSaveScript: function(b) {
        var editorPanel = b.findParentByType('[xtype="python_editor"]');
        var pythonPanel = editorPanel.down('#ace_python_editor');
        var editor = editorPanel.down('#ace_editor');
        var request = pythonPanel.getRequestObject('save_script');
        request.values = JSON.stringify({'file_name': editor.getScriptName(), 'source': editor.getValue()});
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var win = Ext.create({
                        xtype: 'vanishing_confirm_message'
                    });
                    win.setMessage('Script successfully saved!');
                    win.show(win);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });

    },

    onExpandCollapseAll: function(b) {
        var panel = b.findParentByType('[xtype="script_tree"]');
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

    onScriptTreeAfterRender: function (me, eOpts) {
        var ws = command.current.ws;
        var operation = 'read_script_tree';
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
    },

    resetEditor: function(button) {
        var editorPanel = button.up('#python_editor');
        var pythonPanel = editorPanel.down('#ace_python_editor');
        var editor = editorPanel.down('#ace_editor')
        var save_script_button = pythonPanel.down('#save_script_button');
        pythonPanel.setTitle('');
        editor.setScriptName(null);
        editor.setValue('');
        editor.disable();
        save_script_button.disable();
    },

    onSelectTreeItem: function(me, record, index, eOpts) {
        var panel = me.view.findParentByType('[xtype="script_tree"]');
        var editorPanel = me.view.findParentByType('[xtype="python_editor"]');
        var pythonPanel = editorPanel.down('#ace_python_editor');
        var editor = editorPanel.down('#ace_editor')
        var save_script_button = pythonPanel.down('#save_script_button');
        var create_button = panel.down('#create_button');
        var update_button = panel.down('#update_button');
        var delete_button = panel.down('#delete_button');
        if (record.data.leaf) {
            create_button.disable();
            update_button.enable();
            delete_button.enable();
            var request = panel.getRequestObject('read_script_file');
            request.values = JSON.stringify({'file_name': record.data.path});
            Ext.Ajax.request({
                url: request.view + '/' + request.operation,
                params: request,
                success: function (response) {
                    command.current.checkHttpResponse(response);
                    var resp = JSON.parse(response.responseText);
                    var script_text = resp.data;
                    pythonPanel.setTitle('Script editor: ' + record.data.path);
                    editor.setScriptName(record.data.path);
                    editor.setValue(script_text);
                    editor.enable();
                    save_script_button.enable();
                },
                failure: function (response) {
                    console.log('Server error', reponse);
                }
            });
        } else {
            create_button.enable();
            update_button.disable();
            delete_button.disable();
        }
    },

    onCreate: function(b) {
        var me = this;
        var panel = b.findParentByType('[xtype="script_tree"]');
        var request = panel.getRequestObject('create_script_file');
        Ext.MessageBox.prompt('Name', 'Please enter script name:', function (btn, text) {
            request.values = JSON.stringify({'file_name': text, 'path': panel.getSelection()[0].data.path});
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

    onUpdate: function(b) {
        var me = this;
        var panel = b.findParentByType('[xtype="script_tree"]');
        var request = panel.getRequestObject('update_script_file');
        Ext.MessageBox.prompt('Name', 'Please enter new script name:', function (btn, text) {
            if (btn != 'cancel') {
                request.values = JSON.stringify({'file_name': text, 'path': panel.getSelection()[0].data.path});
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
            }
        });
    },

    onDelete: function(b) {
        var me = this;
        var panel = b.findParentByType('[xtype="script_tree"]');
        var file = panel.getSelection()[0].data;
        Ext.MessageBox.show({
            title: 'Delete group',
            msg: 'Are you sure you want to delete ' + file.text,
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = panel.getRequestObject('delete_script_file');
                    request.values = JSON.stringify({'file_name': file.path});
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
                }
            }
        })
    }

});