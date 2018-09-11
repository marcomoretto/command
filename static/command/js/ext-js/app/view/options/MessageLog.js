Ext.define('command.view.option.NewMessageLog', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_message_log',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    controller: 'message_log_controller',

    command_view: 'message_log',

    bodyPadding: 10,
    title: 'New Message',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 400,
    height: 430,
    constrain: true,

    items: {
        xtype: 'form',
        defaults: {
            anchor: '100%'
        },
        layout: 'anchor',
        fieldDefaults: {
            labelAlign: 'left',
            labelWidth: 70,
            anchor: '100%',
            msgTarget: 'side'
        },
        items: [{
            xtype: 'textfield',
            name: 'title',
            fieldLabel: 'Title',
            allowBlank: false
        }, {
            xtype: 'textarea',
            name: 'message',
            fieldLabel: 'Message',
            height: 300,
            allowBlank: false
        }],
        buttons: [{
            text: 'Create',
            formBind: true,
            listeners: {
                click: 'onCreateNewMessageLog'
            }
        }]
    }
});

Ext.define('command.view.option.MessageLogGrid', {
    extend: 'command.Grid',
    title: 'Message log',
    xtype: 'message_log_grid',
    itemId: 'message_log_grid',

    requires: [
        'Ext.panel.Panel'
    ],

    alias: 'widget.message_log_grid',

    controller: 'message_log_controller',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    reference: 'message_log',

    command_view: 'message_log',

    command_read_operation: 'read_message_log',

    command_ordering: 'DESC',

    store: null,

    viewConfig : {
        enableTextSelection: true
    },

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Date',
        flex: 2,
        sortable: true,
        dataIndex: 'date'
    }, {
        text: 'Title',
        flex: 2,
        sortable: true,
        dataIndex: 'title'
    }, {
        text: 'Message',
        flex: 3,
        sortable: true,
        tdCls: 'command_tooltip',
        dataIndex: 'message'
    }],
    features: [{ftype:'grouping'}],

    listeners: {
        afterrender: 'onMessageLogAfterRender'
    },

    bbar: [{
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'New comment'
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            listeners: {
                click: 'onCreateMessage'
            }
        }, {
            text: null,
            xtype: 'button',
            tooltip: {
                text: 'Delete comment'
            },
            iconCls: null,
            glyph: 'xf056',
            scale: 'medium',
            bind: {
                disabled: '{!message_log.selection}'
            },
            listeners: {
                click: 'onDeleteMessage'
            }
        }
    ],

    initComponent: function() {
        this.store = Ext.create('command.store.MessageLog');
        this.callParent();
    }
});

Ext.define('command.view.option.MessageLog', {
    extend: 'Ext.panel.Panel',
    title: 'Message log',
    xtype: 'message_log',

    layout: 'fit',

    items: [{
        xtype: 'message_log_grid',
        border: false,
        layout: 'fit'
    }],

    initComponent: function() {
        this.callParent();
    }
});