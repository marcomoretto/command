Ext.define('command.view.VanishingConfirmMessage', {
    extend: 'Ext.window.Window',
    xtype: 'vanishing_confirm_message',
    border: false,
    resizable: false,
    draggable: false,
    closable: false,
    layout: {
        type: 'vbox',
        align: 'center',
        pack: 'center'
    },
    autoWidth: true,
    autoHeight: true,

    width: 200,

    setMessage: function (message) {
        this.add({
            border: false,
            frame: false,
            html: '<b>' + message + '</b>'
        });
    },

    listeners:{
        show: function(win) {
            setTimeout(function() {
                win.destroy()
            }, 1200);
        },
        scope: this
    }
});

Ext.define('command.view.data_collection.experiment.ace_editor', {
    extend: 'Ext.Component',//Extending the TextField
    xtype: 'ace_editor',
    itemId: 'ace_editor',

    config: {
        showPrintMargin: false,
        fontSize: '14px'
    },
    autoEl: {
        tag: 'div',
        cls: 'ace_editor ace-eclipse',
        style: 'position:relative;'
    },
    script_filename: '',

    constructor: function (cnfg) {
        this.callParent(arguments);//Calling the parent class constructor
        this.initConfig(cnfg);//Initializing the component
        this.on('resize', this.editorResize);//Associating a new defined method with an event
    },

    onRender: function () {
        this.callParent(arguments);

        this.editorObject = ace.edit(this.el.dom.id);
        this.editorObject.setTheme("ace/theme/eclipse");
        this.editorObject.getSession().setMode("ace/mode/python");
        this.editorObject.setShowPrintMargin(this.showPrintMargin);
        this.editorObject.setFontSize(this.fontSize);
    },

    editorResize: function () {
        this.editorObject.resize();
    },

    setFontSize: function (value) {
        this.fontSize = value;
        if (this.editorObject)
            this.editorObject.setFontSize(value);
    },

    setShowPrintMargin: function (value) {
        this.showPrintMargin = value;
        if (this.editorObject)
            this.editorObject.setShowPrintMargin(value);
    },

    setValue: function (value) {
        this.editorObject.getSession().setValue(value);
    },

    getValue: function () {
        return this.editorObject.getSession().getValue();
    },

    setScriptName: function (value) {
        this.script_filename = value;
    },

    getScriptName: function () {
        return this.script_filename;
    }
});

Ext.define('command.view.data_collection.experiment.ace_python_editor', {
    extend: 'Ext.panel.Panel',

    xtype: 'ace_python_editor',

    requires: [
        'command.model.ScriptTree',
        'command.view.data_collection.experiment.ParseExperimentEditorController'
    ],

    controller: 'parse_experiment_editor_controller',

    frame: true,

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    alias: 'widget.ace_python_editor',

    itemId: 'ace_python_editor',

    reference: 'ace_python_editor',

    viewModel: {},

    command_view: 'script_tree',

    items: [{
        xtype: 'ace_editor',
        frame: true,
        disabled: true,
        border: 5,
        style: {
            borderColor: 'red',
            borderStyle: 'solid'
        }
    }],

    listeners: {
        afterrender: function (panel) {
            panel.el.on('keydown', panel.controller.editorKeyHandler);
        }
    },

    dockedItems: [{
        dock: 'bottom',
        xtype: 'toolbar',
        border: 5,
        style: {
            borderColor: 'red',
            borderStyle: 'solid'
        },
        items: ['->', {
            text: null,
            xtype: 'button',
            itemId: 'save_script_button',
            tooltip: {
                text: 'Save script'
            },
            iconCls: null,
            glyph: 'xf0c7',
            scale: 'medium',
            listeners: {
                click: 'onSaveScript'
            },
            disabled: true
        }]
    }]
});

Ext.define('command.view.data_collection.experiment.ScriptTree', {
    extend: 'Ext.tree.Panel',
    xtype: 'script_tree',
    title: false,
    rootVisible: false,
    store: null,

    requires: [
        'command.model.ScriptTree',
        'command.view.data_collection.experiment.ParseExperimentEditorController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    alias: 'widget.script_tree',

    itemId: 'script_tree',

    reference: 'script_tree',

    viewModel: {},

    command_view: 'script_tree',

    controller: 'parse_experiment_editor_controller',

    dockedItems: [{
        xtype: 'toolbar',
        dock: 'bottom',
        overflowHandler: 'menu',
        items: [{
            text: null,
            xtype: 'button',
            itemId: 'create_button',
            tooltip: {
                text: 'Create new Python script file'
            },
            iconCls: null,
            glyph: 'xf055',
            scale: 'medium',
            listeners: {
                click: 'onCreate'
            },
            disabled: true
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
                click: 'onUpdate'
            },
            disabled: true
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
                click: 'onDelete'
            },
            disabled: true
        }]
    }, {
        dock: 'top',
        xtype: 'toolbar',
        items: [{
            xtype: 'command_livefilter',
            fieldLabel: 'Filter',
            name: 'filter',
            command_operation: 'read_script_tree',
            initComponent: function() {
                this.clearListeners();
                this.on('change', function (me, newValue, oldValue, eOpts) {
                    var ws = command.current.ws;
                    var panel = me.findParentByType('[xtype="script_tree"]');
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
        beforeselect: 'onSelectTreeItem',
        afterrender: 'onScriptTreeAfterRender'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.ScriptTree');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.experiment.PythonEditor', {
    extend: 'Ext.panel.Panel',

    xtype: 'python_editor',

    itemId: 'python_editor',

    title: 'Python editor',

    requires: [
        'Ext.panel.Panel',
        'Ext.tree.Panel',
        'Ext.tree.Column'
    ],

    layout: {
        type: 'hbox',
        pack: 'start',
        align: 'stretch'
    },

    bodyPadding: 5,

    defaults: {
        frame: true,
        bodyPadding: 0
    },

    items: [{
        xtype: 'script_tree',
        title: 'Script files',
        flex: 1,
        margin: '0 10 0 0'
    }, {
        xtype: 'ace_python_editor',
        title: 'Script editor',
        flex: 2,
        layout: 'fit',
        margin: '0 10 0 0'
    }
    ]
});