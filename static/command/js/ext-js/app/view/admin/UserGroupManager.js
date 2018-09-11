Ext.define('command.view.NewGroup', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_group',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel',
        'command.view.admin.UserGroupManagerController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'groups',

    controller: 'user_group_manager',
    bodyPadding: 10,
    title: 'New Group',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 350,
    height: 150,
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
            name: 'name',
            fieldLabel: 'Group name',
            allowBlank: false
        }],
        buttons: [{
            text: 'Create',
            formBind: true,
            listeners: {
                click: 'onCreateNewGroup'
            }
        }]
    }
});

Ext.define('command.view.NewUser', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_user',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel',
        'command.view.admin.UserGroupManagerController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'users',

    controller: 'user_group_manager',
    bodyPadding: 10,
    title: 'New User',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 350,
    height: 310,
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
            name: 'username',
            fieldLabel: 'Username',
            allowBlank: false
        }, {
            xtype: 'textfield',
            name: 'first_name',
            fieldLabel: 'First name',
            allowBlank: false
        }, {
            xtype: 'textfield',
            name: 'last_name',
            fieldLabel: 'Last name',
            allowBlank: false
        }, {
            xtype: 'textfield',
            name: 'email',
            fieldLabel: 'E-mail',
            allowBlank: false
        }, {
            xtype: 'checkboxgroup',
            fieldLabel: 'Groups',
            name: 'groups',
            columns: 1
        }, {
            xtype: 'checkbox',
            name: 'admin',
            fieldLabel: 'Admin'
        }, {
            xtype: 'checkbox',
            name: 'reset_password',
            fieldLabel: 'Reset password',
            checked: true,
            disabled: true
        }, {
            xtype: 'checkbox',
            name: 'active',
            fieldLabel: 'Active',
            checked: true
        }],
        buttons: [{
            text: 'Create',
            formBind: true,
            listeners: {
                click: 'onCreateNewUser'
            }
        }]
    }
});

