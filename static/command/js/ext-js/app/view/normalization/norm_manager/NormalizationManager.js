Ext.define('command.view.normalization.norm_manager.AddExperiment', {
    extend: 'Ext.window.Window',
    xtype: 'window_add_experiment',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    bodyPadding: 10,
    title: 'Add experiment',
    closable: true,
    autoShow: true,
    modal: true,
    width: 400,
    height: 150,
    constrain: true,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [
        {
            xtype: 'add_experiment_panel'
        }
    ]
});

Ext.define('command.view.normalization.norm_manager.AddExperimentPanel', {
    extend: 'Ext.panel.Panel',
    xtype: 'add_experiment_panel',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'normalization_manager_controller',

    alias: 'widget.add_experiment_panel',

    itemId: 'add_experiment_panel',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    command_view: 'win_normalization_manager',

    items: [{
        xtype: 'form',
        itemId: 'experiment_form',
        items: [{
            xtype: 'combobox',
            fieldLabel: 'Accession',
            displayField: 'experiment_access_id',
            valueField: 'id',
            anchor: '100%',
            margin: '10 10 10 5',
            queryMode: 'local',
            typeAhead: true,
            allowBlank: true,
            editable: true,
            lastQuery: '',
            name: 'experiment',
            itemId: 'experiment',
            store: Ext.create('command.store.OntologyNodes'),
            listeners: {
                buffer: 50,
                afterrender: 'AddExperimentAfterRender',
                change: 'onChangeAddExperiment'
            }
        }, {
            buttonAlign: 'right',
            margin: '5 0 0 0',
            buttons: [{
                xtype: 'button',
                itemId: 'add_experiment_button',
                text: 'Add experiment',
                formBind: true,
                listeners: {
                    click: 'onAddSingleExperiment'
                }
            }]
        }]
    }]
});

Ext.define('command.view.normalization.norm_manager.NewNormalization', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_normalization',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    bodyPadding: 10,
    title: 'New normalization',
    closable: true,
    autoShow: true,
    modal: true,
    width: 400,
    height: 250,
    constrain: true,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [
        {
            xtype: 'new_normalization_panel'
        }
    ]
});

Ext.define('command.view.normalization.norm_manager.NewNormalizationPanel', {
    extend: 'Ext.panel.Panel',
    xtype: 'new_normalization_panel',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'normalization_manager_controller',

    alias: 'widget.new_normalization_panel',

    itemId: 'new_normalization_panel',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    command_view: 'normalization_manager',

    items: [{
        xtype: 'form',
        itemId: 'ontology_form',
        items: [{
            xtype: 'textfield',
            anchor: '100%',
            margin: '10 10 10 5',
            allowBlank: false,
            fieldLabel: 'Name',
            name: 'name',
            emptyText: 'New normalization'
        }, {
            xtype: 'textfield',
            anchor: '100%',
            margin: '10 10 10 5',
            allowBlank: true,
            fieldLabel: 'Version',
            name: 'version',
            emptyText: '1.0'
        }, {
            xtype: 'checkboxfield',
            anchor: '100%',
            margin: '10 10 10 5',
            fieldLabel  : 'Public',
            name      : 'is_public',
            inputValue: '1',
            id        : 'is_public',
            checked: true
        }, {
            xtype: 'combo',
            fieldLabel: 'Type',
            name: 'normalization_type',
            itemId: 'normalization_type',
            valueField: 'id',
            displayField: 'name',
            editable: false,
            allowBlank: false,
            autoSelect: true,
            forceSelection: true,
            queryMode: 'local',
            anchor: '100%',
            margin: '10 10 10 5',
            store: Ext.create('command.store.NormalizationType'),
            listeners: {
                focus: 'onFocusNormalizationType'
            }
        }, {
            buttonAlign: 'right',
            margin: '5 0 0 0',
            buttons: [{
                xtype: 'button',
                itemId: 'create_normalization_button',
                text: 'Create normalization',
                formBind: true,
                listeners: {
                    click: 'onCreateNormalization'
                }
            }]
        }]
    }]
});

