Ext.define('command.view.main.Log', {
    extend: 'Ext.window.Window',
    xtype: 'log_window',
    title: 'title',
    height: 500,
    width: 500,
    modal: true
});

/**
 * The main application class. An instance of this class is created by app.js when it
 * calls Ext.application(). This is the ideal place to handle application launch and
 * initialization details.
 */
Ext.define('command.Application', {
    extend: 'Ext.app.Application',
    
    name: 'command',

    stores: [

    ],

    appProperty: 'current',

    version: null,

    ws: null,

    ws_connect: false,

    ws_channel_name: null,

    version: null,

    panel_glyph: {
        'parse_experiment': 'xf120',
        'import_experiment_public': 'xf0c3',
        'compendia_manager': 'xf00a',
        'user_group_manager': 'xf0c0',
        'admin_options': 'xf0ca',
        'experiments': 'xf0c3',
        'platform_manager': 'f21a',
        'message_log': 'f086',
        'bio_feature': 'f1fb',
        'welcome': 'f259'
    },

    experiment_status_glyph: {
        'new': 'xf0c3',
        'scheduled': 'xf017',
        'downloading': 'xf019',
        'data_ready': 'xf0c7',
        'raw_data': 'f00c',
        'excluded': 'f057',
        'platform_present': 'f21a'
    },

    entity_script_status_glyph : {
        'alt_ready': 'f00c',
        'ready': 'xf120',
        'running': 'xf085',
        'error': 'xf00d',
        'parsed': 'xf00c',
        'scheduled': 'xf017'
    },

    panel_multi_instances: [
        'parse_experiment'
    ],

    admin_panels: [
        'user_group_manager',
        'compendia_manager',
        'admin_options'
    ],

    requires: [
        'Ext.Viewport',
        'command.view.login.Login',
        'command.view.login.ResetPassword'
    ],

    defaultToken : 'view/welcome',

    routes : {
        'view/:panel': {
            before : 'wsConnect',
            action : 'onShowPanel'
        },
        'view/:panel/:params': {
            before : 'wsConnect',
            action : 'onShowPanel'
        }
    },

    createWin: function(config) {
        var panel = config.xtype;
        var views = JSON.parse(localStorage.getItem("views"));
        var compendium = JSON.parse(localStorage.getItem("current_compendium"));
        console.log(views, compendium, panel);
        if ((compendium && views[compendium.compendium_nick_name].indexOf(panel) != -1) ||
            (views['no_compendium'].indexOf(panel) != -1)) {
            Ext.create(config);
        } else {
            this.showMessage('permission_error', '', '');
        }
    },

    showMessage: function(type, title, message) {
        switch (type) {
            case 'error':
                Ext.MessageBox.show({
                    title: title,
                    msg: message,
                    buttons: Ext.MessageBox.OK,
                    icon: Ext.MessageBox.ERROR,
                    fn: function () {
                    }
                });
                break;
            case 'info':
                Ext.MessageBox.show({
                    title: title,
                    msg: message,
                    buttons: Ext.MessageBox.OK,
                    icon: Ext.MessageBox.INFO,
                    fn: function () {
                    }
                });
                break;
            case 'permission_error':
                Ext.MessageBox.show({
                    title: 'Permission denied',
                    msg: "Sorry you don't have enough rights to continue",
                    buttons: Ext.MessageBox.OK,
                    icon: Ext.MessageBox.ERROR,
                    fn: function () {
                    }
                });
                break;
            case 'parsing_log':
                var win = Ext.create({
                    xtype: 'log_window',
                    title: title,
                    items: [{
                        xtype: 'panel',
                        itemId: 'message_panel',
                        margin: '10 10 10 10',
                        html: message
                    }]
                });
                win.show();
                break
        }
    },

    checkHttpResponse: function (message) {
        console.log('HTTP');
        var response = JSON.parse(message.responseText);
        if (!response.success) {
            this.showMessage(response.type, response.title, response.message);
            return false;
        }
        return true;
    },

    onShowPanel: function(panel, params) {
        var main = Ext.ComponentQuery.query('#main_panel')[0];
        var views = JSON.parse(localStorage.getItem("views"));
        var compendium = JSON.parse(localStorage.getItem("current_compendium"));
        console.log(views, compendium, panel);
        if ((compendium && views[compendium.compendium_nick_name].indexOf(panel) != -1) ||
            (views['no_compendium'].indexOf(panel) != -1) || (panel == "welcome")) {
            main.getController().openPanel(panel, this.panel_glyph[panel], params);
        } else {
            this.showMessage('permission_error', '', '');
        }
    },

    updatePermission: function() {
        Ext.Ajax.request({
            url: 'update_permission/',
            success: function (response) {
                var resData = Ext.decode(response.responseText);
                if (resData.login) {
                    localStorage.setItem("views", JSON.stringify(resData.views));
                }
            },
            failure: function (response) {
                Ext.Msg.alert('Server problem', 'Server Problem');
            }
        });
    },

    wsConnect: function(panel, params, action) {
        if (action) {
            this._wsConnect(panel, action, params);
        } else {
            this._wsConnect(panel, params);
        }
    },

    _wsConnect: function(panel, action, params) {
        var me = this;
        if (me.ws_connect) {
            action.resume();
        } else {
            this.ws = new channels.WebSocketBridge();
            this.ws.connect('/ws/');
            this.ws.socket.addEventListener('open', function () {
                console.log('WS connection open');
                me.ws_connect = true;
                action.resume();
            });
            this.ws.socket.addEventListener('message', function (message) {
                var data = JSON.parse(message.data);
                if (data.stream == 'message') {
                    console.log('WEB SOCKET');
                    console.log(message);
                    command.current.showMessage(data.payload.request.type, data.payload.data.title, data.payload.data.message);
                }
                //console.log(message);
            });
            this.ws.socket.addEventListener('close', function () {
                console.log('WS connection close');
                me.ws_connect = false;
            });
        }
    },
    
    launch: function () {
         Ext.create('Ext.data.Store', {
            storeId : 'itemsStore',
            fields  : ['item', 'desc'],
            data    : [{
                item : 'A12',
                desc : 'Stand'
            }, {
                item : 'A13',
                desc : 'Holder'
            }, {
                item : 'A15',
                desc : 'Hanger'
            }]
        });

        Ext.create('Ext.data.Store', {
            storeId : 'simpsonsStore',
            fields  : ['name', 'email', 'phone'],
            data    : [{
                name  : 'Lisa',
                email : 'lisa@simpsons.com',
                phone : '555-111-1224'
            }, {
                name  : 'Bart',
                email : 'bart@simpsons.com',
                phone : '555-222-1234'
            }, {
                name  : 'Homer',
                email : 'homer@simpsons.com',
                phone : '555-222-1244'
            }, {
                name  : 'Marge',
                email : 'marge@simpsons.com',
                phone : '555-222-1254'
            }]
        });
        var main = Ext.create('Ext.panel.Panel', {

        items: [{
            xtype: 'grid',
            title: 'Simpsons',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{
                text: 'Name',
                dataIndex: 'name'
            }, {
                text: 'Email',
                dataIndex: 'email',
                flex: 1
            }, {
                text: 'Phone',
                dataIndex: 'phone'
            }],
            height: Ext.getBody().getHeight(),
            width: '100%',
            plugins: [{
                ptype: 'rowwidget',
                widget: {
                    xtype: 'grid',
                    store: Ext.data.StoreManager.lookup('itemsStore'),
                    columns: [{
                        text: 'Item',
                        dataIndex: 'item',
                        flex: 1
                    }, {
                        text: 'Description',
                        dataIndex: 'desc',
                        flex: 2
                    }]
                }
            }]
        }]
        });
        /*var main = Ext.create('Ext.panel.Panel', {
            title: 'Employee Information',
            width: 600,
            bodyPadding: 10,
            defaults: {
                anchor: '100%',
                labelWidth: 100
            },
            items: [{
                xtype: 'textfield',
                name: 'email',
                fieldLabel: 'Email Address',
                vtype: 'email',
                msgTarget: 'side',
                allowBlank: false
            }, {
                xtype: 'fieldcontainer',
                fieldLabel: 'Availability',
                combineErrors: true,
                msgTarget : 'side',
                layout: 'hbox',
                defaults: {
                    flex: 1,
                    hideLabel: true
                },
                items: [{
                    xtype: 'datefield',
                    name: 'startDate',
                    fieldLabel: 'Start',
                    margin: '0 5 0 0',
                    allowBlank: false
                }, {
                    xtype     : 'datefield',
                    name      : 'endDate',
                    fieldLabel: 'End',
                    allowBlank: false
                }]
            }, {
                xtype: 'fieldset',
                title: 'Details',
                collapsible: true,
                defaults: {
                    labelWidth: 90,
                    anchor: '100%',
                    layout: 'hbox'
                },
                items: [{
                    xtype: 'fieldcontainer',
                    fieldLabel: 'Phone',
                    combineErrors: true,
                    msgTarget: 'under',
                    defaults: {
                        hideLabel: true,
                        enforceMaxLength: true,
                        maskRe: /[0-9.]/
                    },
                    items: [
                        {xtype: 'displayfield', value: '(', margin: '0 2 0 0'},
                        {xtype: 'textfield',    fieldLabel: 'Phone 1', name: 'phone-1', width: 45, allowBlank: false, maxLength: 3},
                        {xtype: 'displayfield', value: ')', margin: '0 5 0 2'},
                        {xtype: 'textfield',    fieldLabel: 'Phone 2', name: 'phone-2', width: 45, allowBlank: false, margin: '0 5 0 0', maxLength: 3},
                        {xtype: 'displayfield', value: '-'},
                        {xtype: 'textfield',    fieldLabel: 'Phone 3', name: 'phone-3', width: 60, allowBlank: false, margin: '0 0 0 5', maxLength: 4}
                    ]
                }, {
                    xtype: 'fieldcontainer',
                    fieldLabel: 'Time worked',
                    combineErrors: false,
                    defaults: {
                        hideLabel: true,
                        margin: '0 5 0 0'
                    },
                    items: [{
                       name : 'hours',
                       xtype: 'numberfield',
                       minValue: 0,
                       width: 95,
                       allowBlank: false
                   }, {
                       xtype: 'displayfield',
                       value: 'hours'
                   }, {
                       name : 'minutes',
                       xtype: 'numberfield',
                       minValue: 0,
                       width: 95,
                       allowBlank: false
                   }, {
                       xtype: 'displayfield',
                       value: 'mins'
                    }]
                }, {
                    xtype : 'fieldcontainer',
                    combineErrors: true,
                    msgTarget: 'side',
                    fieldLabel: 'Full Name',
                    defaults: {
                        hideLabel: true,
                        margin: '0 5 0 0'
                    },
                    items: [{
                        //the width of this field in the HBox layout is set directly
                        //the other 2 items are given flex: 1, so will share the rest of the space
                        width: 75,
                        xtype: 'combo',
                        queryMode: 'local',
                        value: 'mrs',
                        triggerAction: 'all',
                        forceSelection: true,
                        editable: false,
                        fieldLabel: 'Title',
                        name: 'title',
                        displayField: 'name',
                        valueField: 'value',
                        store: {
                            fields: ['name', 'value'],
                            data: [
                                {name : 'Mr',   value: 'mr'},
                                {name : 'Mrs',  value: 'mrs'},
                                {name : 'Miss', value: 'miss'}
                            ]
                        }
                    }, {
                        xtype: 'textfield',
                        flex : 1,
                        name : 'firstName',
                        fieldLabel: 'First',
                        allowBlank: false
                    }, {
                        xtype: 'textfield',
                        flex : 1,
                        name : 'lastName',
                        fieldLabel: 'Last',
                        allowBlank: false
                    }]
                }]
            }],

            buttons: [{
                text   : 'Load test data',
                handler: 'onLoadClick'
            }, {
                text   : 'Save',
                handler: 'onSaveClick'
            }, {
                text   : 'Reset',
                handler: 'onResetClick'
            }]
        });
        var viewPort = Ext.widget('viewport', {
            layout: 'fit',
            items: [
                main
            ]
        });*/

        var main = Ext.create('command.view.main.Main');
        var viewPort = Ext.widget('viewport', {
            layout: 'fit',
            items: [
                main
            ]
        });
        main.setVisible(false);

        Ext.Ajax.request({
            url: 'check_login/',
            success: function (response) {
                var resData = Ext.decode(response.responseText);
                if (resData.login) {
                    if (resData.reset_password) {
                        var m = Ext.create({
                            title: 'Reset password for user ' + resData.username,
                            xtype: 'reset_password'
                        });
                    } else {
                        var m = Ext.ComponentQuery.query('#main_panel')[0];
                        m.queryById('label_welcome_user').update('Welcome, ' + resData.username);
                        m.queryById('menu_button_admin').setVisible(resData.is_admin);
                        m.queryById('label_version').setVisible(resData.version);
                        m.queryById('label_version').update('Version: ' + resData.version);
                        command.version = resData.version;
                        m.setVisible(true);
                    }
                } else {
                    Ext.create({
                        xtype: 'login'
                    });
                }
            },
            failure: function (response) {
                Ext.Msg.alert('Server problem', 'Server Problem');
            }
        });
    }
});