Ext.define('command.view.admin.User', {
    extend: 'command.Grid',
    xtype: 'user',
    title: 'Users',

    requires: [
        'Ext.panel.Panel',

        'command.store.User',
        'command.model.User'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.user',

    itemId: 'user_panel',

    reference: 'user_panel',

    viewModel: {},

    command_view: 'users',

    command_read_operation: 'read_users',

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Username',
        flex: 2,
        sortable: true,
        dataIndex: 'username'
    }, {
        text: 'First name',
        flex: 2,
        sortable: true,
        dataIndex: 'first_name'
    }, {
        text: 'Last name',
        flex: 2,
        sortable: true,
        dataIndex: 'last_name'
    }, {
        text: 'E-mail',
        flex: 3,
        sortable: true,
        dataIndex: 'email'
    }, {
        text: 'Groups',
        flex: 3,
        sortable: true,
        dataIndex: 'groups',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            var groups = []
            record.data.user_groups.forEach(function (e) {
                groups.push(e.name);
            });
            return groups.join();
        }
    }, {
        text: 'Last login',
        flex: 3,
        sortable: true,
        dataIndex: 'last_login'
    }, {
        text: 'Date joined',
        flex: 3,
        sortable: true,
        dataIndex: 'date_joined'
    }, {
        text: 'Is active',
        flex: 1,
        sortable: false,
        xtype: 'actioncolumn',
        dataIndex: 'is_active',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            if (value) {
                this.items[0].glyph = 'xf00c';
                this.items[0].tooltip = 'User is enabled';
            } else {
                this.items[0].glyph = 'xf00d';
                this.items[0].tooltip = 'User is disabled';
            }
        }
    }, {
        text: 'Is superuser',
        flex: 1,
        sortable: true,
        dataIndex: 'is_superuser',
        xtype: 'actioncolumn',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            if (value) {
                this.items[0].glyph = 'xf00c';
                this.items[0].tooltip = 'User is superuser';
            } else {
                this.items[0].glyph = 'xf00d';
                this.items[0].tooltip = 'User is normal user';
            }
        }
    }],

    bbar: [{
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'Create user'
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            listeners: {
                click: 'onCreateUser'
            }
        },{
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Update user'
            },
            glyph: 'xf044',
            scale: 'medium',
            listeners: {
                click: 'onUpdateUser'
            },
            bind: {
                disabled: '{!user_panel.selection}'
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Delete user'
            },
            glyph: 'xf056',
            scale: 'medium',
            listeners: {
                click: 'onDeleteUser'
            },
            bind: {
                disabled: '{!user_panel.selection}'
            }
        }
    ],
    listeners: {
        afterrender: function (me, eOpts) {
            var selecAll = me.down('command_selectall');
            if (selecAll)
                selecAll.setVisible(false);
        }
    },

    initComponent: function() {
        this.store = Ext.create('command.store.User');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.admin.Group', {
    extend: 'command.Grid',
    xtype: 'group',
    title: 'Groups',

    requires: [
        'Ext.panel.Panel',

        'command.store.Group',
        'command.model.Group'
    ],

    alias: 'widget.group',

    itemId: 'group_panel',

    reference: 'group_panel',

    viewModel: {},

    store: null,

    command_view: 'groups',

    command_read_operation: 'read_groups',

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
    }],

    bbar: [{
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'Create group'
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            listeners: {
                click: 'onCreateGroup'
            }
        },{
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Update group'
            },
            glyph: 'xf044',
            scale: 'medium',
            listeners: {
                click: 'onUpdateGroup'
            },
            bind: {
                disabled: '{!group_panel.selection}'
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            tooltip: {
                text: 'Delete group'
            },
            glyph: 'xf056',
            scale: 'medium',
            listeners: {
                click: 'onDeleteGroup'
            },
            bind: {
                disabled: '{!group_panel.selection}'
            }
        }
    ],

    listeners: {
        afterrender: function (me, eOpts) {
            console.log(me.id);
            var selecAll = me.down('command_selectall');
            if (selecAll)
                selecAll.setVisible(false);
        }
    },

    initComponent: function() {
        this.store = Ext.create('command.store.Group');
        this.callParent();
        var paging = this.down('command_paging');
        paging.displayMsg = '';
        paging.doRefresh();
        var toolbar = this.down('toolbar');
        var filter = this.down('command_livefilter');
        var new_toolbar = this.addDocked({xtype:'toolbar'});
        new_toolbar[0].add(filter);
        toolbar.remove(filter);
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.admin.Permission', {
    extend: 'Ext.panel.Panel',
    title: 'Group Permission Manager',

    requires: [
        'Ext.panel.Panel'
    ],

    alias: 'widget.permission_manager',

    itemId: 'permission_panel',

    layout: {
        type: 'hbox',
        pack: 'start',
        align: 'stretch'
    },

    bodyPadding: 10,

    defaults: {
        frame: true,
        bodyPadding: 10
    },

    items: [
        {
            title: 'Groups',
            flex: 1,
            margin: '0 10 0 0',
            layout: 'fit',
            xtype: 'group',
            itemId: 'group',
            columns: [{
                text: 'ID',
                width: '20%',
                sortable: true,
                dataIndex: 'id'
            }, {
                text: 'Name',
                width: '70%',
                sortable: true,
                dataIndex: 'name'
            }],
            listeners: {
                itemclick: 'onGroupSelection'
            }
        },
        {
            title: 'Compendia',
            flex: 1,
            margin: '0 10 0 0',
            layout: 'fit',
            xtype: 'compendium',
            itemId: 'compendium_privileges',
            columnLines: false,
            selModel: {
                mode: 'SINGLE'
            },
            disabled: true,
            columns: [{
                text: 'ID',
                width: '10%',
                sortable: true,
                dataIndex: 'id',
                hidden: true
            }, {
                text: 'Nick name',
                width: '90%',
                sortable: true,
                dataIndex: 'compendium_nick_name'
            }],
            listeners: {
                select: 'onCompendiumSelection',
                afterrender: 'onCompendiumAfterRender'
            }
        },
        {
            title: 'Privileges',
            flex: 1,
            xtype: 'privileges',
            itemId: 'privileges',
            layout: 'fit',
            margin: '0 10 0 0',
            columnLines: false,
            selType: 'checkboxmodel',
            disabled: true,
            columns: [{
                text: 'ID',
                width: '10%',
                sortable: true,
                dataIndex: 'id',
                hidden: true
            }, {
                text: 'Permission',
                width: '80%',
                sortable: true,
                dataIndex: 'name'
            }],
            listeners: {
                select: 'onPermissionSelection',
                deselect: 'onPermissionDeselection'
            }
        }
    ]
});

Ext.define('command.view.admin.Privileges', {
    extend: 'Ext.grid.Panel',
    xtype: 'privileges',
    title: 'Privileges',

    requires: [
        'Ext.panel.Panel',

        'command.store.Privileges',
        'command.model.Privileges'
    ],

    alias: 'widget.privileges',

    itemId: 'privileges_panel',

    store: null,

    command_view: 'privileges',

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
    }],

    listeners: {
        expand: function (p, eOpts ) {
            // Hack to prevent store to crash when reloaded without having focus
            p.getView().refresh();
        },
        afterrender: 'onPrivilegesAfterRender'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.Privileges');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.admin.UserGroupManager', {
    extend: 'Ext.panel.Panel',
    title: 'User/Group Manager',

    requires: [
        'Ext.panel.Panel'
    ],
    controller: 'user_group_manager',

    alias: 'widget.user_group_manager',

    layout: 'accordion',

    items: [{
        xtype: 'user',
        border: false,
        layout: 'fit'
    }, {
        xtype: 'permission_manager',
        border: false
    }]
});
