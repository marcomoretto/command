Ext.define('command.view.data_collection.experiment.ParseExperimentPreviewRawDataController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.parse_experiment_preview_raw_data_controller',
    
    onRawDataAfterRender: function ( me, eOpts ) {
        var win = me.up('window_parse_experiment_preview_raw_data');
        var paging = me.down('command_paging');
        var operation = 'read_parse_experiment_preview_raw_data';
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
    }
});