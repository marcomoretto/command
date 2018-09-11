Ext.define('command.view.data_collection.sample.ParseExperimentPreviewRawData', {
    extend: 'command.Grid',
    xtype: 'parse_experiment_preview_raw_data',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.parse_experiment_preview_raw_data',

    itemId: 'parse_experiment_preview_raw_data',

    reference: 'parse_experiment_preview_raw_data',

    viewModel: {},

    command_view: 'parse_experiment_raw_data',

    command_read_operation: 'read_parse_experiment_preview_raw_data',

    controller: 'parse_experiment_preview_raw_data_controller',

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Bio Feature Reporter Name',
        flex: 2,
        sortable: true,
        dataIndex: 'bio_feature_reporter_name'
    }, {
        text: 'Value',
        flex: 2,
        sortable: true,
        dataIndex: 'value'
    }],

    listeners: {
        afterrender: 'onRawDataAfterRender'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.RawData');
        this.events.afterrender.removeListener(this.events.afterrender.listeners[0], 'self', 0); // remove default event listener
        this.events.beforeshow.removeListener(this.events.beforeshow.listeners[0], 'self', 0); // remove default event listener
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.experiment.ParseExperimentPreviewRawData', {
    extend: 'Ext.window.Window',
    xtype: 'window_parse_experiment_preview_raw_data',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'parse_experiment_raw_data',

    //controller: '',

    bodyPadding: 10,
    title: null,
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 900,
    height: 700,
    constrain: true,

    layout: 'border',
    bodyBorder: false,

    layout: {
        type: 'vbox',
        pack: 'start',
        align: 'stretch'
    },

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [{
        xtype: 'parse_experiment_preview_raw_data',
        flex: 1
    }]
});