/*Ext.define('command.view.NewCompendiumType', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_compendium_type',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel',
        'command.view.admin.CompendiumManagerController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'compendium_types',

    controller: 'compendium_manager_controller',
    bodyPadding: 10,
    title: 'Create compendium type',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 350,
    height: 200,
    constrain: true,

    items: {
        xtype: 'form',
        defaults: {
            anchor: '100%'
        },
        items: [{
            xtype: 'textfield',
            name: 'name',
            fieldLabel: 'Name',
            allowBlank: false
        }, {
            xtype: 'textarea',
            name: 'description',
            fieldLabel: 'Description',
            allowBlank: false
        }],
        buttons: [{
            text: 'Create',
            formBind: true,
            listeners: {
                click: 'onCreateNewCompendiumType'
            }
        }]
    }
});*/

Ext.define('command.view.NewCompendium', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_compendium',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel',
        'command.view.admin.CompendiumManagerController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'compendia',

    controller: 'compendium_manager_controller',
    bodyPadding: 10,
    title: 'Create compendium',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 500,
    height: 650,
    constrain: true,

    items: {
        xtype: 'form',
        defaults: {
            anchor: '100%'
        },
        fieldDefaults: {
            labelAlign: 'left',
            labelWidth: 150,
            anchor: '100%',
            msgTarget: 'side'
        },
        items: [{
            xtype: 'textfield',
            name: 'compendium_name',
            fieldLabel: 'Compendium name',
            allowBlank: false
        }, {
            xtype: 'textfield',
            name: 'compendium_nick_name',
            fieldLabel: 'Compendium nick name',
            allowBlank: false
        }, {
            xtype: 'combobox',
            anchor: '-15',
            minChars: 0,
            queryMode: 'local',
            store: null,
            typeAhead: false,
            editable: false,
            name: 'compendium_type',
            itemId: 'compendium_type',
            fieldLabel: 'Compendium type',
            valueField: 'id',
            displayField: 'name',
            allowBlank: false,
            dataIndex: 'id'
        }, {
            xtype: 'textarea',
            name: 'description',
            height: 150,
            fieldLabel: 'Description',
            allowBlank: false
        }, {
            xtype: 'textarea',
            name: 'html_description',
            height: 150,
            fieldLabel: 'HTML description',
            allowBlank: false
        }, {
            xtype: 'combobox',
            itemId: 'db_engine',
            displayField: 'db_engine',
            anchor: '-15',
            minChars: 0,
            queryMode: 'local',
            store: Ext.create('Ext.data.Store', {
                fields: ['db_engine'],
                data : [
                    {'db_engine':'django.db.backends.postgresql'}
                ]
            }),
            typeAhead: false,
            editable: false,
            name: 'db_engine',
            fieldLabel: 'DB engine',
            allowBlank: false,
            listeners: {
                select: 'onSelectDbEngine'
            }
        }, {
            xtype: 'textfield',
            name: 'db_user',
            itemId: 'db_user',
            fieldLabel: 'DB user',
            allowBlank: false
        }, {
            xtype: 'textfield',
            name: 'db_password',
            itemId: 'db_password',
            inputType: 'password',
            fieldLabel: 'DB password',
            allowBlank: false
        }, {
            xtype: 'textfield',
            name: 'db_host',
            itemId: 'db_host',
            fieldLabel: 'DB host',
            allowBlank: false
        }, {
            xtype: 'numberfield',
            name: 'db_port',
            itemId: 'db_port',
            fieldLabel: 'DB port',
            allowBlank: false
        }],
        buttons: [{
            text: 'Create',
            formBind: true,
            listeners: {
                click: 'onCreateNewCompendium'
            }
        }]
    }
});

