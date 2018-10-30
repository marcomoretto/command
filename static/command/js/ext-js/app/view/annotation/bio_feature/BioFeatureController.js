Ext.define('command.view.annotation.bio_feature.BioFeatureController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.bio_feature_anno_controller',

    onBioFeatureAnnotationItemClick: function(me, record, item, index, e, eOpts) {
        var panel = me.up('#bio_feature_annotation');
        var fields = panel.down('#json_field_columns');
        fields.setVisible(true);
        var values = null;
        fields.removeAll();
        record.data.columns.forEach(function (c) {
            var type = 'textfield';
            var value = record.data.fields[c.data_index];
            if (value && value.length > 30) {
                type = 'textarea';
            }
            fields.add(
                {
                    xtype: type,
                    editable: false,
                    fieldLabel: c.text,
                    name: c.data_index,
                    value: value,
                    anchor: '100%',
                    margin: '10 10 10 5',
                    grow: true,
                    growMax: 250,
                    allowBlank: true
                }
            )
        });
    },

    onBioFeatureAnnotationFileUpload: function(me) {
        console.log(me.id);
        var panel = me.up('#bio_feature_anno_file_chooser');
        var win = me.up('window_import_bio_feature_annotation');
        var operation = 'upload_bio_feature_annotation';
        var request = panel.getRequestObject(operation);
        var form = me.up('form');
        var fields = [];
        request.values = form.getValues();
        if (form.isValid()) {
            win.setLoading('Uploading');
            form.submit({
                url: request.view + '/' + request.operation,
                waitMsg: null,
                params: {
                    request: JSON.stringify(request)
                },
                success: function (f, response) {
                    win.setLoading(false);
                    if (command.current.checkHttpResponse(response.response)) {
                        command.current.showMessage('info', 'Gene file uploaded', 'File will now be parsed in background and data will appear in the grid once ready.')
                        win.close();
                    }
                },
                failure: function (f, response) {
                    win.setLoading(false);
                    command.current.checkHttpResponse(response.response);
                }
            });
        }
    },

    onFocusFileType: function(me, eOpts) {
        var panel = me.up('#bio_feature_anno_file_chooser');
        request = panel.getRequestObject('get_file_type');
        request.values = JSON.stringify({
            'destination': 'bio_feature'
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    me.store.loadData(resp.file_type, false);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onFocusOntology: function(me, eOpts) {
        var panel = me.up('#bio_feature_anno_file_chooser');
        request = panel.getRequestObject('get_ontologies');
        request.values = JSON.stringify({
            'destination': 'bio_feature'
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    me.store.loadData(resp.ontologies, false);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onImportBiologicalFeatureAnnotation: function (me) {
        command.current.createWin({
            xtype: 'window_import_bio_feature_annotation'
        });
    },

    onDeleteBiologicalFeatureAnnotation: function (me) {

    }


    /*
    onDeleteBiologicalFeatures: function (me) {
        var request = me.up('grid').getRequestObject('delete_bio_features');
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        Ext.MessageBox.show({
            title: 'Delete file',
            msg: 'Are you sure you want to delete all ' + comp.compendium_type.bio_feature_name +  '?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    })
                }
            }
        });
    },

    onImportBiologicalFeatures: function(me) {
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        switch (comp.compendium_type.bio_feature_name) {
            case 'gene':
                command.current.createWin({
                    xtype: 'window_import_gene_bio_features'
                });
                break
        }
    }*/
    
});