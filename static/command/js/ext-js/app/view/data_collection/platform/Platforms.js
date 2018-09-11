Ext.define('command.view.data_collection.platform.RelatedPlatforms', {
    extend: 'command.Grid',

    xtype: 'related_platforms',

    title: 'Related platforms',

    requires: [
        'Ext.panel.Panel',
        'Ext.toolbar.Paging'
    ],

    controller: 'platforms_controller',

    store: null,

    alias: 'widget.related_platforms',

    itemId: 'related_platforms',

    reference: 'related_platforms',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'related_platforms',

    command_read_operation: 'read_related_platforms',

    columns: [{
        text: 'Original platform',
        flex: 2,
        sortable: true,
        dataIndex: 'original_platform',
        hidden: false,
        renderer: function(value, metadata, record) {
            if (record.data.original_platform_local) {
                return value;
            } else {
                return '<a href="' + record.data['original_platform_accession_base_link'] + value + '" target="_blank">' + value + '</a>';
            }
        }
    }, {
        text: 'Reporter platform',
        flex: 2,
        sortable: true,
        dataIndex: 'reporter_platform',
        hidden: false,
        renderer: function(value, metadata, record) {
            if (record.data.reporter_platform_local) {
                return value;
            } else {
                return '<a href="' + record.data['reporter_platform_accession_base_link'] + value + '" target="_blank">' + value + '</a>';
            }
        }
    }, {
        text: 'Experiments',
        flex: 4,
        sortable: true,
        dataIndex: 'experiments',
        hidden: false,
        renderer: function(value, metadata, record) {
            console.log(value);
            console.log(record);
            var str = [];
            value.forEach(function (v, i) {
                str.push('<a href="' + record.data.experiment_accession_base_links[i] + v + '" target="_blank">' + v + '</a>')
            });
            return str.join(', ');
        }
    }],

    listeners: {
        //afterrender: 'onPlatformAfterRender',
    },
    
    initComponent: function() {
        this.store = Ext.create('command.store.RelatedPlatforms');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.platform.Platforms', {
    extend: 'command.Grid',

    xtype: 'platforms',

    title: 'Platforms',

    requires: [
        'Ext.panel.Panel',
        'Ext.toolbar.Paging'
    ],

    controller: 'platforms_controller',

    store: null,

    alias: 'widget.platforms',

    itemId: 'platforms',

    reference: 'platforms',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'platforms',

    command_read_operation: 'read_platforms',

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id',
        hidden: false
    }, {
        text: 'Accession',
        flex: 2,
        sortable: true,
        dataIndex: 'platform_access_id',
        renderer: function(value, metadata, record) {
            if (record.data.data_source.is_local) {
                return value;
            } else {
                return '<a href="' + record.data['platform_accession_base_link'] + value + '" target="_blank">' + value + '</a>';
            }
        }
    }, {
        text: 'Name',
        flex: 2,
        sortable: true,
        dataIndex: 'platform_name',
        hidden: false
    }, {
        text: 'Source',
        flex: 1,
        sortable: true,
        dataIndex: 'data_source',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            return value.source_name;
        }
    }, {
        text: 'Type',
        flex: 2,
        sortable: true,
        dataIndex: 'platform_type',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            if (value)
                return value.description;
        }
    }, {
        text: 'Description',
        flex: 2,
        sortable: true,
        tdCls: 'command_tooltip',
        dataIndex: 'description'
    }],

    bbar: [
        {
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'Map platform to biological features'
            },
            iconCls: null,
            glyph: 'f0c1',
            scale: 'medium',
            listeners: {
                click: 'onMapPlatformToBioFeature'
            },
            bind: {
                disabled: '{!platforms.selection}'
            }
        }, {
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'View platform feature reporter'
            },
            iconCls: null,
            glyph: 'f06e',
            scale: 'medium',
            listeners: {
                click: 'onViewBioFeatureReporter'
            },
            bind: {
                disabled: '{!platforms.selection}'
            }
        }, {
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'Delete platform'
            },
            iconCls: null,
            glyph: 'xf014',
            scale: 'medium',
            listeners: {
                click: 'onDeletePlatform'
            },
            bind: {
                disabled: '{!platforms.selection}'
            }
        }
    ],

    listeners: {
        afterrender: 'onPlatformAfterRender',
        itemdblclick: 'onViewBioFeatureReporter'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.Platforms');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.platform.PlatformManager', {
    extend: 'Ext.panel.Panel',
    title: 'Platforms',

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'platforms_controller',

    alias: 'widget.platform_manager',

    layout: 'accordion',

    items: [{
        xtype: 'platforms',
        border: false,
        layout: 'fit'
    }, {
        xtype: 'related_platforms',
        border: false,
        layout: 'fit'
    }]
});