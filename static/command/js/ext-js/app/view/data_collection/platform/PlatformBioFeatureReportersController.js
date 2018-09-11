Ext.define('command.view.data_collection.platform.microarray.ViewPlatformBioFeatureReportersController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.bio_feature_reporters_details_controller',

    onPlatformBioFeatureReporterAfterRender: function (me) {
        var win = me.up('window_bio_feature_reporter');
        win.platform.platform_type.bio_features_reporter_fields.forEach(function(e) {
            me.headerCt.insert(
              me.columns.length,
              Ext.create('Ext.grid.column.Column', {
                  text: e.description,
                  dataIndex: e.name,
                  flex: 2,
                  sortable: true,
                  hidden: false
              })
            );
        });
        me.getView().refresh();
        var paging = me.down('command_paging');
        var operation = 'read_bio_feature_reporter';
        var ws = command.current.ws;
        var request = me.getRequestObject(operation);
        console.log(win.platform);
        request.values = win.platform;
        paging.values = win.platform;
        me.down('command_livefilter').values = win.platform;
        paging.bindStore(me.store);
        ws.listen();
        ws.demultiplex(request.view, function(action, stream) {
            if (action.request.operation == request.operation) {
                me.store.getProxy().setData(action.data);
                me.store.loadPage(action.request.page, {
                    start: 0
                });
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        ws.stream(request.view).send(request);
        
    }
});
