Ext.define('command.view.data_collection.platform.BioFeatureReportersDetails', {
    extend: 'command.Grid',
    xtype: 'bio_feature_reporters_details',
    title: null,

    requires: [
        'Ext.panel.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    store: null,

    alias: 'widget.bio_feature_reporters_details',

    itemId: 'bio_feature_reporters_details',

    reference: 'bio_feature_reporters_details',

    viewModel: {},

    command_view: 'bio_feature_reporter',

    command_read_operation: 'read_bio_feature_reporter',

    controller: 'bio_feature_reporters_details_controller',

    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id'
    }, {
        text: 'Name',
        flex: 2,
        sortable: true,
        dataIndex: 'name'
    }, {
        text: 'Description',
        flex: 2,
        sortable: true,
        dataIndex: 'description'
    }],

    listeners: {
        afterrender: 'onPlatformBioFeatureReporterAfterRender'
    },

    initComponent: function() {
        this.store = Ext.create('command.store.BioFeatureReporter');
        this.events.afterrender.removeListener(this.events.afterrender.listeners[0], 'self', 0); // remove default event listener
        this.events.beforeshow.removeListener(this.events.beforeshow.listeners[0], 'self', 0); // remove default event listener
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.platform.BioFeatureReporters', {
    extend: 'Ext.window.Window',
    xtype: 'window_bio_feature_reporter',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'bio_feature_reporter',

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
        xtype: 'bio_feature_reporters_details',
        flex: 1
    }]
});