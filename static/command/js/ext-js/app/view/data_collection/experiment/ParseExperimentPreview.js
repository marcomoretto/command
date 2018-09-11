Ext.define('command.view.data_collection.experiment.PlatformPreview', {
    extend: 'command.Grid',
    xtype: 'platform_preview',
    title: 'Platforms',

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.platform_preview',

    itemId: 'platform_preview',

    reference: 'platform_preview',

    viewModel: {},

    command_view: 'parse_experiment_platform',

    command_read_operation: 'read_platform_preview',

    controller: 'parse_experiment_preview_controller',

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Access ID',
        flex: 2,
        sortable: true,
        dataIndex: 'platform_access_id'
    }, {
        text: 'Name',
        flex: 2,
        sortable: true,
        dataIndex: 'platform_name'
    }, {
        text: 'Type',
        flex: 2,
        sortable: true,
        dataIndex: 'platform_type'
    },{
        text: 'Description',
        flex: 5,
        sortable: true,
        dataIndex: 'description'
    }],

    listeners: {
        afterrender: 'onPlatformPreviewAfterRender',
        itemdblclick: 'onPlatformPreviewDoubleClick'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.ExperimentPlatformsFiles');
        this.events.afterrender.removeListener(this.events.afterrender.listeners[0], 'self', 0); // remove default event listener
        this.events.beforeshow.removeListener(this.events.beforeshow.listeners[0], 'self', 0); // remove default event listener
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.experiment.SamplePreview', {
    extend: 'command.Grid',
    xtype: 'sample_preview',
    title: 'Samples',

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.sample_preview',

    itemId: 'sample_preview',

    reference: 'sample_preview',

    viewModel: {},

    command_view: 'parse_experiment',

    command_read_operation: 'read_sample_preview',

    controller: 'parse_experiment_preview_controller',

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Name',
        flex: 2,
        sortable: true,
        dataIndex: 'sample_name'
    }, {
        text: 'Platform',
        flex: 2,
        sortable: true,
        dataIndex: 'platform',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            return record.data.platform.platform_access_id;
        }
    }, {
        text: 'Reporter platform',
        flex: 2,
        sortable: true,
        dataIndex: 'reporter_platform',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            return record.data.reporter_platform.platform_access_id;
        }
    }, {
        text: 'Description',
        flex: 5,
        sortable: true,
        dataIndex: 'description'
    }],

    listeners: {
        afterrender: 'onSamplePreviewAfterRender',
        itemdblclick: 'onSamplePreviewDoubleClick'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.ExperimentSamplesFiles');
        this.events.afterrender.removeListener(this.events.afterrender.listeners[0], 'self', 0); // remove default event listener
        this.events.beforeshow.removeListener(this.events.beforeshow.listeners[0], 'self', 0); // remove default event listener
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.experiment.ExperimentPreview', {
    extend: 'Ext.tab.Panel',

    plain: false,

    defaults: {
        bodyPadding: 5,
        scrollable: true,
        border: false
    },

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    xtype: 'experiment_preview',

    itemId: 'experiment_preview',

    title: null,

    border: false,

    viewModel: {},

    command_view: 'parse_experiment',

    command_read_operation: 'read_experiment',
    
    controller: 'parse_experiment_preview_controller',

    items: [
        {
            xtype: 'panel',
            title: 'Experiment',
            flex: 1,
            layout: 'anchor',
            items: [
                {
                    xtype: 'displayfield',
                    name: 'experiment_access_id',
                    itemId: 'experiment_access_id',
                    fieldLabel: 'Access ID',
                    labelStyle : 'font-weight: bold;',
                    border: 0,
                    anchor: '95%',
                    margin: '10 0 0 5'
                },
                {
                    xtype: 'displayfield',
                    name: 'experiment_name',
                    itemId: 'experiment_name',
                    fieldLabel: 'Name',
                    labelStyle : 'font-weight: bold;',
                    anchor: '95%',
                    margin: '10 0 0 5'
                },
                {
                    xtype: 'displayfield',
                    name: 'publications',
                    itemId: 'publications',
                    fieldLabel: 'Publications',
                    labelStyle : 'font-weight: bold;',
                    anchor: '95%',
                    margin: '10 0 0 5',
                    autoEl: {
                        tag: 'a',
                        href: '#',
                        target:'_blank'
                    },
                    listeners: {
                        afterrender: function(view) {
                            view.getEl().on('click', function() {
                                window.open(view.value);
                            })
                        }
                    }
                },
                {
                    xtype: 'displayfield',
                    name: 'experiment_platforms',
                    itemId: 'experiment_platforms',
                    fieldLabel: 'Platforms',
                    labelStyle : 'font-weight: bold;',
                    anchor: '95%',
                    margin: '10 0 0 5'
                },
                {
                    xtype: 'displayfield',
                    name: 'experiment_n_samples',
                    itemId: 'experiment_n_samples',
                    fieldLabel: 'N° of samples',
                    labelStyle : 'font-weight: bold;',
                    anchor: '95%',
                    margin: '10 0 0 5'
                },
                {
                    xtype: 'displayfield',
                    name: 'description',
                    itemId: 'description',
                    fieldLabel: 'Description',
                    labelStyle : 'font-weight: bold;',
                    anchor: '95%',
                    margin: '10 0 0 5'
                }
            ]
        }, {
            xtype: 'platform_preview',
            flex: 1,
            layout: 'fit'
        }, {
            xtype: 'sample_preview',
            flex: 1,
            layout: 'fit'
        }
    ],

    bbar: ['->', {
        xtype: 'button',
        text: null,
        iconCls: null,
        scale: 'medium',
        tooltip: {
            text: 'Import'
        },
        itemId: 'import_button',
        name: 'import_button',
        glyph: 'f063',
        menu: {
            xtype: 'menu',
            forceLayout: true,
            items: [{
                text: 'Import whole experiment',
                scale: 'medium',
                tooltip: {
                    text: 'Import whole experiment'
                },
                glyph: 'f0c3',
                listeners: {
                    click: 'onImportExperiment'
                }
            }, {
                text: 'Import platform only',
                itemId: 'import_platform_only_menu_item',
                scale: 'medium',
                tooltip: {
                    text: 'Import platform only'
                },
                glyph: 'f21a',
                listeners: {
                    click: 'onImportExperimentPlatform'
                }
            }]
        }
    }],

    listeners: {
        expand: function (p, eOpts ) {
            // Hack to prevent store to crash when reloaded without having focus
            p.down('sample_preview').view.refresh();
            p.down('platform_preview').view.refresh();
        },
        afterrender: 'onParseExperimentPreviewAfterRender',
        beforeshow: function ( me, eOpts ) {
            //
        }
    }

});