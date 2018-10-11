Ext.define('command.view.normalization.jupyter_notebook.NotebookTree', {
    extend: 'Ext.tree.Panel',
    xtype: 'notebook_tree',
    title: false,
    rootVisible: true,
    store: null,
    title: 'Notebooks',

    requires: [
        'command.model.ScriptTree'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    alias: 'widget.notebook_tree',

    itemId: 'notebook_tree',

    reference: 'notebook_tree',

    viewModel: {},

    command_view: 'jupyter_notebook',

    controller: 'jupyter_notebook',

    dockedItems: [{
        xtype: 'toolbar',
        dock: 'bottom',
        overflowHandler: 'menu',
        items: [{
            text: null,
            xtype: 'button',
            itemId: 'create_button',
            tooltip: {
                text: 'Create new'
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            disabled: false,
            menu: {
                xtype: 'menu',
                forceLayout: true,
                items: [{
                    text: 'Jupyter notebook',
                    scale: 'medium',
                    tooltip: {
                        text: 'Jupyter notebook'
                    },
                    glyph: 'xf15b',
                    listeners: {
                        click: 'onCreateNotebook'
                    },
                }, {
                    text: 'Folder',
                    scale: 'medium',
                    tooltip: {
                        text: 'Folder'
                    },
                    glyph: 'xf07c',
                    listeners: {
                        click: 'onCreateFolder'
                    }
                }]
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            itemId: 'update_button',
            tooltip: {
                text: 'Update name'
            },
            glyph: 'xf044',
            scale: 'medium',
            listeners: {
                click: 'onUpdateNotebook'
            },
            bind: {
                disabled: '{!notebook_tree.selection}'
            }
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            itemId: 'delete_button',
            tooltip: {
                text: 'Delete'
            },
            glyph: 'xf056',
            scale: 'medium',
            listeners: {
                click: 'onDeleteNotebook'
            },
            bind: {
                disabled: '{!notebook_tree.selection}'
            }
        }]
    }, {
        dock: 'top',
        xtype: 'toolbar',
        items: [{
            xtype: 'command_livefilter',
            fieldLabel: 'Filter',
            name: 'filter',
            command_operation: 'read_notebook_tree',
            initComponent: function() {
                this.clearListeners();
                this.on('change', function (me, newValue, oldValue, eOpts) {
                    var ws = command.current.ws;
                    var panel = me.findParentByType('[xtype="notebook_tree"]');
                    var request = panel.getRequestObject(me.command_operation);
                    ws.stream(request.view).send(request);
                });
                this.callParent();
            }
        }, '->', {
            xtype: 'button',
            text: null,
            iconCls: null,
            itemId: 'expand_all_button',
            tooltip: {
                text: 'Expand all'
            },
            glyph: 'xf065',
            scale: 'small',
            listeners: {
                click: 'onExpandCollapseAll'
            },
            hidden: false
        }, {
            xtype: 'button',
            text: null,
            iconCls: null,
            itemId: 'collapse_all_button',
            tooltip: {
                text: 'Collapse all'
            },
            glyph: 'xf066',
            scale: 'small',
            listeners: {
                click: 'onExpandCollapseAll'
            },
            hidden: true
        }]
    }],

    listeners: {
        //beforeselect: 'onSelectTreeItem',
        afterrender: 'onNotebookTreeAfterRender',
        itemdblclick: 'onNotebookDoubleClick'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.ScriptTree');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.normalization.jupyter_notebook.Notebook', {
    extend: 'Ext.Component',

    xtype: 'notebook',

    requires: [
        'Ext.panel.Panel',
        'command.view.normalization.jupyter_notebook.JupyterNotebookController'
    ],

    controller: 'jupyter_notebook',

    store: null,

    alias: 'widget.notebook',

    itemId: 'notebook',

    reference: 'notebook',

    autoEl : {
        tag : "iframe",
        src : ""
    },

    listeners: {
        afterrender: 'onJupyterNotebookAfterRenderer'
    },

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.normalization.jupyter_notebook.JupyterNotebook', {
    extend: 'Ext.panel.Panel',

    xtype: 'jupyter_notebook',

    title: 'Jupyter Notebook',

    requires: [
        'Ext.panel.Panel',
        'command.view.normalization.jupyter_notebook.JupyterNotebookController'
    ],

    controller: 'jupyter_notebook',

    store: null,

    alias: 'widget.jupyter_notebook',

    itemId: 'jupyter_notebook',

    reference: 'jupyter_notebook',

    layout: 'border',
    width: 500,
    height: 400,

    bodyBorder: false,

    defaults: {
        collapsible: true,
        split: true,
        bodyPadding: 10,
        scrollable: true,
        border: false
    },

    items:[{
            xtype: 'notebook_tree',
            region:'west',
            floatable: false,
            margin: '5 0 0 0',
            flex: 2
        },
        {
            xtype: 'notebook',
            bodyBorder: false,
            collapsible: false,
            region: 'center',
            margin: '5 0 0 0',
            flex: 5
    }],

    listeners: {
        //afterrender: 'onJupyterNotebookAfterRenderer'
    },

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});