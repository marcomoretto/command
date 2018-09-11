Ext.define('command.view.data_collection.experiment.ExperimentsController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.experiments_controller',

    onNewExperimentPublicDB: function(b) {
        command.current.createWin({
            xtype: 'window_new_experiment',
            title: 'Download Experiment from Public DB',
            items:[{
                xtype: 'import_experiment_public'
            }]
        });
    },

    onNewExperimentLocalFiles: function(b) {
        command.current.createWin({
            xtype: 'window_new_experiment',
            title: 'New Experiment from Local Files',
            items:[{
                xtype: 'import_experiment_local'
            }]
        });
    },

    onExperimentDoubleClick: function(dv, record, item, index, e) {
        command.current.createWin({
            xtype: 'window_experiment_sample_details',
            title: 'Experiment samples details',
            items:[{
                xtype: 'view_experiment_sample_details',
                experiment: record.id
            }]
        });
    },

    onViewExperimentDetails: function (b) {
        var gridSelection = b.up('grid').getSelection();
        this.onExperimentDoubleClick(null, gridSelection[0], null, null, null);
    },

    onParseExperiment: function (b) {
        var main = Ext.ComponentQuery.query('#main_panel')[0];
        var gridSelection = b.up('grid').getSelection();
        gridSelection.forEach(function(e) {
            command.current.onShowPanel('parse_experiment', e.data.id);
        });
    },

    onDeleteDownloadedUploadedData: function(b) {
        var mainTab = Ext.ComponentQuery.query('#main_tab_panel')[0];
        var grid = b.up('grid');
        var gridSelection = grid.getSelection();
        var compendium_ids = [];
        gridSelection.forEach(function(e) {
            compendium_ids.push(e.data.id.toString());
        });
        Ext.MessageBox.show({
            title: 'Delete downloaded/uploaded files',
            msg: 'Are you sure you want to delete downloaded/uploaded this experiment?' +
            ' You will need to download/upload them again.',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_downloaded_uploaded_data');
                    request.values = JSON.stringify(compendium_ids);
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            if (command.current.checkHttpResponse(response)) {
                                command.current.showMessage('info', 'Files deleted', 'Experiment files successfully deleted!')
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

    onDeleteParsingData: function (b) {
        var mainTab = Ext.ComponentQuery.query('#main_tab_panel')[0];
        var grid = b.up('grid');
        var gridSelection = grid.getSelection();
        var compendium_ids = [];
        gridSelection.forEach(function(e) {
            compendium_ids.push(e.data.id.toString());
        });
        Ext.MessageBox.show({
            title: 'Delete parsing data',
            msg: 'Are you sure you want to delete the parsing data for this experiment?' +
            ' You will need to parse it again.',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_parsing_data');
                    request.values = JSON.stringify(compendium_ids);
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            if (command.current.checkHttpResponse(response)) {
                                mainTab.items.items.forEach(function (p) {
                                    var hasId = false;
                                    if (p.command_params) {
                                        hasId = compendium_ids.indexOf(p.command_params.toString()) != -1;
                                    }
                                    if (p.xtype == 'parse_experiment' && hasId) {
                                        command.current.showMessage('info', 'Parsing data deleted', 'Experiment parsing data successfully deleted!')
                                        p.close();
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

    onDeleteExperiment: function (b) {
        var mainTab = Ext.ComponentQuery.query('#main_tab_panel')[0];
        var grid = b.up('grid');
        var gridSelection = grid.getSelection();
        var compendium_ids = [];
        gridSelection.forEach(function(e) {
            compendium_ids.push(e.data.id.toString());
        });
        Ext.MessageBox.show({
            title: 'Delete experiment',
            msg: 'Are you sure you want to delete this experiment?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    var request = grid.getRequestObject('delete_experiment');
                    request.values = JSON.stringify(compendium_ids);
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                            mainTab.items.items.forEach(function (p) {
                                var hasId = false;
                                if (p.command_params) {
                                    hasId = compendium_ids.indexOf(p.command_params.toString()) != -1;
                                }
                                if (p.xtype == 'parse_experiment' && hasId) {
                                    p.close();
                                }
                            });
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