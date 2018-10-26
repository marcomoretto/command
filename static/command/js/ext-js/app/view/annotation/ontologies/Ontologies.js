Ext.define('command.view.annotation.ontologies.NewOntologyNode', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_ontology_node',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    bodyPadding: 10,
    title: 'New ontology node',
    closable: true,
    autoShow: true,
    modal: true,
    width: 400,
    height: 300,
    constrain: true,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [
        {
            xtype: 'new_ontology_node_panel'
        }
    ]
});

Ext.define('command.view.annotation.ontologies.NewOntologyNodePanel', {
    extend: 'Ext.panel.Panel',
    xtype: 'new_ontology_node_panel',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'ontologies_controller',

    alias: 'widget.new_ontology_node_panel',

    itemId: 'new_ontology_node_panel',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    command_view: 'ontologies',

    items: [{
        xtype: 'form',
        itemId: 'ontology_form',
        items: [{
            xtype: 'textfield',
            anchor: '100%',
            margin: '10 10 10 5',
            allowBlank: false,
            fieldLabel: 'Node id',
            name: 'node_id',
            emptyText: 'ID'
        }, {
            xtype: 'textfield',
            anchor: '100%',
            margin: '10 10 10 5',
            allowBlank: true,
            fieldLabel: 'Edge type',
            name: 'edge_type',
            emptyText: 'is_a'
        }, {
            xtype: 'checkboxfield',
            anchor: '100%',
            margin: '10 10 10 5',
            fieldLabel  : 'Directed',
            name      : 'edge_directed',
            inputValue: '1',
            id        : 'edge_directed',
            checked: true
        }, {
            xtype: 'combobox',
            fieldLabel: 'Parent node',
            displayField: 'original_id',
            valueField: 'id',
            anchor: '100%',
            margin: '10 10 10 5',
            queryMode: 'local',
            typeAhead: true,
            allowBlank: true,
            editable: true,
            lastQuery: '',
            name: 'parent_node_id',
            itemId: 'parent_node_id',
            store: Ext.create('command.store.OntologyNodes'),
            listeners: {
                buffer: 50,
                afterrender: 'NewOntologyNodeParentAfterRender',
                change: 'NewOntologyNodeChange'
            }
        }, {
            xtype: 'fieldset',
            title: 'Fields',
            hidden: true,
            itemId: 'json_field_columns',
            items: [

            ]
        }, {
            buttonAlign: 'right',
            margin: '5 0 0 0',
            buttons: [{
                xtype: 'button',
                itemId: 'create_ontology_node_button',
                text: 'Create ontology node',
                formBind: true,
                listeners: {
                    click: 'onCreateOntologyNode'
                }
            }]
        }]
    }]
});

Ext.define('command.view.annotation.ontologies.NewOntologyPanel', {
    extend: 'Ext.panel.Panel',
    xtype: 'new_ontology_panel',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'ontologies_controller',

    alias: 'widget.new_ontology_panel',

    itemId: 'new_ontology_panel',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    command_view: 'ontologies',

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
            emptyText: 'New ontology',
            listeners: {
                //change: 'onExperimentIDChange'
            }
        }, {
            xtype: 'textarea',
            anchor: '100%',
            margin: '10 10 10 5',
            allowBlank: true,
            fieldLabel: 'Description',
            name: 'description',
            listeners: {
                //change: 'onExperimentIDChange'
            }
        }, {
            xtype: 'checkboxgroup',
            fieldLabel: 'Target',
            margin: '10 10 10 5',
            columns: 1,
            vertical: true,
            allowBlank: false,
            items: [
                { boxLabel: 'Biological feature', itemId: 'destination_bio_feature', name: 'destination', inputValue: 'biofeature', checked: true},
                { boxLabel: 'Sample', itemId: 'destination_sample', name: 'destination', inputValue: 'sample'}
            ]
        }, {
            xtype: 'checkboxfield',
            itemId: 'create_blank',
            name : 'create_blank',
            fieldLabel: 'Create blank',
            anchor: '100%',
            margin: '10 10 10 5',
            checked: true,
            listeners: {
                change: 'onCreateBlankChange'
            }
        }, {
            xtype: 'fieldset',
            title: 'Ontology fields',
            disabled: false,
            itemId: 'add_json_field_columns',
            name: 'add_json_field_columns',
            items: [{
                xtype: 'form',
                itemId: 'add_json_field_form',
                layout: 'hbox',
                anchor: '100%',
                items: [{
                    xtype: 'textfield',
                    anchor: '50%',
                    labelWidth: '100%',
                    margin: '10 10 10 5',
                    allowBlank: true,
                    fieldLabel: 'Name',
                    name: 'text',
                    emptyText: 'Description'
                }, {
                    xtype: 'textfield',
                    anchor: '50%',
                    labelWidth: '100%',
                    margin: '10 10 10 5',
                    allowBlank: true,
                    fieldLabel: 'Index',
                    name: 'data_index',
                    emptyText: 'description'
                }, {
                    xtype: 'button',
                    text: 'Add field',
                    margin: '10 10 10 5',
                    formBind: true,
                    listeners: {
                        click: 'onCreateOntologyField'
                    }
                }]
            }, {
                xtype: 'tagfield',
                anchor: '100%',
                margin: '0 0 0 10',
                name: 'ontology_tagfield',
                itemId: 'ontology_tagfield',
                store:  Ext.create('Ext.data.Store', {
                    fields: ['text','data_index'],
                    data: []
                }),
                fieldLabel: 'Fields',
                displayField: 'text',
                valueField: 'data_index',
                queryMode: 'local',
                filterPickList: true,
                hideTrigger: true
            }]
        }, {
            xtype: 'form',
            layout: 'hbox',
            margin: '10 10 10 5',
            itemId: 'ontology_file',
            name: 'ontology_file',
            anchor: '100%',
            disabled: true,
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
                itemId: 'create_ontology_button',
                text: 'Create ontology',
                formBind: true,
                listeners: {
                    click: 'onCreateOntology'
                }
                }]
            }]
    }]
});

