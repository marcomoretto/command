Ext.define('command.view.normalization.norm_manager.NormalizationDesignGroup.Cy', {
    extend: 'Ext.Component',

    xtype: 'cy_design',

    alias: 'widget.cy_design',

    itemId: 'cy_design',

    reference: 'cy_design',

    controller: 'normalization_experiment_controller',

    listeners: {
        afterrender: 'cyDesignAfterRender'
    },

    cy: null,

    autoEl: {
        tag: 'div',
        cls: 'cy'
    },

    layout: 'fit',

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.normalization.norm_manager.NormalizationDesignGroup', {
    extend: 'command.Grid',

    xtype: 'normalization_design_group',

    title: 'Sample groups',

    requires: [
        'Ext.panel.Panel',
        'Ext.toolbar.Paging'
    ],

    controller: 'normalization_experiment_controller',

    store: null,

    alias: 'widget.normalization_design_group',

    itemId: 'normalization_design_group',

    reference: 'normalization_design_group',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'normalization_experiment',

    command_read_operation: 'read_normalization_design_group',

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
    }],

    bbar: [{
        text: null,
        xtype: 'button',
        tooltip: {
            text: 'Update group'
        },
        iconCls: null,
        glyph: 'xf044',
        scale: 'medium',
        listeners: {
            click: 'onUpdateNormalizationDesignGroup'
        },
        bind: {
            disabled: '{!normalization_design_group.selection}'
        }
    }, {
        text: null,
        iconCls: null,
        tooltip: {
            text: 'Delete group'
        },
        glyph: 'xf014',
        scale: 'medium',
        listeners: {
            click: 'onDeleteNormalizationDesignGroup'
        },
        bind: {
            disabled: '{!normalization_design_group.selection}'
        }
    }],

    plugins: [{
        ptype: 'rowwidget',
        widget: {
            xtype: 'grid',
            itemId: 'samples_inner_grid',
            selModel: 'rowmodel',
            autoLoad: false,
            bind: {
                store: {
                    data: '{record.samples}'
                },
                title: '{record.name} samples'
            },
            listeners: {

            },
            columns: [{
                header: 'ID',
                dataIndex: 'id',
                flex: 1
            }, {
                header: 'Name',
                dataIndex: 'sample_name',
                flex: 2
            }, {
                header: 'Description',
                dataIndex: 'description',
                flex: 3
            }, {
                text: 'Remove sample',
                flex: 1,
                align: 'center',
                xtype: 'actioncolumn',
                items: [{
                    xtype: 'button',
                    itemId: 'remove_sample_button',
                    text: null,
                    iconCls: 'dimgrayIcon',
                    scale: 'medium',
                    glyph: 'xf014',
                    handler: 'onRemoveSample'
                }]
            }]
        }
    }],

    listeners: {
        afterrender: 'onNormalizationDesignGroupAfterRender',
        itemclick: 'onNormalizationDesignGroupItemClick'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.NormalizationDesignGroup');
        this.callParent();
        this.events.afterrender.removeListener(this.events.afterrender.listeners[0], 'self', 0); // remove default event listener
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.normalization.norm_manager.NormalizationExperimentDesign', {
    extend: 'Ext.Container',

    xtype: 'normalization_experiment_design',

    title: 'Experimental design',

    controller: 'normalization_experiment_controller',

    store: null,

    alias: 'widget.normalization_experiment_design',

    itemId: 'normalization_experiment_design',

    reference: 'normalization_experiment_design',

    viewModel: {},

    command_view: 'normalization_experiment',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'border',

    bodyBorder: false,

    defaults: {
        collapsible: true,
        split: true,
        frame: false,
        margin: '5 5 5 0'
    },

    items: [
        {
            xtype: 'panel',
            title: 'Samples',
            layout: 'border',
            region: 'west',
            flex: 1,
            bodyBorder: false,
            defaults: {
                collapsible: true,
                split: true
            },
            items: [{
                xtype: 'panel',
                itemId: 'sample_panel',
                title: null,
                region: 'center',
                layout: 'fit',
                flex: 1
            }, {
                xtype: 'normalization_design_group',
                region: 'south',
                flex: 1
            }]
        },{
            xtype: 'panel',
            region: 'center',
            layout: 'border',
            title: 'Design',
            flex: 1,
            bodyBorder: false,
            defaults: {
                collapsible: true,
                split: true
            },
            bbar: [{
                text: null,
                xtype: 'button',
                tooltip: {
                    text: 'New condition (group samples)'
                },
                iconCls: null,
                glyph: 'f247',
                scale: 'medium',
                listeners: {
                    click: 'onNewCondition'
                }
            }, {
                text: null,
                iconCls: null,
                tooltip: {
                    text: 'Delete condition (ungroup samples)'
                },
                glyph: 'f248',
                scale: 'medium',
                listeners: {
                    click: 'onDeleteCondition'
                }
            }, {
                text: null,
                iconCls: null,
                tooltip: {
                    text: 'Link conditions'
                },
                glyph: 'f0c1',
                scale: 'medium',
                listeners: {
                    //click: 'onDeleteBiologicalFeatureAnnotation'
                }
            }, {
                text: null,
                iconCls: null,
                tooltip: {
                    text: 'Unlink conditions'
                },
                glyph: 'f127',
                scale: 'medium',
                listeners: {
                    //click: 'onDeleteBiologicalFeatureAnnotation'
                }
            }],
            items: [{
                xtype: 'cy_design',
                region: 'center',
                flex: 1
            }]
        }],

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.normalization.norm_manager.NormalizationExperiment', {
    extend: 'Ext.tab.Panel',
    xtype: 'normalization_experiment',
    title: 'Normalize experiment',

    requires: [
        'Ext.tab.Tab'
    ],

    controller: 'normalization_experiment_controller',

    alias: 'widget.normalization_experiment',

    itemId: 'normalization_experiment',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    command_view: 'normalization_experiment',

    bodyBorder: false,

    defaults: {
        collapsible: true,
        split: true,
        bodyPadding: 10
    },

    margin: '10 10 10 5',

    items: [{
        xtype: 'normalization_experiment_design'
    }, {
        xtype: 'panel',
        title: 'Normalization'
    }],

    listeners: {
        afterrender: 'onNormalizationExperimentAfterRender'
    },

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});