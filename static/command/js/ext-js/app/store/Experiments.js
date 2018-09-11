Ext.define('command.store.Experiments', {
    extend: 'Ext.data.Store',

    alias: 'store.experiments',
    model: 'command.model.Experiments',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    groupField: 'status',

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'experiments',
            totalProperty: 'total'
        }
    }

});