Ext.define('command.view.admin.Compendium', {
    extend: 'command.Grid',
    xtype: 'compendium',
    title: 'Compendia',

    requires: [
        'Ext.panel.Panel',

        'command.store.Compendium',
        'command.model.Compendium',
        'command.view.admin.CompendiumManagerController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    controller: 'compendium_manager_controller',

    alias: 'widget.compendium',

    itemId: 'compendium_panel',

    reference: 'compendium_panel',

    viewModel: {},

    store: null,

    command_view: 'compendia',

    command_read_operation: 'read_compendia',

    bbar: [{
            text: null,
            tooltip: {
                text: 'Create compendium'
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            listeners: {
                click: 'onCreateCompendium'
            }
        },{
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Update compendium'
            },
            glyph: 'xf044',
            scale: 'medium',
            listeners: {
                click: 'onUpdateCompendium'
            },
            bind: {
                disabled: '{!compendium_panel.selection}'
            }
        }, {
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Delete compendium'
            },
            glyph: 'xf056',
            scale: 'medium',
            listeners: {
                click: 'onDeleteCompendium'
            },
            bind: {
                disabled: '{!compendium_panel.selection}'
            }
        }, {
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Initialize compendium'
            },
            glyph: 'xf1c0',
            scale: 'medium',
            listeners: {
                click: 'onInitCompendium'
            },
            bind: {
                disabled: '{!compendium_panel.selection}'
            }
        }
    ],

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Compendium name',
        flex: 2,
        sortable: true,
        dataIndex: 'compendium_name'
    }, {
        text: 'Nick name',
        flex: 2,
        sortable: true,
        dataIndex: 'compendium_nick_name'
    }, {
        text: 'Type',
        flex: 3,
        sortable: true,
        dataIndex: 'compendium_type',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            return value.name;
        }
    }, {
        text: 'Description',
        flex: 2,
        sortable: true,
        dataIndex: 'description'
    }, {
        text: 'DB engine',
        flex: 2,
        sortable: true,
        dataIndex: 'db_engine'
    }, {
        text: 'DB user',
        flex: 2,
        sortable: true,
        dataIndex: 'db_user'
    }, {
        text: 'DB Host',
        flex: 2,
        sortable: true,
        dataIndex: 'db_host'
    }],

    listeners: {
        afterrender: function (me, eOpts) {
            var selecAll = me.down('command_selectall');
            if (selecAll)
                selecAll.setVisible(false);
        }
    },

    initComponent: function() {
        this.store = Ext.create('command.store.Compendium');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.admin.CompendiumType', {
    extend: 'command.Grid',
    xtype: 'compendium_type',
    title: 'Compendium type',

    requires: [
        'Ext.panel.Panel',

        'command.store.CompendiumType',
        'command.model.CompendiumType',
        'command.view.admin.CompendiumManagerController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    alias: 'widget.compendium_type',

    itemId: 'compendium_type_panel',

    reference: 'compendium_type_panel',

    viewModel: {},

    store: null,

    controller: 'compendium_manager_controller',

    command_view: 'compendium_types',

    command_read_operation: 'read_compendium_types',

    /*bbar: [{
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'Create compendium type '
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            listeners: {
                click: 'onCreateCompendiumType'
            }
        },{
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Update compendium type '
            },
            glyph: 'xf044',
            scale: 'medium',
            listeners: {
                click: 'onUpdateCompendiumType'
            },
            bind: {
                disabled: '{!compendium_type_panel.selection}'
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Delete compendium type'
            },
            glyph: 'xf056',
            scale: 'medium',
            listeners: {
                click: 'onDeleteCompendiumType'
            },
            bind: {
                disabled: '{!compendium_type_panel.selection}'
            }
        }
    ],*/

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Name',
        flex: 2,
        sortable: true,
        dataIndex: 'name'
    }, {
        text: 'Description',
        flex: 4,
        sortable: true,
        dataIndex: 'description'
    }],

    listeners: {
        afterrender: function (me, eOpts) {
            var selecAll = me.down('command_selectall');
            if (selecAll)
                selecAll.setVisible(false);
        }
    },

    initComponent: function() {
        this.store = Ext.create('command.store.CompendiumType');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.admin.Compendia', {
    extend: 'Ext.panel.Panel',

    title: 'Compendium manager',

    requires: [
        'Ext.panel.Panel'
    ],

    alias: 'widget.compendia_manager',

    layout: 'accordion',

    items: [{
        xtype: 'compendium',
        border: false,
        layout: 'fit'
    }, {
        xtype: 'compendium_type',
        border: false,
        layout: 'fit'
    }],

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});