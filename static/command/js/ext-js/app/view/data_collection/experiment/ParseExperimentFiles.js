Ext.define('command.view.data_collection.experiment.UploadFileAssignmentWin', {
    extend: 'Ext.window.Window',
    xtype: 'window_upload_experiment_file_assignment',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'file_assignment_list',

    controller: 'experiment_files_controller',

    bodyPadding: 10,
    title: 'Upload a file',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'anchor',
    width: 500,
    height: 140,
    constrain: true,

    items: [{
        xtype: 'form',
        items: [{
            xtype: 'filefield',
            anchor: '100%',
            margin: '10 0 0 5',
            fieldLabel: 'Experiment file',
            clearOnSubmit: false,
            name: 'experiment_data_file',
            reference: 'experiment_data_file',
            itemId: 'experiment_data_file',
            listeners: {
                change: 'onExperimentDataChange'
            }
        }]
    }],

    bbar: [ '->',
        {
            xtype: 'button',
            text: 'Upload',
            disabled: true,
            listeners: {
                click: 'onExperimentDataUploadFile'
            }
        }
    ]
});

Ext.define('command.view.data_collection.experiment.FileAssignmentWin', {
    extend: 'Ext.window.Window',
    xtype: 'window_experiment_file_assignment',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel',
        'Ext.form.FieldSet'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'file_assignment',

    controller: 'experiment_files_controller',

    bodyPadding: 10,
    title: 'Assign files and scripts to experiment structure',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'anchor',
    width: 500,
    height: 400,
    constrain: true,

    items: [{
        xtype: 'form',
        items: [{
            xtype: 'fieldset',
            title: 'Assignment script to use',
            collapsible: false,
            items: [{
                xtype: 'combo',
                fieldLabel: 'Script',
                name: 'assign_file_combobox',
                itemId: 'assign_file_combobox',
                emptyText: 'Select a script ...',
                anchor: '100%',
                queryMode: 'local',
                typeAhead: false,
                store: Ext.create('command.store.Script'),
                displayField: 'script_name',
                valueField: 'script_name',
                allowBlank: false,
                editable: false
            }, {
                xtype: 'textfield',
                anchor: '100%',
                fieldLabel: 'Parameters',
                name: 'parameters'
            }, {
                xtype: 'radiogroup',
                fieldLabel: 'Apply script to',
                itemId: 'apply_to',
                anchor: '100%',
                columns: 1,
                vertical: false,
                items: [
                    {boxLabel: 'Only selected files', name: 'apply_to', inputValue: 'selected', checked: true},
                    {boxLabel: 'All files', name: 'apply_to', inputValue: 'all'}
                ]
            }]
        }, {
            xtype: 'tbspacer',
            height: 10
        }, {
            xtype: 'tabpanel',
            bodyPadding: 10,
            layout: 'fit',
            items: [{
                title: 'Experiment',
                layout: 'anchor',
                items: [{
                    xtype: 'combo',
                    fieldLabel: 'Script',
                    name: 'assign_file_combobox_exp',
                    itemId: 'assign_file_combobox_exp',
                    emptyText: 'Select a script ...',
                    anchor: '100%',
                    queryMode: 'local',
                    typeAhead: false,
                    store: Ext.create('command.store.Script'),
                    displayField: 'script_name',
                    valueField: 'script_name',
                    allowBlank: true,
                    editable: false,
                    entity_type: 'experiment',
                    listeners: {
                        focus: 'onFocusExperimentEntityType'
                    }
                }, {
                    xtype: 'numberfield',
                    minValue: 0,
                    anchor: '100%',
                    fieldLabel: 'Execution order',
                    name: 'order_exp',
                    itemId: 'order_exp'
                }, {
                    xtype: 'textfield',
                    anchor: '100%',
                    fieldLabel: 'Parameters',
                    name: 'parameters_exp'
                }]
            }, {
                title: 'Platform',
                layout: 'anchor',
                items: [{
                    xtype: 'combo',
                    fieldLabel: 'Script',
                    name: 'assign_file_combobox_plt',
                    itemId: 'assign_file_combobox_plt',
                    emptyText: 'Select a script ...',
                    anchor: '100%',
                    queryMode: 'local',
                    typeAhead: false,
                    store: Ext.create('command.store.Script'),
                    displayField: 'script_name',
                    valueField: 'script_name',
                    allowBlank: true,
                    editable: false,
                    entity_type: 'platform',
                    listeners: {
                        focus: 'onFocusExperimentEntityType'
                    }
                }, {
                    xtype: 'numberfield',
                    minValue: 0,
                    anchor: '100%',
                    fieldLabel: 'Execution order',
                    name: 'order_plt',
                    itemId: 'order_plt'
                }, {
                    xtype: 'textfield',
                    anchor: '100%',
                    fieldLabel: 'Parameters',
                    name: 'parameters_plt'
                }]
            }, {
                title: 'Sample',
                layout: 'anchor',
                items: [{
                    xtype: 'combo',
                    fieldLabel: 'Script',
                    name: 'assign_file_combobox_smp',
                    itemId: 'assign_file_combobox_smp',
                    emptyText: 'Select a script ...',
                    anchor: '100%',
                    queryMode: 'local',
                    typeAhead: false,
                    store: Ext.create('command.store.Script'),
                    displayField: 'script_name',
                    valueField: 'script_name',
                    allowBlank: true,
                    editable: false,
                    entity_type: 'sample',
                    listeners: {
                        focus: 'onFocusExperimentEntityType'
                    }
                }, {
                    xtype: 'numberfield',
                    minValue: 0,
                    anchor: '100%',
                    fieldLabel: 'Execution order',
                    name: 'order_smp',
                    itemId: 'order_smp'
                }, {
                    xtype: 'textfield',
                    anchor: '100%',
                    fieldLabel: 'Parameters',
                    name: 'parameters_smp'
                }]
            }]
        }],

        bbar: ['->',
            {
                xtype: 'button',
                text: 'Run assignment script',
                itemId: 'run_assignment_script',
                formBind: true,
                handler: 'onAssignFiles'
            }
        ]
    }],

    listeners: {
        afterrender: 'onExperimentFileAssignmentWindowAfterRender'
    }
});

