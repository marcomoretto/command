Ext.define('command.store.Normalizations', {
    extend: 'Ext.data.Store',

    alias: 'store.normalizations',
    model: 'command.model.Normalizations',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'normalizations',
            totalProperty: 'total'
        }
    }
});
