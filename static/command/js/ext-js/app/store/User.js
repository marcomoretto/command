Ext.define('command.store.User', {
    extend: 'Ext.data.ArrayStore',

    requires: [
        'command.model.User'
    ],

    alias: 'store.user',
    model: 'command.model.User',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'users',
            totalProperty: 'total'
        }
    }
});
