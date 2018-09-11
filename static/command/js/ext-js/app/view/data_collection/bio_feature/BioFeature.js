Ext.define('command.view.data_collection.bio_feature.BioFeature', {
    extend: 'command.Grid',

    xtype: 'bio_feature',

    title: 'Bio features',

    requires: [
        'Ext.panel.Panel',
        'Ext.toolbar.Paging',

        'command.view.data_collection.bio_feature.BioFeatureController',
        'command.view.data_collection.bio_feature.gene.ImportBioFeature'
    ],

    controller: 'bio_feature_controller',

    store: null,

    alias: 'widget.bio_feature',

    itemId: 'bio_feature',

    reference: 'bio_feature',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'bio_feature',

    command_read_operation: 'read_bio_feature',

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
            text: 'Import biological features'
        },
        iconCls: null,
        glyph: 'xf055',
        scale: 'medium',
        listeners: {
            click: 'onImportBiologicalFeatures'
        }
    }, {
        text: null,
        iconCls: null,
        tooltip: {
            text: 'Delete biological features'
        },
        glyph: 'xf014',
        scale: 'medium',
        listeners: {
            click: 'onDeleteBiologicalFeatures'
        }
        }
    ],
    
    listeners: {
        afterrender: 'onBioFeatureAfterRender'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.BioFeature');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});