Ext.define('command.store.RawData', {
    extend: 'Ext.data.Store',

    alias: 'store.raw_data',
    model: 'command.model.RawData',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'raw_data',
            totalProperty: 'total'
        }
    }

});
