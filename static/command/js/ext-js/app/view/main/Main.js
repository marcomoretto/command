Ext.setGlyphFontFamily('FontAwesome');

Ext.define('command.view.main.Main', {
    extend: 'Ext.panel.Panel',
    requires: [
        'Ext.tab.Panel',
        'Ext.window.MessageBox',
        'Ext.panel.Panel',
        'Ext.layout.container.Fit',

        'command.view.option.MessageLog',

        'command.view.main.MainController',
        'command.view.main.MainModel',
        'command.view.admin.UserGroupManager',
        'command.view.admin.Compendia',
        'command.view.data_collection.experiment.Experiments',
        'command.view.data_collection.experiment.ParseExperiment'
        //'command.store.Compendium',
        //'command.view.data_collection.experiment.ImportExperimentPublic',
        //'command.view.data_collection.experiment.ParseExperiment',
        //'command.view.data_collection.experiment.Experiments'
    ],
    xtype: 'main',
    controller: 'main',
    itemId: 'main_panel',
    cls: 'command-header-title',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',
    autoHeight: true,
    bodyPadding: 5,
    tbar: {
        defaults: {
            xtype: 'button',
            scale: 'small'
        },
        overflowHandler: 'menu',
        items: [{
            text: 'Data collection',
            itemId: 'data_collection_menu_item',
            iconCls: null,
            glyph: 'xf019',
            listeners: {
                focus: {
                    fn: 'onMenuBeforeShow'
                },
                click: {
                    fn: 'onMenuBeforeShow'
                }
            },
            menu: {
                xtype: 'menu',
                plain: true,
                items: [{
                    text: 'Experiments',
                    itemId: 'experiments_menu_item',
                    iconCls: null,
                    glyph:'xf0c3',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/experiments',
                            glyph: 'xf0c3',
                            panel: 'experiments'
                        }
                    }
                    },
                    ' ',
                    {
                        text: 'Platforms',
                        itemId: 'platforms_menu_item',
                        iconCls: null,
                        glyph:'f21a',
                        listeners: {
                            click: {
                                fn: 'onAction',
                                hash: 'view/platform_manager',
                                glyph: 'xf12e',
                                panel: 'platform_manager'
                            }
                        }
                    }, {
                        text: 'Biological features',
                        glyph: 'xf06c',
                        iconCls: null,
                        listeners: {
                            click: {
                                fn: 'onAction',
                                hash: 'view/bio_feature',
                                glyph: 'f1fb',
                                panel: 'bio_feature'
                            }
                        }
                    }]
            }
        },{
            text: 'Options',
            iconCls: null,
            glyph: 'xf0ca',
            menu: {
                items: [{
                    text: 'Change compendium',
                    iconCls: null,
                    glyph: 'xf1c0',
                    menu: {
                        id: 'change_compendium_menu',
                        xtype: 'menu',
                        hideOnClick: true,
                        items: [{
                            emptyText: 'Select a compendium ...',
                            width: 200,
                            indent: true,
                            xtype: 'combobox',
                            store: Ext.create('command.store.Compendium'),
                            queryMode: 'local',
                            typeAhead: false,
                            displayField: 'compendium_name',
                            valueField: 'id',
                            editable: false,
                            listeners: {
                                select: 'onSelectCompendium',
                                focus: 'onFocusCompendium'
                            }
                        }]
                    }
                },'-',{
                    text: 'Message log',
                    glyph: 'f086',
                    iconCls: null,
                    displayText: 'Message log',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/message_log',
                            glyph: 'f086',
                            panel: 'message_log'
                        }
                    }
                }, '-', {
                    text: 'Export',
                    glyph: 'f062',
                    iconCls: null,
                    displayText: 'Export',
                    listeners: {
                        click: {
                            fn: 'exportRawData'
                        }
                    }
                }]
            }
        },{
            text: 'Admin',
            iconCls: null,
            itemId: 'menu_button_admin',
            glyph: 'xf0f0',
            menu: {
                items: [{
                    text: 'User/Group manager',
                    iconCls: null,
                    glyph:'xf0c0',
                    displayText: 'User manager',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/user_group_manager',
                            glyph: 'xf0c0',
                            panel: 'user_group_manager'
                        }
                    }
                },{
                    text: 'Compendium manager',
                    iconCls: null,
                    glyph: 'xf00a',
                    displayText: 'Compendium manager',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/compendia_manager',
                            glyph: 'xf00a',
                            panel: 'compendia_manager'
                        }
                    }
                },'-', {
                    text: 'Options',
                    iconCls: null,
                    glyph: 'xf0ca',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/admin_options',
                            glyph: 'xf085',
                            panel: 'admin_options'
                        }
                    }
                }]
            }
        },{
            xtype: 'tbfill'
        },{
            xtype: 'panel',
            itemId: 'label_version',
            html: 'Version: ',
            width: '200'
        }, {
            xtype: 'tbfill'
        }, {
            xtype: 'panel',
            itemId: 'label_welcome_user',
            html: 'Welcome, User',
            width: '200'
        },{
            xtype: 'button',
            html: 'Logout',
            glyph: 'xf08b',
            listeners: {
                click: 'onLogoutClick'
            }
        }]
    },
    items: [{
        title: null,
        titleAlign: 'left',
        region: 'top',
        itemId: 'main_tab_panel',
        xtype: 'tabpanel',
        plain: false,
        defaults: {
            bodyPadding: 5,
            scrollable: true,
            border: false
        },
        tabPosition: 'left',
        tabRotation: 0,
        bodyPadding: 0,
        tabBar: {
            border: false
        },
        items:[
            //
        ],
        listeners: {
            tabchange: 'onTabChange'
        }
    }],

    listeners: {
        afterrender: function ( me, eOpts ) {
            var compendium = JSON.parse(localStorage.getItem("current_compendium"));
            if (!compendium) {
                me.down('#data_collection_menu_item').disable();
            }
        }
    },

    initComponent: function() {
        this.callParent();
    }
});