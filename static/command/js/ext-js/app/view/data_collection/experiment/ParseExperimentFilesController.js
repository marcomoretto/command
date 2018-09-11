Ext.define('command.view.data_collection.experiment.ExperimentFilesController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.experiment_files_controller',

    onFileAssignmentPlatformClick: function(grid, record, element, rowIndex, e, eOpts ) {
        grid.ownerGrid.last_row_index_clicked = rowIndex;
    },

    onFocusReporterPlatform: function(me, opt) {
        var grid = me.up('grid');
        var plt = grid.store.data.items[grid.last_row_index_clicked];
        var exp_id = grid.up('parse_experiment').command_params;
        request = grid.getRequestObject('read_reporter_platforms');
        request.values = JSON.stringify({
            'experiment_id': exp_id,
            'platform_id': plt.id
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    me.store.loadData(resp.platforms, false);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onFocusLeaveReporterPlatform: function(me, opt) {
        var value = me.getDisplayValue();
        var data_plt_id = null;
        me.store.data.items.find(
            function (e) {
                if (e.data.platform_access_id == value) {
                    data_plt_id = e.data.id;
                }
            }
        );
        var grid = me.up('grid');
        var panel = grid.up('parse_experiment');
        var plt = grid.store.data.items[grid.last_row_index_clicked];
        request = grid.getRequestObject('change_reporter_platforms');
        request.values = JSON.stringify({
            experiment_id: panel.command_params,
            platform_id: plt.id,
            reporter_platform_id: data_plt_id
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

    onExperimentShowParsingError: function(a,b,c,d,e,f,g) {
        if (f.data.status.name == 'entity_script_error') {
            var message = f.data.message_log;
            Ext.MessageBox.show({
                title: message.title,
                msg: "Date: " + message.date + "</br>" + message.message,
                buttons: Ext.MessageBox.OK,
                icon: Ext.MessageBox.ERROR,
                fn: function () {
                }
            });
        }
    },
    
    onChangeAssociatedFileDetails: function(me, newValue, oldValue) {
        var grid = me.up('grid');
        var panel = grid.up('parse_experiment');
        var id = grid.getSelectionModel().getSelection()[0].data.id;
        var field = me.dataIndex;
        var value = newValue;
        var request = null;
        try {
            request = grid.getRequestObject('change_associated_file_details');
        } catch (err) {
            grid = grid.up('grid');
            request = grid.getRequestObject('change_associated_file_details');
        }
        request.values = JSON.stringify({
            experiment_id: panel.command_params,
            associated_file_id: id,
            field: field,
            value: value
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

    onFocusLeaveAssociatedFileDetails: function(me) {
        var grid = me.up('grid');
        var panel = grid.up('parse_experiment');
        var id = grid.getSelectionModel().getSelection()[0].data.id;
        var field = me.dataIndex;
        var value = me.getValue();
        var request = null;
        try {
            request = grid.getRequestObject('change_associated_file_details');
        } catch (err) {
            grid = grid.up('grid');
            request = grid.getRequestObject('change_associated_file_details');
        }
        request.values = JSON.stringify({
            experiment_id: panel.command_params,
            associated_file_id: id,
            field: field,
            value: value
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

    onAssignScripts: function (me, eOpts) {
        var panel = me.up('window_experiment_script_file_assignment');
        var request = panel.getRequestObject('assign_script_to_file');
        request.values = me.up('form').getForm().getValues();
        request.values.experiment_id = panel.command_params;
        request.values.selected_files = panel.selected_files;
        request.values = JSON.stringify(request.values);
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                panel.close();
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onAssignFiles: function (me, eOpts) {
        var panel = me.up('window_experiment_file_assignment');
        var request = panel.getRequestObject('run_assign_script');
        request.values = me.up('form').getForm().getValues();
        request.values.experiment_id = panel.command_params;
        request.values.selected_files = panel.selected_files;
        request.values = JSON.stringify(request.values);
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                panel.close();
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onRunExperimentParsingScript: function(me, idx) {
        var panel = me.findParentByType('[xtype="file_assignment_experiments"]');
        var request = panel.getRequestObject('run_experiment_parsing_script');
        var exp_id = panel.up('parse_experiment').command_params;
        request.values = JSON.stringify({
            experiment_id: exp_id
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

    runPlatformParsingScript: function(request) {
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
    
    onRunMultiplePlatformParsingScript: function(me) {
        var panel = me.findParentByType('[xtype="file_assignment_platforms"]');
        var grid = me.up('grid');
        var exp_id = panel.up('parse_experiment').command_params;
        var request = panel.getRequestObject('run_platform_parsing_script');
        var platform_ids = [];
        if (me.itemId == 'run_all') {
            request.values = JSON.stringify({
                experiment_id: exp_id,
                platform_id: 'all'
            });
        }
        if (me.itemId == 'run_selected') {
            grid.getSelectionModel().getSelection().forEach(function (e) {
                platform_ids.push(e.data.id);
            });
            request.values = JSON.stringify({
                experiment_id: exp_id,
                platform_id: platform_ids
            });
        }
        this.runPlatformParsingScript(request);
    },
    
    onRunPlatformParsingScript: function(me, idx) {
        var item = me.store.data.items[idx];
        var panel = me.findParentByType('[xtype="file_assignment_platforms"]');
        var exp_id = panel.up('parse_experiment').command_params;
        var request = panel.getRequestObject('run_platform_parsing_script');
        request.values = JSON.stringify({
            experiment_id: exp_id,
            platform_id: [item.id]
        });
        this.runPlatformParsingScript(request);
    },

    runSampleParsingScript: function(request) {
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
    
    onRunMultipleSampleParsingScript: function(me) {
        var panel = me.findParentByType('[xtype="file_assignment_samples"]');
        var grid = me.up('grid');
        var exp_id = panel.up('parse_experiment').command_params;
        var request = panel.getRequestObject('run_sample_parsing_script');
        var sample_ids = [];
        if (me.itemId == 'run_all') {
            request.values = JSON.stringify({
                experiment_id: exp_id,
                sample_id: 'all'
            });
        }
        if (me.itemId == 'run_selected') {
            grid.getSelectionModel().getSelection().forEach(function (e) {
                sample_ids.push(e.data.id);
            });
            request.values = JSON.stringify({
                experiment_id: exp_id,
                sample_id: sample_ids
            });
        }
        this.runSampleParsingScript(request);
        
    },

    onRunSampleParsingScript: function(me, idx) {
        var item = me.store.data.items[idx];
        var panel = me.findParentByType('[xtype="file_assignment_samples"]');
        var exp_id = panel.up('parse_experiment').command_params;
        var request = panel.getRequestObject('run_sample_parsing_script');
        request.values = JSON.stringify({
            experiment_id: exp_id,
            sample_id: [item.id]
        });
        this.runSampleParsingScript(request);
    },

    onRemoveExperimentFileAssignment: function(me, idx) {
        var item = me.store.data.items[idx];
        var panel = me.findParentByType('[xtype="file_assignment_experiments"]');
        var exp_id = panel.up('parse_experiment').command_params;
        var request = panel.getRequestObject('remove_file_assignment');
        request.values = JSON.stringify({
            experiment_id: exp_id,
            assigned_file_id: item.id
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    me.store.remove(item);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onRemovePlatformFileAssignment: function(me, idx) {
        var item = me.store.data.items[idx];
        var panel = me.findParentByType('[xtype="file_assignment_platforms"]');
        var exp_id = panel.up('parse_experiment').command_params;
        var request = panel.getRequestObject('remove_file_assignment');
        request.values = JSON.stringify({
            experiment_id: exp_id,
            assigned_file_id: item.id
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    me.store.remove(item);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onRemoveSampleFileAssignment: function(me, idx) {
        var item = me.store.data.items[idx];
        var panel = me.findParentByType('[xtype="file_assignment_samples"]');
        var exp_id = panel.up('parse_experiment').command_params;
        var request = panel.getRequestObject('remove_file_assignment');
        request.values = JSON.stringify({
            experiment_id: exp_id,
            assigned_file_id: item.id
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    me.store.remove(item);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    cleanFileAssignment: function(exp_id, request, entity_type) {
        Ext.MessageBox.show({
            title: 'Clean all assigned files',
            msg: 'Are you sure you want to clean all assigned files?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    request.values = JSON.stringify({
                        experiment_id: exp_id,
                        entity_type: entity_type
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
                }
            }
        })
    },

    onCleanFileAssignment: function(me, eOpts) {
        var exp_id = me.up('parse_experiment').command_params;
        var grid = me.up('file_assignment');
        var request = grid.getRequestObject('clean_file_assignment');
        this.cleanFileAssignment(exp_id, request, 'ALL');
    },

    onCleanExperimentsFileAssignment: function(me, eOpts) {
        var exp_id = me.up('parse_experiment').command_params;
        var grid = me.up('file_assignment_experiments');
        var request = grid.getRequestObject('clean_file_assignment');
        this.cleanFileAssignment(exp_id, request, 'EXP');
    },

    onCleanPlatformsFileAssignment: function(me, eOpts) {
        var exp_id = me.up('parse_experiment').command_params;
        var grid = me.up('file_assignment_platforms');
        var request = grid.getRequestObject('clean_file_assignment');
        this.cleanFileAssignment(exp_id, request, 'PLT');
    },

    onCleanSamplesFileAssignment: function(me, eOpts) {
        var exp_id = me.up('parse_experiment').command_params;
        var grid = me.up('file_assignment_samples');
        var request = grid.getRequestObject('clean_file_assignment');
        this.cleanFileAssignment(exp_id, request, 'SMP');
    },

    onAssignFileToScript: function(me, eOpts) {
        var exp_id = me.up('parse_experiment').command_params;
        var selectedFiles = [];
        me.up('file_assignment').getSelection().forEach(function (e) {
            selectedFiles.push(e.data.name);
        });
        var win = Ext.create({
            xtype: 'window_experiment_script_file_assignment',
            command_params: exp_id,
            selected_files: selectedFiles
        });
    },

    onAssignFileToExperiment: function ( me, eOpts ) {
        var exp_id = me.up('parse_experiment').command_params;
        var selectedFiles = [];
        me.up('file_assignment').getSelection().forEach(function (e) {
            selectedFiles.push(e.data.name);
        });
        var win = Ext.create({
            xtype: 'window_experiment_file_assignment',
            command_params: exp_id,
            selected_files: selectedFiles
        });
    },

    onUploadFile: function ( me, eOpts ) {
        var exp_id = me.up('parse_experiment').command_params;
        var win = Ext.create({
            xtype: 'window_upload_experiment_file_assignment',
            command_params: exp_id
        });
    },

    onExperimentDataChange: function (me, newValue, oldValue, eOpts) {
        me.up('window_upload_experiment_file_assignment').down('button').setDisabled(!newValue);
    },

    onExperimentDataUploadFile: function(me) {
        var panel = me.up('window_upload_experiment_file_assignment');
        var operation = 'upload_experiment_files';
        var request = panel.getRequestObject(operation);
        var form_panel = panel.down('form');
        var form = form_panel.getForm();
        request.values = {
            experiment_id: panel.command_params
        }
        if (form.isValid()) {
            panel.setLoading('Uploading file ...');
            form.submit({
                url: request.view + '/' + request.operation,
                waitMsg: null,
                params: {
                    request: JSON.stringify(request)
                },
                success: function (f, response) {
                    if (command.current.checkHttpResponse(response.response)) {
                        command.current.showMessage('info', 'Experiment uploaded', 'Experiment file will be decompressed (if necessary) in background!')
                        panel.setLoading(false);
                        panel.close();
                    }
                },
                failure: function (f, response) {
                    command.current.checkHttpResponse(response.response);
                    panel.setLoading(false);
                }
            });
        }
    },

    onDeleteFile: function ( me, eOpts ) {
        var panel = me.findParentByType('[xtype="parse_experiment"]');
        var grid = me.findParentByType('[xtype="file_assignment"]');
        var files = [];
        grid.getSelection().forEach(function (e, i) {
            files.push(e.data.name);
        });
        Ext.MessageBox.show({
            title: 'Delete file',
            msg: 'Are you sure you want to delete the selected file(s)?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_file');
                    request.values = JSON.stringify({
                            'experiment_id': parseInt(panel.command_params),
                            'files': files
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
                }
            }
        })
    },

    onFocusExperimentEntityType: function ( me, eOpts ) {
        var panel = me.up('window_experiment_file_assignment');
        var request = panel.getRequestObject('get_script_names');
        request.values = me.entity_type;
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    me.store.loadData(resp.data, false);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onExperimentFileAssignmentWindowAfterRender: function ( me, eOpts ) {
        var request = me.getRequestObject('get_script_names');
        request.values = 'file_assignment';
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    me.down('combo').store.loadData(resp.data, false);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onFocusExperimentExperimentFiles: function (me) {
        var files = me.up('parse_experiment').experiment_files;
        me.store.loadData(files.files, false);
    },

    onFocusExperimentSampleFiles: function (me) {
        var files = me.up('parse_experiment').experiment_files;
        me.store.loadData(files.files, false);
    },

    onFocusExperimentPlatformFiles: function (me) {
        var files = me.up('parse_experiment').experiment_files;
        me.store.loadData(files.files, false);
    },

    onFocusExperimentSampleScripts: function (me) {
        var scripts = me.up('parse_experiment').script_files_sample;
        me.store.loadData(scripts.data, false);
    },

    onFocusExperimentPlatformScripts: function (me) {
        var scripts = me.up('parse_experiment').script_files_platform;
        me.store.loadData(scripts.data, false);
    },

    onFocusExperimentExperimentScripts: function (me) {
        var scripts = me.up('parse_experiment').script_files_experiment;
        me.store.loadData(scripts.data, false);
    },

    onFileAssignmentExperimentAfterRender: function ( me, eOpts ) {
        var panel = me.findParentByType('[xtype="parse_experiment"]');
        var ws = command.current.ws;
        var operation = 'read_experiment_experiment_files';
        var request = me.getRequestObject(operation);
        request.values = panel.command_params;
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                me.store.getProxy().setData(action.data);
                me.store.loadPage(action.request.page, {
                    start: 0
                });
                if (action.data.status.name == 'entity_script_running' ||
                    action.data.status.name == 'entity_script_scheduled') {
                    me.setLoading('Parsing ...');
                } else {
                    me.setLoading(false);
                }
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);
        var operation = 'get_experiment_files';
        var request_ajax = me.getRequestObject(operation);
        request_ajax.values = panel.command_params;
        Ext.Ajax.request({
            url: request_ajax.view + '/' + operation,
            params: request_ajax,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var res = JSON.parse(response.responseText);
                panel.experiment_files = res;
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
        var script_panel = panel.down('script_tree');
        var new_request = script_panel.getRequestObject('get_script_names');
        new_request.values = 'experiment';
        Ext.Ajax.request({
            url: new_request.view + '/' + new_request.operation,
            params: new_request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var res = JSON.parse(response.responseText);
                panel.script_files_experiment = res;
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onFileAssignmentPlatformAfterRender: function ( me, eOpts ) {
        var panel = me.findParentByType('[xtype="parse_experiment"]');
        var paging = me.down('command_paging');
        paging.bindStore(me.store);
        var ws = command.current.ws;
        var operation = 'read_experiment_platform_files';
        var request = me.getRequestObject(operation);
        request.values = panel.command_params;
        me.down('command_paging').values = panel.command_params;
        me.down('command_livefilter').values = panel.command_params;
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
        var operation = 'get_experiment_files';
        var request_ajax = me.getRequestObject(operation);
        request_ajax.values = panel.command_params;
        Ext.Ajax.request({
            url: request_ajax.view + '/' + operation,
            params: request_ajax,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var res = JSON.parse(response.responseText);
                panel.experiment_files = res;
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
        var script_panel = panel.down('script_tree');
        var new_request = script_panel.getRequestObject('get_script_names');
        new_request.values = 'platform';
        Ext.Ajax.request({
            url: new_request.view + '/' + new_request.operation,
            params: new_request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var res = JSON.parse(response.responseText);
                panel.script_files_platform = res;
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onFileAssignmentSamplesAfterRender: function ( me, eOpts ) {
        var panel = me.findParentByType('[xtype="parse_experiment"]');
        var paging = me.down('command_paging');
        paging.bindStore(me.store);
        var ws = command.current.ws;
        var operation = 'read_experiment_sample_files';
        var request = me.getRequestObject(operation);
        request.values = panel.command_params;
        me.down('command_paging').values = panel.command_params;
        me.down('command_livefilter').values = panel.command_params;
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            console.log('SAMPLES!');
            console.log(action);
            console.log(me.id);
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
        var operation = 'get_experiment_files';
        var request_ajax = me.getRequestObject(operation);
        request_ajax.values = panel.command_params;
        Ext.Ajax.request({
            url: request_ajax.view + '/' + operation,
            params: request_ajax,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var res = JSON.parse(response.responseText);
                panel.experiment_files = res;
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
        var script_panel = panel.down('script_tree');
        var new_request = script_panel.getRequestObject('get_script_names');
        new_request.values = 'sample';
        Ext.Ajax.request({
            url: new_request.view + '/' + new_request.operation,
            params: new_request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var res = JSON.parse(response.responseText);
                panel.script_files_sample = res;
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onFileAssignmentAfterRender: function ( me, eOpts ) {
        var panel = me.findParentByType('[xtype="parse_experiment"]');
        var paging = me.down('command_paging');
        paging.bindStore(me.store);
        var ws = command.current.ws;
        var operation = 'read_experiment_files';
        var request = me.getRequestObject(operation);
        request.values = panel.command_params;
        me.down('command_paging').values = panel.command_params;
        me.down('command_livefilter').values = panel.command_params;
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
    }

});