Ext.define('command.view.annotation.ontologies.NewOntology', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_ontology',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    bodyPadding: 10,
    title: 'New ontology',
    closable: true,
    autoShow: true,
    modal: true,
    width: 600,
    height: 500,
    constrain: true,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [
        {
            xtype: 'new_ontology_panel'
        }
    ]
});

Ext.define('command.view.annotation.ontologies.AvailableOntologies', {
    extend: 'command.Grid',
    xtype: 'available_ontologies',
    title: 'Available ontologies',

    requires: [
        'Ext.panel.Panel',

        'command.store.Ontologies',
        'command.model.Ontologies'
    ],

    alias: 'widget.available_ontologies',

    itemId: 'available_ontologies',

    reference: 'available_ontologies',

    controller: 'ontologies_controller',

    viewModel: {},

    store: null,

    command_view: 'ontologies',

    command_read_operation: 'read_ontologies',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id',
        hidden: true
    }, {
        text: 'Name',
        flex: 1,
        sortable: true,
        dataIndex: 'name'
    }],

    bbar: [{
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'New ontology'
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            listeners: {
                click: 'onNewOntology'
            }
        },{
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Update ontology'
            },
            glyph: 'xf044',
            scale: 'medium',
            listeners: {
                click: 'onUpdateOntology'
            },
            bind: {
                disabled: '{!available_ontologies.selection}'
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Delete ontology'
            },
            glyph: 'xf056',
            scale: 'medium',
            listeners: {
                click: 'onDeleteOntology'
            },
            bind: {
                disabled: '{!available_ontologies.selection}'
            }
        }
    ],

    listeners: {
        itemclick: 'onSelectOntology'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.Ontologies');
        this.callParent();
        var paging = this.down('command_paging');
        paging.hide();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.annotation.ontologies.ViewOntology', {
    extend: 'command.Grid',
    xtype: 'view_ontology',

    requires: [
        'Ext.panel.Panel',

        'command.store.Ontologies',
        'command.model.Ontologies'
    ],

    alias: 'widget.view_ontology',

    itemId: 'view_ontology',

    reference: 'view_ontology',

    controller: 'ontologies_controller',

    viewModel: {},

    store: null,

    command_view: 'view_ontology',

    command_read_operation: 'get_ontology_nodes',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    columns: [],

    listeners: {
        itemclick: 'onSelectOntologyNode'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.OntologyNodes');
        this.events.beforeshow.removeListener(this.events.beforeshow.listeners[0], 'self', 0); // remove default event listener
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.annotation.ontologies.Cy', {
    extend: 'Ext.Component',

    xtype: 'cy_ontology',

    alias: 'widget.cy_ontology',

    itemId: 'cy_ontology',

    reference: 'cy_ontology',

    controller: 'ontologies_controller',

    listeners: {
        afterrender: 'CyOntologyAfterRender'
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

Ext.define('command.view.annotation.ontologies.Ontologies', {
    extend: 'Ext.Container',

    xtype: 'ontologies',

    title: 'Ontologies',

    requires: [
        'command.view.annotation.ontologies.OntologiesController'
    ],

    controller: 'ontologies_controller',

    store: null,

    alias: 'widget.ontologies',

    itemId: 'ontologies',

    reference: 'ontologies',

    viewModel: {},

    command_view: 'ontologies',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'border',
    bodyBorder: false,

    defaults: {
        collapsible: true,
        split: true,
        bodyPadding: 10
    },

    items: [
        {
            xtype: 'available_ontologies',
            region:'west',
            //margin: '5 0 0 0',
            flex: 3
        },
        {
            xtype: 'tabpanel',
            itemId: 'ontology_tabpanel',
            deferredRender: false,
            region: 'center',
            reference: 'ontology_tabpanel',
            //margin: '5 0 0 0',
            flex: 7,
            collapsible: false,
            title: 'Ontology: ',
            listeners: {
                tabchange: 'onOntologyTabChange'
            },
            items: [{
                xtype: 'view_ontology',
                title: 'Ontology nodes'
            }, {
                xtype: 'cy_ontology',
                title: 'Graph view'
            }],
            bbar: ['->', {
                text: null,
                xtype: 'button',
                itemId: 'new_ontology_node_button',
                tooltip: {
                    text: 'New node'
                },
                iconCls: null,
                glyph: 'xf055',
                scale: 'medium',
                listeners: {
                    click: 'onNewOntologyNode'
                },
                disabled: true
            },{
                xtype: 'button',
                itemId: 'update_ontology_node_button',
                text: null,
                iconCls: null,
                tooltip: {
                    text: 'Update node'
                },
                glyph: 'xf044',
                scale: 'medium',
                /*listeners: {
                    click: 'onUpdateGroup'
                },*/
                disabled: true
            }, {
                xtype: 'button',
                itemId: 'delete_ontology_node_button',
                text: null,
                iconCls: null,
                tooltip: {
                    text: 'Delete node'
                },
                glyph: 'xf056',
                scale: 'medium',
                listeners: {
                    click: 'onDeleteOntologyNode'
                },
                disabled: true
            }
        ]
        }
    ],

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});