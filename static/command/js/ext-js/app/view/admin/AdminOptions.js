Ext.define('command.view.admin.AdminOptions', {
    extend: 'Ext.panel.Panel',

    title: 'Admin options',

    requires: [
        'Ext.panel.Panel'
    ],

    alias: 'widget.admin_options',

    controller: 'admin_options_controller',

    defaults: {
        anchor: '100%',
        labelWidth: 100
    },

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'admin_options',
    
    itemId: 'admin_options',

    items: [{
        xtype: 'fieldset',
        title: 'Working directories',
        collapsible: false,
        defaults: {
            labelWidth: 150,
            anchor: '100%',
            layout: 'hbox',
            margin: '5 0 0 0'
        },
        items: [{
            xtype: 'form',
            items: [{
                fieldLabel: 'Download directory',
                labelWidth: 150,
                xtype: 'textfield',
                name: 'download_directory',
                itemId: 'download_directory',
                reference: 'download_directory',
                allowBlank: false,
                margin: '0 5 0 0',
                flex: 5
            }, {
                xtype: 'button',
                text: 'Check',
                flex: 1,
                formBind: true,
                margin: '0 5 0 0',
                listeners: {
                    click: 'onCheckDirectory'
                }
            }, {
                xtype: 'button',
                text: 'Clear',
                flex: 1,
                formBind: true,
                margin: '0 5 0 0',
                listeners: {
                    click: 'onClearDirectory'
                }
            }]
        },{
            xtype: 'form',
            items: [{
                fieldLabel: 'Raw data directory',
                labelWidth: 150,
                xtype: 'textfield',
                name: 'raw_data_directory',
                itemId: 'raw_data_directory',
                reference: 'raw_data_directory',
                allowBlank: false,
                margin: '0 5 0 0',
                flex: 5
            }, {
                xtype: 'button',
                text: 'Check',
                flex: 1,
                formBind: true,
                margin: '0 5 0 0',
                listeners: {
                    click: 'onCheckDirectory'
                }
            }, {
                xtype: 'button',
                text: 'Clear',
                flex: 1,
                formBind: true,
                margin: '0 5 0 0',
                listeners: {
                    click: 'onClearDirectory'
                }
            }]
        }]
    }, {
        xtype: 'fieldset',
        title: 'Jupyter notebook',
        collapsible: false,
        defaults: {
            labelWidth: 150,
            anchor: '100%',
            layout: 'hbox',
            margin: '5 0 0 0'
        },
        items: [{
            xtype: 'form',
            items: [{
                fieldLabel: 'Jupyter Notebook server',
                labelWidth: 150,
                xtype: 'textfield',
                name: 'jupyter_notebook_ip',
                itemId: 'jupyter_notebook_ip',
                reference: 'jupyter_notebook_ip',
                allowBlank: false,
                margin: '0 5 0 0',
                flex: 5
            }, {
                xtype: 'button',
                text: 'Check',
                flex: 1,
                formBind: true,
                margin: '0 5 0 0',
                listeners: {
                    click: 'onCheckJupyterNotebook'
                }
            }]
        }]
    }],

    listeners: {
        afterrender: function ( me, eOpts ) {
            var ws = command.current.ws;
            var operation = 'read_admin_options';
            var request = this.getRequestObject(operation);
            ws.listen();
            ws.demultiplex(request.view, function(action, stream) {
                if (action.request.operation == request.operation) {
                    action.data.admin_options.forEach(function (i) {
                        var option = me.down('#' + i.option_name);
                        option.setValue(i.option_value);
                    });
                }
                if (action.request.operation == 'refresh') {
                    ws.stream(request.view).send(request);
                }
            });
            ws.stream(request.view).send(request);
        }
    },

    initComponent: function() {
        this.callParent();
    }
});