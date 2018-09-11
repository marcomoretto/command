Ext.define('command.view.data_collection.platform.microarray.MapPlatformController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.map_platform_controller',

    onCellClickAlignment: function(me, td, cellIndex, record, tr, rowIndex, e, eOpts) {
        var form = me.up('window').down('#alignment_form').getForm();
        form.setValues(record.data.alignment_params);
    },

    onCellClickFilter: function(me, td, cellIndex, record, tr, rowIndex, e, eOpts) {
        var form = me.up('window').down('#filter_form').getForm();
        form.setValues(record.data.filter_params);
    },

    onRunFilterAlignment: function(me, idx) {
        var request = me.up('grid').getRequestObject('filter_alignment');
        var item = me.store.data.items[idx];
        request.values = JSON.stringify({
            platform_id: me.up('window').platform.id,
            alignment_id: item.id,
            filter_params: me.up('window').down('#filter_form').getForm().getValues()
        });
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onImportMapping: function(me, idx) {
        var win = me.up('window_map_microarray_platform');
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        var request = me.up('#map_platform_results').getRequestObject('import_mapping');
        var item = me.store.data.items[idx];
        request.values = JSON.stringify({
            platform_id: me.up('window').platform.id,
            filter_id: item.id,
            alignment_id: item.data.alignment_id
        });
        Ext.MessageBox.show({
            title: 'Import mapping for platform ' + win.platform.platform_access_id,
            msg: 'You are about to bind each ' + comp.compendium_type.bio_feature_name + ' of this compendium to one or more ' +
                win.platform.platform_type.bio_feature_reporter_name + ' of platform ' + win.platform.platform_access_id + '. Do you want to continue?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    })
                }
            }
        });
    },

    onRemoveFilter: function(me, idx) {
        var request = me.up('#map_platform_results').getRequestObject('delete_alignment_filter');
        var item = me.store.data.items[idx];
        request.values = JSON.stringify({
            platform_id: me.up('window').platform.id,
            filter_id: item.id,
            alignment_id: item.data.alignment_id,
            operations: ['import_mapping', 'filter_alignment']
        });
        Ext.MessageBox.show({
            title: 'Delete filter',
            msg: 'Are you sure you want to delete this alignment filter?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    })
                }
            }
        });
    },

    onRemoveAlignment: function(me, idx) {
        var request = me.up('grid').getRequestObject('delete_alignment');
        var item = me.store.data.items[idx];
        request.values = JSON.stringify({
            platform_id: me.up('window').platform.id,
            alignment_id: item.id
        });
        Ext.MessageBox.show({
            title: 'Delete alignment',
            msg: 'Are you sure you want to delete this alignment?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    })
                }
            }
        });
    },
    
    onRunAlignment: function(me) {
        var values = me.up('#alignment_form').getForm().getValues();
        var request = me.up('map_platform_parameters').getRequestObject('run_alignment');
        request.values = values;
        request.values.platform_id = me.up('window').platform.id;
        request.values = JSON.stringify(request.values);
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onMapPlatformToBioFeatureAfterRender: function (me) {
        var win = me.up('window_map_microarray_platform');
        var paging = me.down('command_paging');
        var operation = 'read_mapping';
        var ws = command.current.ws;
        var request = me.getRequestObject(operation);
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