Ext.define('command.LiveFilter', {
    extend: 'Ext.form.field.Text',
    xtype: 'command_livefilter',
    requires: [
        'Ext.form.field.Text'
    ],
    labelWidth:'auto',

    values: null,

    getValues: function() {
        return this.values;
    },

    listeners: {
        change: function (me, newValue, oldValue, eOpts) {
            var ws = command.current.ws;
            var grid = me.up('command_grid');
            var request = grid.getRequestObject(grid.command_read_operation);
            request.filter = newValue;
            request.page = 1;
            request.values = me.getValues();
            console.log(request);
            ws.stream(request.view).send(request);
        }
    }
});


Ext.define('command.Paging', {
    extend: 'Ext.toolbar.Paging',
    xtype: 'command_paging',
    requires: [
        'Ext.toolbar.Paging'
    ],

    values: null,

    getValues: function() {
        return this.values;
    },

    listeners: {
        beforechange: function(pagingtoolbar, page, eOpts) {
            var ws = command.current.ws;
            var grid = pagingtoolbar.up('command_grid');
            var request = grid.getRequestObject(grid.command_read_operation);
            request.page = page;
            request.values = this.getValues();
            ws.stream(request.view).send(request);
        }
    }
});

Ext.define('RequestMixin', {

    getRequestObject: function(operation) {
        var compendium = JSON.parse(localStorage.getItem("current_compendium"));
        var compendium_id = null;
        var data = {};
        var paging = this.down('command_paging');
        var filter = this.down('command_livefilter');
        var ordering = 'ASC';
        this.command_ordering != null ? ordering = this.command_ordering : ordering = 'ASC';
        var ordering_value = 'id';
        var page = 1;
        var page_size = 10;
        var filter_val = '';
        if (filter) {
            filter_val = filter.getValue();
        }
        if (paging) {
            page = paging.getPageData().currentPage;
        }
        if (this.store) {
            page_size = this.store.pageSize;
        }
        if (this.columns) {
            this.columns.forEach(function (c, i) {
                if (c.sortState) {
                    ordering = c.sortState;
                    ordering_value = c.dataIndex;
                }
            });
        }
        if (compendium) {
            compendium_id = compendium.id;
        }
        data = {
            'compendium_id': compendium_id,
            'operation': operation,
            'page': page,
            'page_size': page_size,
            'component_id': this.id,
            'view': this.command_view,
            'filter': filter_val,
            'ordering': ordering,
            'ordering_value': ordering_value
        };
        return data;
    }
});

