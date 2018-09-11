Ext.define('command.view.data_collection.platform.microarray.MappingParameters', {
    extend: 'Ext.panel.Panel',
    xtype: 'map_platform_parameters',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.map_platform_parameters',

    itemId: 'map_platform_parameters',

    reference: 'map_platform_parameters',

    viewModel: {},

    command_view: 'microarray_platforms',

    command_read_operation: '',

    controller: 'map_platform_controller',

    items: [{
        xtype: 'fieldset',
        title: 'BLAST parameters',
        collapsible: false,
        defaults: {
            labelWidth: 150,
            anchor: '100%',
            layout: 'hbox',
            margin: '5 0 0 0'
        },
        items: [{
            xtype: 'form',
            itemId: 'alignment_form',
            items: [{
                fieldLabel: 'Alignment identity (%)',
                labelWidth: 150,
                xtype: 'numberfield',
                name: 'alignment_identity',
                itemId: 'alignment_identity',
                reference: 'alignment_identity',
                allowBlank: false,
                margin: '0 5 0 0',
                minValue: 0,
                value: 98,
                flex: 3
            }, {
                xtype: 'checkboxfield',
                name: 'use_short_blastn',
                inputValue: '1',
                checked: true,
                boxLabel: 'Use short-blastn',
                margin: '0 5 0 15',
                flex: 1
            },{
                xtype: 'button',
                text: 'Run alignment',
                margin: '0 5 0 0',
                flex: 1,
                formBind: true,
                listeners: {
                    click: 'onRunAlignment'
                }
            }]
        }
    ]}, {
        xtype: 'panel',
        title: null,
        border: 0,
        collapsible: false,
        defaults: {
            labelWidth: 150,
            anchor: '100%',
            layout: 'hbox',
            margin: '0 0 0 0'
        },
        items: [{
            xtype: 'form',
            itemId: 'filter_form',
            items: [{
                xtype: 'fieldset',
                title: 'Filtering: first step (sensitivity)',
                collapsible: false,
                flex: 1,
                defaults: {
                    labelWidth: 150,
                    anchor: '100%',
                    layout: 'vbox',
                    margin: '5 0 0 0'
                },
                items: [{
                    fieldLabel: 'Alignment length (%)',
                    labelWidth: 150,
                    xtype: 'numberfield',
                    name: 'alignment_length_1',
                    itemId: 'alignment_length_1',
                    reference: 'alignment_length_1',
                    allowBlank: false,
                    minValue: 0,
                    value: 90
                }, {
                    fieldLabel: 'Gap open',
                    labelWidth: 150,
                    xtype: 'numberfield',
                    name: 'gap_open_1',
                    itemId: 'gap_open_1',
                    reference: 'gap_open_1',
                    allowBlank: false,
                    minValue: 0,
                    value: 0
                }, {
                    fieldLabel: 'Mismatches',
                    labelWidth: 150,
                    xtype: 'numberfield',
                    name: 'mismatches_1',
                    itemId: 'mismatches_1',
                    reference: 'mismatches_1',
                    allowBlank: false,
                    minValue: 0,
                    value: 0
                }
                ]
            }, {
                xtype: 'fieldset',
                title: 'Filtering: second step (specificity)',
                collapsible: false,
                flex: 1,
                defaults: {
                    labelWidth: 150,
                    anchor: '100%',
                    layout: 'hbox'
                },
                items: [{
                    fieldLabel: 'Alignment length (%)',
                    labelWidth: 150,
                    xtype: 'numberfield',
                    name: 'alignment_length_2',
                    itemId: 'alignment_length_2',
                    reference: 'alignment_length_2',
                    allowBlank: false,
                    minValue: 0,
                    value: 90
                }, {
                    fieldLabel: 'Gap open',
                    labelWidth: 150,
                    xtype: 'numberfield',
                    name: 'gap_open_2',
                    itemId: 'gap_open_2',
                    reference: 'gap_open_2',
                    allowBlank: false,
                    minValue: 0,
                    value: 0
                }, {
                    fieldLabel: 'Mismatches',
                    labelWidth: 150,
                    xtype: 'numberfield',
                    name: 'mismatches_2',
                    itemId: 'mismatches_2',
                    reference: 'mismatches_2',
                    allowBlank: false,
                    minValue: 0,
                    value: 0
                }
                ]
            }

            ]
        }
    ]}
    ]
});

