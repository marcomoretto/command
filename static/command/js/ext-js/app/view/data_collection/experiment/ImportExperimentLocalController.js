Ext.define('command.view.data_collection.experiment.ImportExperimentLocalController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.import_experiment_local_controller',

    onExperimentIDChange: function (me, newValue, oldValue, eOpts) {
        var panel = me.findParentByType('[xtype="import_experiment_local"]');
        panel.down('#card-next').setDisabled(!newValue);
    },

    onExperimentDataChange: function (me, newValue, oldValue, eOpts) {
        var panel = me.findParentByType('[xtype="import_experiment_local"]');
        panel.down('#card-next').setVisible(!newValue);
        panel.down('#upload_experiment').setVisible(newValue);
    },

    onExperimentDataFileUpload: function(me, e, eOpts) {
        var panel = me.findParentByType('[xtype="import_experiment_local"]');
        var operation = 'upload_experiment_files';
        var request = panel.getRequestObject(operation);
        var form_panel = panel.down('#card-2');
        var form = form_panel.getForm();
        request.values = {
            experiment_id: panel.down('#card-0').down('textfield').getValue(),
            experiment_structure_file: panel.down('#card-1').down('filefield').getValue().replace(/^.*\\/, "")
        }
        if (form.isValid()) {
            form.submit({
                url: request.view + '/' + request.operation,
                waitMsg: null,
                params: {
                    request: JSON.stringify(request)
                },
                success: function (f, response) {
                    if (command.current.checkHttpResponse(response.response)) {
                        command.current.showMessage('info', 'Experiment uploaded', 'Experiment file will be decompressed (if necessary) in background!')
                        panel.findParentByType('[xtype="window_new_experiment"]').close();
                    }
                },
                failure: function (f, response) {
                    command.current.checkHttpResponse(response.response);
                }
            });
        }
    },

    onExperimentStructureFileChange: function (me, newValue, oldValue, eOpts) {
        var panel = me.findParentByType('[xtype="import_experiment_local"]');
        var operation = 'upload_experiment_structure_file';
        var request = panel.getRequestObject(operation);
        var form_panel = me.up('form');
        var form = form_panel.getForm();
        panel.down('#card-next').setDisabled(true);
        request.values = {
            experiment_id: panel.down('#card-0').down('textfield').getValue()
        }
        if (form.isValid()) {
            form.submit({
                url: request.view + '/' + request.operation,
                waitMsg: null,
                params: {
                    request: JSON.stringify(request)
                },
                success: function (f, response) {
                    if (command.current.checkHttpResponse(response.response)) {
                        command.current.showMessage('info', 'Valid file', 'The experiment structure file is a valid YAML file!')
                        panel.down('#card-next').setDisabled(!newValue);
                    }
                },
                failure: function (f, response) {
                    command.current.checkHttpResponse(response.response);
                }
            });
        }
    },

    showNext: function () {
        this.doCardNavigation(1);
        this.view.down('#card-next').setDisabled(true);
    },

    showPrevious: function (btn) {
        this.doCardNavigation(-1);
        this.view.down('#card-next').setVisible(true);
        this.view.down('#upload_experiment').setVisible(false);
    },

    doCardNavigation: function (incr) {
        var me = this.view;
        var l = me.getLayout();
        var i = l.activeItem.id.split('card-')[1];
        var next = parseInt(i, 10) + incr;
        l.setActiveItem(next);

        me.down('#card-prev').setDisabled(next===0);
        me.down('#card-next').setDisabled(next===me.items.length - 1);
    }

});