Ext.define('command.view.data_collection.experiment.FileAssignment', {
    extend: 'command.Grid',
    xtype: 'file_assignment',
    title: 'File assignment',

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.file_assignment',

    itemId: 'file_assignment',

    reference: 'file_assignment',

    viewModel: {},

    command_view: 'file_assignment_list',

    command_read_operation: 'read_experiment_files',

    controller: 'experiment_files_controller',

    selModel: {
        selType: 'checkboxmodel',
        mode: 'MULTI',
        checkOnly: true,
        allowDeselect: false
    },

    columns: [{
        text: 'Name',
        flex: 3,
        sortable: true,
        dataIndex: 'name',
        renderer: function(value, metadata, record) {
            return '<a href="file_assignment/read_experiment_file?path=' + record.data.path + '" target="_blank">'+ value +'</a>';
        }
    }, {
        text: 'Type',
        flex: 1,
        sortable: true,
        dataIndex: 'type'
    }, {
        text: 'Size (Kb)',
        flex: 1,
        sortable: true,
        dataIndex: 'size'
    }, {
        text: 'Date',
        flex: 3,
        sortable: true,
        dataIndex: 'date'
    }],

    listeners: {
        afterrender: 'onFileAssignmentAfterRender'
    },

    bbar: [{
            text: null,
            tooltip: {
                text: 'Upload file'
            },
            iconCls: null,
            glyph: 'xf093',
            scale: 'medium',
            listeners: {
                click: 'onUploadFile'
            }
        },{
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Delete file'
            },
            glyph: 'xf056',
            scale: 'medium',
            listeners: {
                click: 'onDeleteFile'
            },
            bind: {
                disabled: '{!file_assignment.selection}'
            }
        }, '->', {
            xtype: 'button',
            text: null,
            iconCls: null,
            scale: 'medium',
            tooltip: {
                text: 'Clean all file assignment'
            },
            glyph: 'xf014',
            listeners: {
                click: 'onCleanFileAssignment'
            }
        }, {
            text: null,
            tooltip: {
                text: 'Use assignment script to assign files to experiment entities'
            },
            iconCls: null,
            glyph: 'xf08e',
            scale: 'medium',
            listeners: {
                click: 'onAssignFileToExperiment'
            }
        }
    ],

    initComponent: function() {
        this.store = Ext.create('command.store.ExperimentFiles');
        this.events.afterrender.removeListener(this.events.afterrender.listeners[0], 'self', 0); // remove default event listener
        this.events.beforeshow.removeListener(this.events.beforeshow.listeners[0], 'self', 0); // remove default event listener
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.experiment.FileAssignmentExperiments', {
    extend: 'Ext.grid.Panel',

    xtype: 'file_assignment_experiments',
    title: 'Experiments',

    requires: [
        'Ext.grid.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.file_assignment_experiments',

    itemId: 'file_assignment_experiments',

    reference: 'file_assignment_experiments',

    viewModel: {},

    command_view: 'experiment_file_assignment',

    command_read_operation: 'read_experiment_experiment_files',

    controller: 'experiment_files_controller',

    selModel: 'rowmodel',
    margin: '10 0 0 5',
    plugins: [{
        ptype: 'cellediting',
        clicksToMoveEditor: 0
    }],
    autoLoad: false,
    bind: {
        store: {
            data: '{record.parsing_details}'
        },
        title: 'Parsing script and files for platform {record.platform_name}'
    },
    columns: [{
        header: 'Script name',
        dataIndex: 'script_name',
        flex: 1,
        editor: {
            xtype: 'combobox',
            allowBlank: false,
            editable: false,
            forceSelection: true,
            store: Ext.create('command.store.Script'),
            valueField: 'script_name',
            displayField: 'script_name',
            queryMode: 'local',
            listeners: {
                focus: 'onFocusExperimentExperimentScripts',
                change: 'onChangeAssociatedFileDetails'
            }
        }
    }, {
        header: 'Parameters',
        dataIndex: 'parameters',
        flex: 1,
        editor: {
            xtype: 'textfield',
            listeners: {
                focusleave: 'onFocusLeaveAssociatedFileDetails'
            }
        }
    }, {
        header: 'Execution order',
        dataIndex: 'order',
        editor: {
            xtype: 'numberfield',
            minValue: 0,
            listeners: {
                focusleave: 'onFocusLeaveAssociatedFileDetails'
            }
        },
        flex: 1
    }, {
        header: 'Platform file',
        dataIndex: 'input_filename',
        flex: 1,
        editor: {
            xtype: 'combobox',
            allowBlank: false,
            editable: false,
            forceSelection: true,
            queryMode: 'local',
            store: Ext.create('command.store.ExperimentFiles'),
            valueField: 'name',
            displayField: 'name',
            listeners: {
                focus: 'onFocusExperimentExperimentFiles',
                change: 'onChangeAssociatedFileDetails'
            }
        }
    }, {
        text: 'Status',
        flex: 1,
        xtype: 'actioncolumn',
        dataIndex: 'status',
        align: 'center',
        iconCls: 'dimgrayIcon',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            switch (record.data.status.name) {
                case 'entity_script_ready':
                    this.items[0].glyph = command.current.entity_script_status_glyph['ready'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_scheduled':
                    this.items[0].glyph = command.current.entity_script_status_glyph['scheduled'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_running':
                    this.items[0].glyph = command.current.entity_script_status_glyph['running'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_error':
                    this.items[0].glyph = command.current.entity_script_status_glyph['error'];
                    this.items[0].tooltip = value.description + ". Click to see last log message.";
                    break;
                case 'entity_script_parsed':
                    this.items[0].glyph = command.current.entity_script_status_glyph['parsed'];
                    this.items[0].tooltip = value.description;
                    break;
            }
        },
        handler: 'onExperimentShowParsingError'
    }, {
        text: 'Remove',
        align: 'center',
        xtype: 'actioncolumn',
        iconCls: 'dimgrayIcon',
        items: [{
              xtype: 'button',
              glyph: 'xf056',
              scale: 'small',
              handler: 'onRemoveExperimentFileAssignment'
           }]
        }
    ],

    bbar: ['->', {
        xtype: 'button',
        text: null,
        iconCls: null,
        scale: 'medium',
        tooltip: {
            text: 'Clean all experiment file assignment'
        },
        glyph: 'xf014',
        listeners: {
            click: 'onCleanExperimentsFileAssignment'
        }
        },
        {
            xtype: 'button',
            text: null,
            iconCls: null,
            scale: 'medium',
            glyph: 'xf144',
            tooltip: {
                text: 'Run script'
            },
            listeners: {
                click: 'onRunExperimentParsingScript'
            }
    }],

    listeners: {
        afterrender: 'onFileAssignmentExperimentAfterRender'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.ExperimentFiles');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.experiment.FileAssignmentPlatforms', {
    extend: 'command.Grid',
    xtype: 'file_assignment_platforms',
    title: 'Platforms',

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.file_assignment_platforms',

    itemId: 'file_assignment_platforms',

    reference: 'file_assignment_platforms',

    viewModel: {},

    command_view: 'platform_file_assignment',

    command_read_operation: 'read_experiment_platform_files',

    controller: 'experiment_files_controller',

    last_row_index_clicked: null,

    selModel: {
        selType: 'checkboxmodel',
        mode: 'MULTI',
        checkOnly: true,
        allowDeselect: false
    },

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Access ID',
        flex: 3,
        sortable: true,
        dataIndex: 'platform_access_id'
    }, {
        text: 'Name',
        flex: 3,
        sortable: true,
        dataIndex: 'platform_name'
    }, {
        header: 'Reporter Platform',
        dataIndex: 'reporter_platform',
        flex: 3,
        editor: {
            xtype: 'combo',
            allowBlank: false,
            editable: false,
            forceSelection: true,
            store: Ext.create('command.store.Platforms'),
            displayField: 'platform_access_id',
            queryMode: 'local',
            listeners: {
                focus: 'onFocusReporterPlatform',
                focusleave: 'onFocusLeaveReporterPlatform'
            }
        }
    }, {
        text: 'Status',
        flex: 1,
        xtype: 'actioncolumn',
        dataIndex: 'status',
        iconCls: 'dimgrayIcon',
        align: 'center',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            switch (value.name) {
                case 'entity_script_ready':
                    this.items[0].glyph = command.current.entity_script_status_glyph['ready'];
                    this.items[0].tooltip =value.description;
                    break;
                case 'entity_script_scheduled':
                    this.items[0].glyph = command.current.entity_script_status_glyph['scheduled'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_running':
                    this.items[0].glyph = command.current.entity_script_status_glyph['running'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_error':
                    this.items[0].glyph = command.current.entity_script_status_glyph['error'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_parsed':
                    this.items[0].glyph = command.current.entity_script_status_glyph['parsed'];
                    this.items[0].tooltip = value.description;
                    break;
            }
        }
    }, {
        text: 'Run script(s)',
        flex: 1,
        align: 'center',
        xtype: 'actioncolumn',
        items: [{
            xtype: 'button',
            itemId: 'run_button',
            text: null,
            iconCls: 'dimgrayIcon',
            scale: 'medium',
            glyph: 'xf144',
            handler: 'onRunPlatformParsingScript',
            isDisabled: function( view, rowIndex, colIndex, item, record ) {
                var disabled = false;
                if (record.data.status.name == 'entity_script_scheduled') {
                    disabled = true;
                }
                if (record.data.status.name == 'entity_script_running') {
                    disabled = true;
                }
                return disabled;
            }
        }]
    }],

    plugins: [{
        ptype: 'cellediting',
        clicksToMoveEditor: 0
            }, {
        ptype: 'rowwidget',
        widget: {
            xtype: 'grid',
            selModel: 'rowmodel',
            plugins: [{
                ptype: 'cellediting',
                clicksToMoveEditor: 0
            }],
            autoLoad: false,
            bind: {
                store: {
                    data: '{record.parsing_details}'
                },
                title: 'Parsing script and files for platform {record.platform_name}'
            },
            columns: [{
                header: 'Script name',
                dataIndex: 'script_name',
                flex: 1,
                editor: {
                    xtype: 'combobox',
                    allowBlank: false,
                    editable: false,
                    forceSelection: true,
                    store: Ext.create('command.store.Script'),
                    valueField: 'script_name',
                    displayField: 'script_name',
                    queryMode: 'local',
                    listeners: {
                        focus: 'onFocusExperimentPlatformScripts',
                        change: 'onChangeAssociatedFileDetails'
                    }
                }
            }, {
                header: 'Parameters',
                dataIndex: 'parameters',
                flex: 1,
                editor: {
                    xtype: 'textfield',
                    listeners: {
                        focusleave: 'onFocusLeaveAssociatedFileDetails'
                    }
                }
            }, {
                header: 'Execution order',
                dataIndex: 'order',
                editor: {
                    xtype: 'numberfield',
                    minValue: 0,
                    listeners: {
                        focusleave: 'onFocusLeaveAssociatedFileDetails'
                    }
                },
                flex: 1
            }, {
                header: 'Platform file',
                dataIndex: 'input_filename',
                flex: 1,
                editor: {
                    xtype: 'combobox',
                    allowBlank: false,
                    editable: false,
                    forceSelection: true,
                    queryMode: 'local',
                    store: Ext.create('command.store.ExperimentFiles'),
                    valueField: 'name',
                    displayField: 'name',
                    listeners: {
                        focus: 'onFocusExperimentPlatformFiles',
                        change: 'onChangeAssociatedFileDetails'
                    }
                }
            }, {
                text: 'Remove',
                align: 'center',
                xtype: 'actioncolumn',
                items: [{
                      xtype: 'button',
                      glyph: 'xf056',
                      scale: 'small',
                      iconCls: 'dimgrayIcon',
                      handler: 'onRemovePlatformFileAssignment'
                   }]
                }
            ]
        }
    }],

    bbar: ['->', {
        xtype: 'button',
        text: null,
        iconCls: null,
        scale: 'medium',
        tooltip: {
            text: 'Clean all platform file assignment'
        },
        glyph: 'xf014',
        listeners: {
            click: 'onCleanPlatformsFileAssignment'
        }
        },
        {
            xtype: 'button',
            text: null,
            iconCls: null,
            scale: 'medium',
            tooltip: {
                text: 'Run script(s)'
            },
            glyph: 'xf144',
            menu: {
                xtype: 'menu',
                forceLayout: true,
                items: [{
                    text: 'Run all',
                    itemId: 'run_all',
                    scale: 'medium',
                    tooltip: {
                        text: 'Run all'
                    },
                    glyph: 'xf0cb',
                    listeners: {
                        click: 'onRunMultiplePlatformParsingScript'
                    }
                }, {
                    text: 'Run selected',
                    scale: 'medium',
                    itemId: 'run_selected',
                    tooltip: {
                        text: 'Run selected'
                    },
                    glyph: 'xf046',
                    listeners: {
                        click: 'onRunMultiplePlatformParsingScript'
                    }
                }]
            }
    }],

    listeners: {
        afterrender: 'onFileAssignmentPlatformAfterRender',
        rowclick: 'onFileAssignmentPlatformClick'
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

Ext.define('command.view.data_collection.experiment.FileAssignmentSamples', {
    extend: 'command.Grid',
    xtype: 'file_assignment_samples',
    title: 'Samples',

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.file_assignment_samples',

    itemId: 'file_assignment_samples',

    reference: 'file_assignment_samples',

    viewModel: {},

    command_view: 'sample_file_assignment',

    command_read_operation: 'read_experiment_sample_files',

    controller: 'experiment_files_controller',

    selModel: {
        selType: 'checkboxmodel',
        mode: 'MULTI',
        checkOnly: true,
        allowDeselect: false
    },

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Name',
        flex: 4,
        sortable: true,
        dataIndex: 'sample_name'
    }, {
        text: 'Status',
        flex: 1,
        xtype: 'actioncolumn',
        dataIndex: 'status',
        align: 'center',
        iconCls: 'dimgrayIcon',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            switch (value.name) {
                case 'entity_script_ready':
                    this.items[0].glyph = command.current.entity_script_status_glyph['ready'];
                    this.items[0].tooltip =value.description;
                    break;
                case 'entity_script_scheduled':
                    this.items[0].glyph = command.current.entity_script_status_glyph['scheduled'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_running':
                    this.items[0].glyph = command.current.entity_script_status_glyph['running'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_error':
                    this.items[0].glyph = command.current.entity_script_status_glyph['error'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'entity_script_parsed':
                    this.items[0].glyph = command.current.entity_script_status_glyph['parsed'];
                    this.items[0].tooltip = value.description;
                    break;
            }
        }
    }, {
        text: 'Run script(s)',
        flex: 1,
        align: 'center',
        xtype: 'actioncolumn',
        renderer: function (val, metadata, record) {

        },
        items: [{
            xtype: 'button',
            itemId: 'run_button',
            text: null,
            iconCls: 'dimgrayIcon',
            scale: 'medium',
            glyph: 'xf144',
            handler: 'onRunSampleParsingScript',
            isDisabled: function( view, rowIndex, colIndex, item, record ) {
                var disabled = false;
                if (record.data.status.name == 'entity_script_scheduled') {
                    disabled = true;
                }
                if (record.data.status.name == 'entity_script_running') {
                    disabled = true;
                }
                return disabled;
            }
        }]
    }],

    plugins: [{
        ptype: 'rowwidget',
        widget: {
            xtype: 'grid',
            selModel: 'rowmodel',
            plugins: [{
                ptype: 'cellediting',
                clicksToMoveEditor: 0
            }],
            autoLoad: false,
            bind: {
                store: {
                    data: '{record.parsing_details}'
                },
                title: 'Parsing script and files for sample {record.sample_name}'
            },
            columns: [{
                header: 'Script name',
                dataIndex: 'script_name',
                flex: 1,
                editor: {
                    xtype: 'combobox',
                    allowBlank: false,
                    editable: false,
                    forceSelection: true,
                    store: Ext.create('command.store.Script'),
                    valueField: 'script_name',
                    displayField: 'script_name',
                    queryMode: 'local',
                    listeners: {
                        focus: 'onFocusExperimentSampleScripts',
                        focusleave: 'onFocusLeaveAssociatedFileDetails'
                    }
                }
            }, {
                header: 'Parameters',
                dataIndex: 'parameters',
                flex: 1,
                editor: {
                    xtype: 'textfield',
                    listeners: {
                        focusleave: 'onFocusLeaveAssociatedFileDetails'
                    }
                }
            }, {
                header: 'Execution order',
                dataIndex: 'order',
                editor: {
                    xtype: 'numberfield',
                    minValue: 0,
                    listeners: {
                        focusleave: 'onFocusLeaveAssociatedFileDetails'
                    }
                },
                flex: 1
            }, {
                header: 'Sample file',
                dataIndex: 'input_filename',
                flex: 1,
                editor: {
                    xtype: 'combobox',
                    allowBlank: false,
                    editable: false,
                    forceSelection: true,
                    queryMode: 'local',
                    store: Ext.create('command.store.ExperimentFiles'),
                    valueField: 'name',
                    displayField: 'name',
                    listeners: {
                        focus: 'onFocusExperimentSampleFiles',
                        focusleave: 'onFocusLeaveAssociatedFileDetails'
                    }
                }
            }, {
                text: 'Remove',
                align: 'center',
                xtype: 'actioncolumn',
                items: [{
                      xtype: 'button',
                      glyph: 'xf056',
                      scale: 'small',
                      iconCls: 'dimgrayIcon',
                      handler: 'onRemoveSampleFileAssignment'
                   }]
                }
            ]
        }
    }],

    bbar: ['->', {
        xtype: 'button',
        text: null,
        iconCls: null,
        scale: 'medium',
        tooltip: {
            text: 'Clean all samples file assignment'
        },
        glyph: 'xf014',
        listeners: {
            click: 'onCleanSamplesFileAssignment'
        }
        },
        {
            xtype: 'button',
            text: null,
            iconCls: null,
            scale: 'medium',
            tooltip: {
                text: 'Run script(s)'
            },
            glyph: 'xf144',
            menu: {
                xtype: 'menu',
                forceLayout: true,
                items: [{
                    text: 'Run all',
                    scale: 'medium',
                    itemId: 'run_all',
                    tooltip: {
                        text: 'Run all'
                    },
                    glyph: 'xf0cb',
                    listeners: {
                        click: 'onRunMultipleSampleParsingScript'
                    }
                }, {
                    text: 'Run selected',
                    scale: 'medium',
                    itemId: 'run_selected',
                    tooltip: {
                        text: 'Run selected'
                    },
                    glyph: 'xf046',
                    listeners: {
                        click: 'onRunMultipleSampleParsingScript'
                    }
                }]
            }
    }],

    listeners: {
        afterrender: 'onFileAssignmentSamplesAfterRender'
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

Ext.define('command.view.data_collection.experiment.ExperimentFiles', {
    extend: 'Ext.tab.Panel',

    plain: false,

    defaults: {
        bodyPadding: 5,
        scrollable: true,
        border: false
    },

    layout: 'fit',

    viewModel: {},

    xtype: 'experiment_files',

    itemId: 'experiment_files',

    title: 'Experiment files',

    controller: 'experiment_files_controller',

    items: [
        {
            xtype: 'file_assignment',
            flex: 1,
            layout: 'fit'
        },
        {
            xtype: 'file_assignment_experiments',
            title: 'Experiment',
            flex: 1,
            layout: 'fit'
        }, {
            xtype: 'file_assignment_platforms',
            title: 'Platforms',
            flex: 1,
            layout: 'fit'
        }, {
            xtype: 'file_assignment_samples',
            title: 'Samples',
            flex: 1,
            layout: 'fit'
        }
    ],
    listeners: {
        expand: function (p, eOpts) {
            p.down('file_assignment').view.refresh();
            p.down('file_assignment_experiments').view.refresh();
            p.down('file_assignment_platforms').view.refresh();
            p.down('file_assignment_samples').view.refresh();
        }
    }

});