Ext.define('command.view.normalization.norm_manager.NormalizationExperimentList', {
    extend: 'command.Grid',
    xtype: 'normalization_experiment_list',
    title: 'Experiments for normalization',

    requires: [
        'Ext.panel.Panel'
    ],

    alias: 'widget.normalization_list',

    itemId: 'normalization_experiment_list',

    reference: 'normalization_experiment_list',

    controller: 'normalization_manager_controller',

    viewModel: {},

    store: null,

    command_view: 'normalization_manager',

    command_read_operation: 'read_normalization_experiments',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Accession',
        flex: 2,
        sortable: true,
        dataIndex: 'experiment_access_id',
        renderer: function(value, metadata, record) {
            return record.data.experiment.experiment_access_id;
        }
    }, {
        text: 'Experiment name',
        flex: 2,
        sortable: true,
        dataIndex: 'name',
        renderer: function(value, metadata, record) {
            return record.data.experiment.experiment_name;
        }
    }, {
        text: 'Status',
        flex: 1,
        sortable: true,
        dataIndex: 'public',
        xtype: 'actioncolumn',
        iconCls: 'dimgrayIcon',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            command.current.getExperimentGlyph(this, record.data.experiment.status.name, record.data.experiment.status.description);
        }
    }, {
        xtype: 'checkcolumn',
        text: 'Use experiment',
        flex: 1,
        sortable: true,
        dataIndex: 'use_experiment',
        listeners: {
            checkchange: 'onUseExperimentCheckChange'
        }
    }],

    bbar: [{
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'Add experiment'
            },
            itemId: 'add_experiment_button',
            iconCls: null,
            disabled: true,
            glyph: 'xf055',
            scale: 'medium',
            menu: {
                xtype: 'menu',
                forceLayout: true,
                items: [{
                    text: 'Add single experiment',
                    scale: 'medium',
                    tooltip: {
                        text: 'Add single experiment'
                    },
                    glyph: 'xf0c3',
                    listeners: {
                        click: 'onAddExperiment'
                    }
                }, {
                    text: 'Add all experiments',
                    scale: 'medium',
                    tooltip: {
                        text: 'Add all experiments'
                    },
                    glyph: 'xf00a',
                    listeners: {
                        click: 'onAddAllExperiments'
                    }
                }]
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Remove experiment'
            },
            glyph: 'xf056',
            disabled: true,
            itemId: 'remove_experiment_button',
            scale: 'medium',
            menu: {
                xtype: 'menu',
                forceLayout: true,
                items: [{
                    text: 'Remove selected experiment',
                    scale: 'medium',
                    tooltip: {
                        text: 'Remove selected experiment'
                    },
                    bind: {
                        disabled: '{!normalization_experiment_list.selection}'
                    },
                    glyph: 'xf0c3',
                    listeners: {
                        click: 'onRemoveSelectedExperiment'
                    }
                }, {
                    text: 'Remove all experiments',
                    scale: 'medium',
                    tooltip: {
                        text: 'Remove all experiments'
                    },
                    glyph: 'xf00a',
                    listeners: {
                        click: 'onRemoveAllExperiments'
                    }
                }]
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Normalize experiment'
            },
            glyph: 'f080',
            scale: 'medium',
            listeners: {
                click: 'onNormalizeExperiment'
            },
            bind: {
                disabled: '{!normalization_experiment_list.selection}'
            }
        }
    ],

    listeners: {

    },

    initComponent: function() {
        this.store = Ext.create('command.store.NormalizationExperiments');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.normalization.norm_manager.NormalizationList', {
    extend: 'command.Grid',
    xtype: 'normalization_list',
    title: 'Normalizations',

    requires: [
        'Ext.panel.Panel'
    ],

    alias: 'widget.normalization_list',

    itemId: 'normalization_list',

    reference: 'normalization_list',

    controller: 'normalization_manager_controller',

    viewModel: {},

    store: null,

    command_view: 'normalization',

    command_read_operation: 'read_normalizations',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Name',
        flex: 1,
        sortable: true,
        dataIndex: 'name'
    }, {
        text: 'Date',
        flex: 1,
        sortable: true,
        dataIndex: 'date'
    }, {
        text: 'Type',
        flex: 1,
        sortable: true,
        dataIndex: 'normalization_type',
        renderer: function(value, metadata, record) {
            return value.name;
        }
    }, {
        text: 'Version',
        flex: 1,
        sortable: true,
        dataIndex: 'version'
    }, {
        text: 'N° Exp',
        flex: 1,
        sortable: true,
        dataIndex: 'n_exp'
    }, {
        text: 'Public',
        flex: 1,
        sortable: true,
        dataIndex: 'is_public',
        renderer: function(value, metadata, record) {
            if (value) {
                return 'Yes';
            }
            return 'No';
        }
    }],

    bbar: [{
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'New normalization'
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            listeners: {
                click: 'onNewNormalization'
            }
        },{
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Update normalization'
            },
            glyph: 'xf044',
            scale: 'medium',
            listeners: {
                //click: 'onUpdateOntology'
            },
            bind: {
                disabled: '{!normalization_list.selection}'
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Delete normalization'
            },
            glyph: 'xf056',
            scale: 'medium',
            listeners: {
                //click: 'onDeleteOntology'
            },
            bind: {
                disabled: '{!normalization_list.selection}'
            }
        }
    ],

    listeners: {
        itemclick: 'onSelectNormalization'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.Normalizations');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.normalization.norm_manager.NormalizationManager', {
    extend: 'Ext.panel.Panel',
    xtype: 'normalization_manager',
    title: 'Normalization manager',

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'normalization_manager_controller',

    alias: 'widget.normalization_manager',

    itemId: 'normalization_manager',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    command_view: 'normalization_manager',

    layout: 'border',
    bodyBorder: false,

    defaults: {
        collapsible: true,
        split: true,
        bodyPadding: 10
    },

    items: [{
        xtype: 'normalization_list',
        region:'center',
        flex: 1
    }, {
        xtype: 'normalization_experiment_list',
        region:'south',
        flex: 1
    }],

    listeners: {

    },

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});