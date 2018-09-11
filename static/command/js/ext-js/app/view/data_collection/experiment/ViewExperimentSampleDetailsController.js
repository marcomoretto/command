Ext.define('command.view.data_collection.experiment.ViewExperimentSampleDetailsController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.view_experiment_sample_details_controller',

    onRawDataAfterRender: function ( me, eOpts ) {
        var win = me.up('window_view_experiment_sample_raw_data');
        var paging = me.down('command_paging');
        var operation = 'read_experiment_sample_raw_data';
        var ws = command.current.ws;
        var request = me.getRequestObject(operation);
        request.values = win.sample;
        paging.values = win.sample;
        me.down('command_livefilter').values = win.sample;
        paging.bindStore(me.store);
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                if (me.store) {
                    me.store.getProxy().setData(action.data);
                    me.store.loadPage(action.request.page, {
                        start: 0
                    });
                }
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);
    },

    onViewExperimentDetailsDoubleClick: function(dv, record, item, index, e) {
        var win = Ext.create({
            xtype: 'window_view_experiment_sample_raw_data',
            title: 'Raw data for sample ' + record.data.sample_name,
            sample: record.data
        });
    },

    onViewExperimentDetailsAfterRender: function ( me, eOpts ) {
        var paging = me.down('command_paging');
        var panel = me;
        var operation = 'read_sample_details';
        var ws = command.current.ws;
        var request = me.getRequestObject(operation);
        request.values = panel.experiment;
        paging.values = panel.experiment;
        me.down('command_livefilter').values = panel.experiment;
        paging.bindStore(me.store);
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                me.store.getProxy().setData(action.data);
                me.store.loadPage(action.request.page, {
                    start: 0
                });
                me.setLoading(false);
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);
    }
});