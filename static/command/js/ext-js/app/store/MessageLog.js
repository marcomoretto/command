Ext.define('command.store.MessageLog', {
    extend: 'Ext.data.Store',

    alias: 'store.message_log',
    model: 'command.model.MessageLog',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    groupField: 'source',

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'messages',
            totalProperty: 'total'
        }
    }
});
