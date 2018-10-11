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
            /*listeners: {
                click: 'onUpdateGroup'
            },*/
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
            /*listeners: {
                click: 'onDeleteGroup'
            },*/
            bind: {
                disabled: '{!available_ontologies.selection}'
            }
        }
    ],

    listeners: {
        afterrender: function (me, eOpts) {

        }
    },

    initComponent: function() {
        this.store = Ext.create('command.store.Ontologies');
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

Ext.define('command.view.annotation.ontologies.D3', {
    extend: 'Ext.panel.Panel',

    xtype: 'cy_ontology',

    alias: 'widget.cy_ontology',

    itemId: 'cy_ontology',

    reference: 'cy_ontology',

    controller: 'ontologies_controller',

    listeners: {
        afterrender: 'CyOntologyAfterRender'
    },

    bodyCls: 'cy',

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
            margin: '5 0 0 0',
            flex: 3
        },
        {
            xtype: 'panel',
            title: 'Current ontology',
            collapsible: false,
            region: 'center',
            margin: '5 0 0 0',
            flex: 7,
            items: [{
                xtype: 'cy_ontology'
            }]
        }
    ],

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});