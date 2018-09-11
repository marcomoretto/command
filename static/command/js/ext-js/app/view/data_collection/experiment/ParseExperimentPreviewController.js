Ext.define('command.view.data_collection.experiment.ParseExperimentPreviewController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.parse_experiment_preview_controller',

    _checkImportedPlatforms: function(exp_id, importedPlatforms, request, no_clause) {
        if (importedPlatforms.length > 0) {
            Ext.MessageBox.show({
                title: 'Platforms',
                msg: 'Platform(s) ' + importedPlatforms.join(',') + ' are already imported.' +
                'Do you want to re-import it(them) or keep the existing one(s)?',
                buttons: Ext.MessageBox.YESNO,
                icon: Ext.MessageBox.QUESTION,
                buttonText: {
                    yes    : "Re-import",
                    no     : "Keep existing"
                },
                fn: function (a) {
                    if (a == 'yes') {
                        Ext.Ajax.request({
                            url: request.view + '/' + request.operation + '/' + exp_id,
                            params: request,
                            success: function (response) {
                                command.current.checkHttpResponse(response);
                            },
                            failure: function (response) {
                                console.log('Server error', reponse);
                            }
                        });
                    }
                    if (a == 'no' && no_clause) {
                        request.keep_platform = true;
                        Ext.Ajax.request({
                            url: request.view + '/' + request.operation + '/' + exp_id,
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
            });
        } else {
            Ext.Ajax.request({
                url: request.view + '/' + request.operation + '/' + exp_id,
                params: request,
                success: function (response) {
                    command.current.checkHttpResponse(response);
                },
                failure: function (response) {
                    console.log('Server error', reponse);
                }
            });
        }

    },

    onImportExperiment: function(b) {
        var me = this;
        var panel = b.up('#experiment_preview');
        var exp_id = panel.up('parse_experiment').command_params;
        var experiment_status = panel.up('parse_experiment').experiment_status;
        var experiment_access_id = panel.up('parse_experiment').experiment_access_id;
        var operation = 'import_experiment';
        var request = panel.getRequestObject(operation);
        request.values = exp_id;
        var importedPlatforms = [];
        panel.down('platform_preview').store.data.items.forEach(function (e) {
            if (e.data.is_imported) {
                if (e.data.platform_type != 'rnaseq') {
                    importedPlatforms.push(e.data.platform_access_id);
                }
            }
        });
        if (experiment_status && experiment_status == 'experiment_raw_data_imported') {
            Ext.MessageBox.show({
                title: 'Experiment',
                msg: 'Experiment ' + experiment_access_id + ' is already imported. If you continue descriptions will be updated and samples raw data will be added. Continue?',
                buttons: Ext.MessageBox.YESNOCANCEL,
                icon: Ext.MessageBox.INFO,
                fn: function (a) {
                    if (a == 'yes') {
                        me._checkImportedPlatforms(exp_id, importedPlatforms, request, true);
                    }
                }
            });
        } else {
            me._checkImportedPlatforms(exp_id, importedPlatforms, request, true);
        }
    },
    
    onImportExperimentPlatform: function(b) {
        var panel = b.up('#experiment_preview');
        var exp_id = panel.up('parse_experiment').command_params;
        var operation = 'import_experiment_platform';
        var request = panel.getRequestObject(operation);
        request.values = exp_id;
        var importedPlatforms = [];
        panel.down('platform_preview').store.data.items.forEach(function (e) {
            if (e.data.is_imported) {
                if (e.data.platform_type != 'rnaseq') {
                    importedPlatforms.push(e.data.platform_access_id);
                }
            }
        });
        this._checkImportedPlatforms(exp_id, importedPlatforms, request);
    },

    onSamplePreviewDoubleClick: function(dv, record, item, index, e) {
        var win = Ext.create({
            xtype: 'window_parse_experiment_preview_raw_data',
            title: 'Raw data for sample ' + record.data.sample_name,
            sample: record.data
        });
    },

    onPlatformPreviewDoubleClick: function(dv, record, item, index, e) {
        switch (record.data.platform_type) {
            case 'microarray':
                var win = Ext.create({
                    xtype: 'window_parse_experiment_preview_bio_feature_reporter',
                    title: 'Microarray platform ' + record.data.platform_access_id + ' (' +  record.data.bio_feature_reporter_name + ')',
                    platform: record.data
                });
                break;
            case 'rnaseq':
                Ext.MessageBox.show({
                    title: 'RNA-seq platform',
                    msg: record.data.platform_access_id +  ' is an RNA-seq platform.',
                    buttons: Ext.MessageBox.OK,
                    icon: Ext.MessageBox.INFO,
                    fn: function (a) {
                    }
                });
                break;
            default:
                Ext.MessageBox.show({
                    title: 'Cannot show biological features reported',
                    msg: 'Platform ' + record.data.platform_access_id +  ' does not have a valid type (yet)! You need to specify platform type during parsing.',
                    buttons: Ext.MessageBox.OK,
                    icon: Ext.MessageBox.ERROR,
                    fn: function (a) {
                    }
                });
        }
    },

    onPlatformPreviewAfterRender: function ( me, eOpts ) {
        var paging = me.down('command_paging');
        var panel = me.up('parse_experiment');
        var operation = 'read_platform_preview';
        var ws = command.current.ws;
        var request = me.getRequestObject(operation);
        var importButton = me.up('experiment_preview').down('[itemId="import_button"]');
        request.values = panel.command_params;
        paging.values = panel.command_params;
        me.down('command_livefilter').values = panel.command_params;
        paging.bindStore(me.store);
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                var allRNAseq = true;
                action.data.platforms.forEach(function(e, i) {
                    if (e.platform_type != 'rnaseq') {
                        allRNAseq = false;
                    }
                });
                panel.down('#import_platform_only_menu_item').setDisabled(allRNAseq);
                me.store.getProxy().setData(action.data);
                me.store.loadPage(action.request.page, {
                    start: 0
                });
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
            if (action.data && action.data.status == 'importing') {
                panel.setLoading('Importing ...');
            } else {
                panel.setLoading(false);
            }
        });
        ws.stream(request.view).send(request);
    },

    onSamplePreviewAfterRender: function ( me, eOpts ) {
        var paging = me.down('command_paging');
        var panel = me.up('parse_experiment');
        var operation = 'read_sample_preview';
        var ws = command.current.ws;
        var request = me.getRequestObject(operation);
        var importButton = panel.down('[itemId="import_button"]');
        request.values = panel.command_params;
        paging.values = panel.command_params;
        me.down('command_livefilter').values = panel.command_params;
        paging.bindStore(me.store);
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                me.store.getProxy().setData(action.data);
                me.store.loadPage(action.request.page, {
                    start: 0
                });
                me.setLoading(false);
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
            if (action.data && action.data.status == 'importing') {
                panel.setLoading('Importing ...');
            } else {
                panel.setLoading(false);
            }
        });
        ws.stream(request.view).send(request);
    },

    onParseExperimentPreviewAfterRender: function ( me, eOpts ) {
        var panel = me.up('parse_experiment');
        var ws = command.current.ws;
        var operation = 'read_experiment';
        var request = me.getRequestObject(operation);
        var importButton = panel.down('[itemId="import_button"]');
        request.values = panel.command_params;
        panel.setLoading('Loading ...');
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            panel.setLoading(false);
            if (action.request.operation == request.operation) {
                panel.experiment_status = action.data.experiment.status.name;
                panel.experiment_access_id = action.data.experiment.experiment_access_id;
                panel.setTitle('Parse Experiment ' + action.data.experiment.experiment_access_id);
                me.setTitle('Preview of ' + action.data.experiment.experiment_access_id + ": " + action.data.experiment.experiment_name);
                me.down('#experiment_access_id').setValue(action.data.parsing_experiment.experiment_access_id);
                me.down('#experiment_name').setValue(action.data.parsing_experiment.experiment_name);
                me.down('#publications').setValue(action.data.parsing_experiment.scientific_paper_ref);
                me.down('#description').setValue(action.data.parsing_experiment.description);
                me.down('#experiment_n_samples').setValue(action.data.n_samples);
                me.down('#experiment_platforms').setValue(action.data.platforms);
                panel.down('platform_preview').show();
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
            if (action.data && action.data.status == 'importing') {
                panel.setLoading('Importing ...');
            } else {
                panel.setLoading(false);
            }
        });
        ws.stream(request.view).send(request);
    }
});