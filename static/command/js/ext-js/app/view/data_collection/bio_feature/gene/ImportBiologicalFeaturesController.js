Ext.define('command.view.data_collection.bio_feature.gene.BioFeatureController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.bio_feature_gene_controller',
    
    onFocusFileType: function (me) {
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        me.getStore().loadData(comp.bio_feature_file_types);
    },

    onBioFeatureFileChooserAfterRender: function (me) {
        //
    },

    onBioFeatureAfterRender: function (me) {
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        comp.bio_features_fields.forEach(function(e) {
            me.headerCt.insert(
              me.columns.length,
              Ext.create('Ext.grid.column.Column', {
                  text: e.description,
                  dataIndex: e.name,
                  flex: 2,
                  sortable: true,
                  hidden: false
              })
            );
        });

        me.getView().refresh();
    },
    
    onBioFeatureFileUpload: function(me, e, eOpts) {
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        var panel = me.findParentByType('[xtype="gene_bio_features_file_chooser"]');
        var win = panel.findParentByType('[xtype="window_import_gene_bio_features"]');
        var operation = 'upload_bio_feature_file';
        var request = panel.getRequestObject(operation);
        var form_panel = panel.down('form');
        var form = form_panel.getForm();
        request.bio_feature_name = comp.compendium_type.bio_feature_name;
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
    }
});