Ext.define('command.view.data_collection.platform.microarray.MappingResults', {
    extend: 'command.Grid',
    xtype: 'map_platform_results',
    title: 'Mapping results',

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.map_platform_results',

    itemId: 'map_platform_results',

    reference: 'map_platform_results',

    viewModel: {},

    command_view: 'microarray_platforms',

    command_read_operation: 'microarray_read_mapping',

    controller: 'map_platform_controller',
    
    columns: [{
        text: 'ID',
        flex: 2,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Date',
        flex: 2,
        sortable: true,
        dataIndex: 'date'
    }, {
        text: 'Total aligned',
        flex: 1,
        sortable: true,
        dataIndex: 'total_aligned'
    }, {
        text: 'Status',
        flex: 1,
        xtype: 'actioncolumn',
        dataIndex: 'status',
        align: 'center',
        iconCls: 'dimgrayIcon',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            switch (record.data.status) {
                case 'ready':
                    this.items[0].glyph = command.current.entity_script_status_glyph['alt_ready'];
                    this.items[0].tooltip = 'ready';
                    break;
                case 'running':
                    this.items[0].glyph = command.current.entity_script_status_glyph['running'];
                    this.items[0].tooltip = 'running';
                    break;
                case 'error':
                    this.items[0].glyph = command.current.entity_script_status_glyph['error'];
                    this.items[0].tooltip = 'error';
                    break;
            }
        }
    }, {
        text: 'Run filtering',
        flex: 1,
        align: 'center',
        xtype: 'actioncolumn',
        items: [{
            xtype: 'button',
            itemId: 'run_filtering_button',
            text: null,
            iconCls: 'dimgrayIcon',
            scale: 'medium',
            glyph: 'xf144',
            handler: 'onRunFilterAlignment',
            isDisabled: function( view, rowIndex, colIndex, item, record ) {
                return record.data.status == 'running';
            }
        }]
    }, {
        text: 'Remove alignment',
        flex: 1,
        align: 'center',
        xtype: 'actioncolumn',
        items: [{
            xtype: 'button',
            itemId: 'remove_alignment_button',
            text: null,
            iconCls: 'dimgrayIcon',
            scale: 'medium',
            glyph: 'xf014',
            handler: 'onRemoveAlignment',
            isDisabled: function( view, rowIndex, colIndex, item, record ) {
                return record.data.status == 'running';
            }
        }]
    }],

    plugins: [{
        ptype: 'rowwidget',
        widget: {
            xtype: 'grid',
            selModel: 'rowmodel',
            autoLoad: false,
            bind: {
                store: {
                    data: '{record.parsing_details}'
                },
                title: 'Filtering results for alignment {record.id}'
            },
            listeners: {
                cellClick: 'onCellClickFilter'
            },
            columns: [{
                header: 'ALIGNMENT_ID',
                dataIndex: 'alignment_id',
                flex: 1,
                hidden: true
            }, {
                header: 'ID',
                dataIndex: 'id',
                flex: 1,
                hidden: true
            }, {
                header: 'Non-unique PASS sensitivity',
                dataIndex: 'non_unique_pass_sensitivity',
                flex: 1
            }, {
                header: 'Unique REJECT sensitivity',
                dataIndex: 'unique_reject_sensitivity',
                flex: 1
            }, {
                header: 'Non-unique REJECT sensitivity',
                dataIndex: 'non_unique_reject_sensitivity',
                flex: 1
            }, {
                header: 'Unique PASS sensitivity',
                dataIndex: 'unique_pass_sensitivity',
                flex: 1
            }, {
                header: 'PASS specificity',
                dataIndex: 'pass_specificity',
                flex: 1
            }, {
                header: 'REJECT specificity',
                dataIndex: 'reject_specificity',
                flex: 1
            }, {
                header: 'Imported',
                dataIndex: 'imported',
                flex: 1
            }, {
                text: 'Status',
                flex: 1,
                xtype: 'actioncolumn',
                dataIndex: 'status',
                align: 'center',
                renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
                    switch (record.data.filter_params.status) {
                        case 'ready':
                            this.items[0].glyph = command.current.entity_script_status_glyph['alt_ready'];
                            this.items[0].tooltip = 'ready';
                            break;
                        case 'running':
                            this.items[0].glyph = command.current.entity_script_status_glyph['running'];
                            this.items[0].tooltip = 'running';
                            break;
                        case 'error':
                            this.items[0].glyph = command.current.entity_script_status_glyph['error'];
                            this.items[0].tooltip = 'error';
                            break;
                    }
                }
            }, {
                text: 'Import filter',
                flex: 1,
                align: 'center',
                xtype: 'actioncolumn',
                items: [{
                    xtype: 'button',
                    itemId: 'import_filter_button',
                    text: null,
                    iconCls: 'dimgrayIcon',
                    scale: 'medium',
                    glyph: 'f063',
                    handler: 'onImportMapping',
                    isDisabled: function( view, rowIndex, colIndex, item, record ) {
                        return record.data.filter_params.status == 'running';
                    }
                }]
            }, {
                text: 'Remove filter',
                flex: 1,
                align: 'center',
                xtype: 'actioncolumn',
                items: [{
                    xtype: 'button',
                    itemId: 'remove_filter_button',
                    text: null,
                    iconCls: 'dimgrayIcon',
                    scale: 'medium',
                    glyph: 'xf014',
                    handler: 'onRemoveFilter'
                    /*isDisabled: function( view, rowIndex, colIndex, item, record ) {
                        return record.data.filter_params.status == 'running';
                    }*/
                }]
                }
            ]
        }
    }],

    listeners: {
        afterrender: 'onMapPlatformToBioFeatureAfterRender',
        cellClick: 'onCellClickAlignment'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.PlatformToBioFeatureMapping');
        this.events.afterrender.removeListener(this.events.afterrender.listeners[0], 'self', 0); // remove default event listener
        this.events.beforeshow.removeListener(this.events.beforeshow.listeners[0], 'self', 0); // remove default event listener
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.platform.microarray.MapPlatform', {
    extend: 'Ext.window.Window',
    xtype: 'window_map_microarray_platform',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'microarray_platforms',

    //controller: '',

    bodyPadding: 10,
    title: 'Map microarray',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 900,
    height: 700,
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

    items: [{
        xtype: 'map_platform_parameters',
        flex: 1
    }, {
        xtype: 'map_platform_results',
        flex: 2,
        title: 'Results'
    }]
});