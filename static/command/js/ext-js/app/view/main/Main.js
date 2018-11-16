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
            text: 'Annotation',
            itemId: 'annotation_menu_item',
            iconCls: null,
            glyph: 'xf02b',
            menu: {
                items: [{
                    text: 'Biological features',
                    glyph: 'xf06c',
                    iconCls: null,
                    displayText: 'Biological features',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/bio_feature_annotation',
                            glyph: 'xf06c',
                            panel: 'bio_feature_annotation'
                        }
                    }
                }, {
                    text: 'Samples',
                    glyph: 'f1fb',
                    iconCls: null,
                    displayText: 'Samples',
                    disabled: true,
                    /*listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/message_log',
                            glyph: 'f086',
                            panel: 'message_log'
                        }
                    }*/
                }, '-', {
                    text: 'Ontologies',
                    glyph: 'f0e8',
                    iconCls: null,
                    displayText: 'Ontologies',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/ontologies',
                            glyph: 'f0e8',
                            panel: 'ontologies'
                        }
                    }
                }]
            }
        },{
            text: 'Normalization',
            itemId: 'normalization_menu_item',
            iconCls: null,
            glyph: 'f1fe',
            menu: {
                items: [{
                    text: 'Normalization manager',
                    glyph: 'f1fe',
                    iconCls: null,
                    displayText: 'Normalization manager',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/normalization_manager',
                            glyph: 'f1fe',
                            panel: 'normalization_manager'
                        }
                    }
                }, {
                    text: 'Jupyter notebook',
                    glyph: 'f12b',
                    iconCls: null,
                    displayText: 'Jupyter notebook',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/jupyter_notebook',
                            glyph: 'f12b',
                            panel: 'jupyter_notebook'
}
                     }
                }]
            }
        },/*{
            text: 'Test',
            itemId: 'test_menu_item',
            iconCls: null,
            glyph: 'xf11b',
            listeners: {
                click: {
                    fn: 'onAction',
                    hash: 'view/test',
                    glyph: 'xf11b',
                    panel: 'test'
                }
            }
        },*/{
            text: 'Options',
            iconCls: null,
            glyph: 'xf142',
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
                    glyph: 'xf0ad',
                    displayText: 'Compendium manager',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/compendia_manager',
                            glyph: 'xf0ad',
                            panel: 'compendia_manager'
                        }
                    }
                },'-', {
                    text: 'Options',
                    iconCls: null,
                    glyph: 'xf142',
                    listeners: {
                        click: {
                            fn: 'onAction',
                            hash: 'view/admin_options',
                            glyph: 'xf142',
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
        afterrender: 'mainAfterRender'
    },

    initComponent: function() {
        this.callParent();
    }
});