Ext.define('command.Grid', {
    extend: 'Ext.grid.Panel',

    xtype: 'command_grid',

    requires: [
        'command.Paging',
        'command.LiveFilter'
        //'command.SelectAll'
    ],

    store: null,

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: null,

    command_read_operation: null,

    dockedItems: [{
        dock: 'top',
        xtype: 'toolbar',
        itemId: 'command_toptoolbar',
        items: [{
            xtype: 'command_paging',
            itemId: 'command_paging',
            displayInfo: true
        }, '->', {
            xtype: 'command_livefilter',
            fieldLabel: 'Filter',
            name: 'filter'
        }]
    }],

    initComponent: function() {
        this.callParent(arguments);
        this.headerCt.items.each(function(c){
            c.menuDisabled = true;
        });
    },

    listeners: {
        expand: function (p, eOpts ) {
            // Hack to prevent store to crash when reloaded without having focus
            p.getView().refresh();
        },
        headerclick: function(ct, column, e, t, eOpts) {
            var grid = ct.up('command_grid');
            if (!column.isCheckerHd) {
                var ws = command.current.ws;
                grid.store.loadData([], false);
                var operation = grid.command_read_operation;
                var request = grid.getRequestObject(operation);
                request.values = this.down('command_paging').getValues();
                ws.stream(request.view).send(request);
            }
        },
        afterrender: function ( me, eOpts ) {
            var paging = me.down('command_paging');
            paging.bindStore(me.store);
            //var selectall = me.down('command_selectall');
            var ws = command.current.ws;
            var operation = me.command_read_operation;
            var request = this.getRequestObject(operation);
            ws.listen();
            ws.demultiplex(request.view, function(action, stream) {
                if (action.request.operation == request.operation) {
                    if (action.data.task_running) {
                        me.setLoading(true);
                    } else {
                        me.setLoading(false);
                        if (me.store) {
                            me.store.getProxy().setData(action.data);
                            me.store.loadPage(action.request.page, {
                                start: 0
                            });
                        }
                    }
                }
                if (action.request.operation == 'refresh') {
                    ws.stream(request.view).send(request);
                }
            });
            ws.stream(request.view).send(request);
        },
        beforeshow: function ( me, eOpts ) {
            var ws = command.current.ws;
            var operation = me.command_read_operation;;
            var request = this.getRequestObject(operation);
            ws.stream(request.view).send(request);
        },
        render: function(grid) {
            var view=grid.getView();
            console.log(view.id);
            view.tip = Ext.create('Ext.tip.ToolTip', {
                dismissDelay: 0,
                target: grid.el,
                // this gets css query to identify the individual cells
                delegate: view.cellSelector + '.command_tooltip',
                listeners: {
                    beforeshow: function(tip) {
                        var column = view.getGridColumns()[tip.triggerElement.cellIndex];
                        var record = view.getRecord(tip.triggerElement.parentNode);
                        tip.update(record.get(column.dataIndex));
                    }
                }
            });
        },
        destroy: function(view) {
            delete view.tip; // Clean up this property on destroy.
        }
    }
});