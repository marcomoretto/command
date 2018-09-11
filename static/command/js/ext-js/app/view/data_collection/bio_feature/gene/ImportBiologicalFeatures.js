Ext.define('command.view.data_collection.bio_feature.gene.FileChooser', {
    extend: 'Ext.panel.Panel',
    xtype: 'gene_bio_features_file_chooser',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'bio_feature_gene_controller',

    alias: 'widget.gene_bio_features_file_chooser',

    itemId: 'gene_bio_features_file_chooser',

    layout: 'fit',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'bio_feature_gene',

    items: {
        xtype: 'form',

        items: [{
            xtype: 'form',
            layout: 'hbox',
            anchor: '100%',
            items: [{
                xtype: 'combo',
                fieldLabel: 'Type',
                labelWidth: 50,
                name: 'file_type',
                itemId: 'file_type',
                valueField: 'file_type',
                displayField: 'file_type',
                editable: false,
                allowBlank: false,
                autoSelect: true,
                forceSelection: true,
                queryMode: 'local',
                flex: 1,
                margin: '0 20 0 0',
                store: Ext.create('command.store.FileType'),
                listeners: {
                    focus: 'onFocusFileType'
                }
            }, {
                fieldLabel: 'File name',
                flex: 3,
                labelWidth: 80,
                xtype: 'filefield',
                name: 'file_name',
                itemId: 'file_name',
                reference: 'file_name',
                allowBlank: false
            }]
        }, {
            buttonAlign: 'right',
            margin: '5 0 0 0',
            buttons: [{
                xtype: 'button',
                text: 'Import biological features',
                formBind: true,
                listeners: {
                    click: 'onBioFeatureFileUpload'
                }
            }]
        }]
    },
    
    listeners: {
        afterrender: 'onBioFeatureFileChooserAfterRender'
    }
});

Ext.define('command.view.data_collection.bio_feature.gene.ImportBioFeature', {
    extend: 'Ext.window.Window',
    xtype: 'window_import_gene_bio_features',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'bio_feature_gene',

    //controller: '',

    bodyPadding: 10,
    title: 'Import genes',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 600,
    height: 130,
    constrain: true,

    layout: 'border',
    bodyBorder: false,

    layout: {
        type: 'vbox',
        pack: 'start',
        align: 'stretch'
    },

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [
        {
            xtype: 'gene_bio_features_file_chooser',
            border: false,
            layout: 'fit'
        }
    ]
});