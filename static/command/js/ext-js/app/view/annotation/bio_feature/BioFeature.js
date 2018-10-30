Ext.define('command.view.annotation.bio_feature.FileChooser', {
    extend: 'Ext.panel.Panel',
    xtype: 'bio_feature_anno_file_chooser',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'bio_feature_anno_controller',

    alias: 'widget.bio_feature_anno_file_chooser',

    itemId: 'bio_feature_anno_file_chooser',

    layout: 'fit',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'bio_feature_anno',

    items: {
        xtype: 'form',

        items: [{
            xtype: 'form',
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            anchor: '100%',
            items: [{
                layout: 'hbox',
                anchor: '100%',
                items: [{
                    xtype: 'combo',
                    fieldLabel: 'Ontology',
                    labelWidth: 80,
                    margin: '10 10 10 5',
                    name: 'ontology',
                    itemId: 'ontology',
                    valueField: 'id',
                    displayField: 'name',
                    editable: false,
                    allowBlank: false,
                    autoSelect: true,
                    forceSelection: true,
                    queryMode: 'local',
                    flex: 2,
                    margin: '10 10 10 5',
                    store: Ext.create('command.store.Ontologies'),
                    listeners: {
                        focus: 'onFocusOntology'
                    }
                }, {
                    xtype: 'combo',
                    fieldLabel: 'File type',
                    labelWidth: 80,
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
                    margin: '10 10 10 5',
                    store: Ext.create('command.store.FileType'),
                    listeners: {
                        focus: 'onFocusFileType'
                    }
                }]
            }, {
                fieldLabel: 'File name',
                margin: '10 10 10 5',
                flex: 2,
                anchor: '100%',
                labelWidth: 80,
                xtype: 'filefield',
                name: 'file_name',
                itemId: 'file_name',
                reference: 'file_name',
                allowBlank: false
            }]
        }, {
            buttonAlign: 'right',
            margin: '10 10 10 5',
            buttons: [{
                xtype: 'button',
                text: 'Import annotation',
                formBind: true,
                listeners: {
                    click: 'onBioFeatureAnnotationFileUpload'
                }
            }]
        }]
    },

    listeners: {
        //afterrender: 'onBioFeatureFileChooserAfterRender'
    }
});

Ext.define('command.view.annotation.bio_feature.ImportBioFeatureAnnotation', {
    extend: 'Ext.window.Window',
    xtype: 'window_import_bio_feature_annotation',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'bio_feature_anno',

    //controller: '',

    bodyPadding: 10,
    title: 'Import annotation',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 600,
    height: 200,
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
            xtype: 'bio_feature_anno_file_chooser',
            border: false,
            layout: 'fit'
        }
    ]
});

Ext.define('command.view.annotation.bio_feature.BioFeatureAnnotation', {
    extend: 'command.Grid',

    xtype: 'bio_feature_anno',

    title: 'Bio feature annotation',

    requires: [
        'Ext.panel.Panel',
        'Ext.toolbar.Paging',

        'command.view.annotation.bio_feature.BioFeatureController'
    ],

    controller: 'bio_feature_anno_controller',

    store: null,

    alias: 'widget.bio_feature_anno',

    itemId: 'bio_feature_anno',

    reference: 'bio_feature_anno',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'bio_feature_anno',

    command_read_operation: 'read_bio_feature_anno',

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id',
        hidden: false
    }, {
        text: 'Name',
        flex: 2,
        sortable: true,
        dataIndex: 'name',
        hidden: false
    }, {
        text: 'Description',
        flex: 2,
        sortable: true,
        tdCls: 'command_tooltip',
        dataIndex: 'description'
    }],

    bbar: [{
        text: null,
        xtype: 'button',
        tooltip: {
            text: 'Import annotation'
        },
        iconCls: null,
        glyph: 'xf055',
        scale: 'medium',
        listeners: {
            click: 'onImportBiologicalFeatureAnnotation'
        }
    }, {
        text: null,
        iconCls: null,
        tooltip: {
            text: 'Delete annotation'
        },
        glyph: 'xf014',
        scale: 'medium',
        listeners: {
            click: 'onDeleteBiologicalFeatureAnnotation'
        }
        }
    ],

    plugins: [{
        ptype: 'rowwidget',
        widget: {
            xtype: 'grid',
            itemId: 'annotation_inner_grid',
            selModel: 'rowmodel',
            autoLoad: false,
            bind: {
                store: {
                    data: '{record.annotation}'
                },
                title: '{record.name} annotations'
            },
            listeners: {
                itemclick: 'onBioFeatureAnnotationItemClick'
            },
            columns: [{
                header: 'ID',
                dataIndex: 'id',
                flex: 1,
                hidden: true
            }, {
                header: 'Original ID',
                dataIndex: 'original_id',
                flex: 1
            }, {
                header: 'Ontology',
                dataIndex: 'ontology',
                flex: 1,
                renderer: function(value, metadata, record) {
                    return value.description;
                }
            }]
        }
    }],
    
    listeners: {

    },

    initComponent: function() {
        this.store = Ext.create('command.store.BioFeature');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.annotation.bio_feature.BioFeature', {
    extend: 'Ext.Container',

    xtype: 'bio_feature_annotation',

    title: 'Bio feature annotation',

    requires: [

    ],

    //controller: 'bio_feature_anno_controller',

    store: null,

    alias: 'widget.bio_feature_annotation',

    itemId: 'bio_feature_annotation',

    reference: 'bio_feature_annotation',

    viewModel: {},

    command_view: 'bio_feature_anno',

    //mixins: {
    //    getRequestObject: 'RequestMixin'
    //},

    layout: 'border',
    bodyBorder: false,

    defaults: {
        collapsible: true,
        split: true,
        bodyPadding: 10
    },

    items: [{
        xtype: 'bio_feature_anno',
        region:'center',
        flex: 5
    }, {
        xtype: 'panel',
        layout: 'fit',
        title: 'Annotation details',
        region: 'east',
        flex: 2,
        items: [{
            xtype: 'fieldset',
            title: 'Fields',
            layout: 'anchor',
            autoScroll: true,
            hidden: true,
            itemId: 'json_field_columns',
            items: [

            ]
        }]
    }],

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});