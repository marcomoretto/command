Ext.define('command.view.data_collection.sample.ViewExperimentSampleRawData', {
    extend: 'command.Grid',
    xtype: 'view_experiment_sample_raw_data',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.view_experiment_sample_raw_data',

    itemId: 'view_experiment_sample_raw_data',

    reference: 'view_experiment_sample_raw_data',

    viewModel: {},

    command_view: 'experiments',

    command_read_operation: 'read_experiment_sample_raw_data',

    controller: 'view_experiment_sample_details_controller',

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

Ext.define('command.view.data_collection.experiment.ViewExperimentSampleRawData', {
    extend: 'Ext.window.Window',
    xtype: 'window_view_experiment_sample_raw_data',

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
        xtype: 'view_experiment_sample_raw_data',
        flex: 1
    }]
});

Ext.define('command.view.data_collection.experiment.ViewExperimentSampleDetails', {
    extend: 'command.Grid',
    xtype: 'view_experiment_sample_details',

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.view_experiment_sample_details',

    itemId: 'view_experiment_sample_details',

    reference: 'view_experiment_sample_details',

    viewModel: {},

    command_view: 'experiments',

    command_read_operation: 'read_sample_details',

    controller: 'view_experiment_sample_details_controller',

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Name',
        flex: 2,
        sortable: true,
        dataIndex: 'sample_name'
    }, {
        text: 'Platform',
        flex: 2,
        sortable: true,
        dataIndex: 'platform',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            return record.data.platform.platform_access_id;
        }
    }, {
        text: 'Reporter platform',
        flex: 2,
        sortable: true,
        dataIndex: 'reporter_platform',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            return record.data.reporter_platform.platform_access_id;
        }
    }, {
        text: 'Description',
        flex: 5,
        sortable: true,
        dataIndex: 'description'
    }],

    listeners: {
        afterrender: 'onViewExperimentDetailsAfterRender',
        itemdblclick: 'onViewExperimentDetailsDoubleClick'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.ExperimentSamplesFiles');
        this.events.afterrender.removeListener(this.events.afterrender.listeners[0], 'self', 0); // remove default event listener
        this.events.beforeshow.removeListener(this.events.beforeshow.listeners[0], 'self', 0); // remove default event listener
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});
