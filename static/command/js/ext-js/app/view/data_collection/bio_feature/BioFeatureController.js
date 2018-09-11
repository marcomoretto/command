Ext.define('command.view.data_collection.bio_feature.BioFeatureController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.bio_feature_controller',

    onBioFeatureAfterRender: function (me) {
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        me.setTitle(me.getTitle() + " (" + comp.compendium_type.bio_feature_name + ")");

        comp.bio_features_fields.forEach(function(e) {
            me.headerCt.insert(
              me.columns.length,
              Ext.create('Ext.grid.column.Column', {
                  text: e.description,
                  dataIndex: e.name,
                  flex: 2,
                  sortable: false,
                  hidden: false
              })
            );
        });

        me.getView().refresh();
    },

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
    }
    
});