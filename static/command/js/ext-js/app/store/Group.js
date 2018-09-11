Ext.define('command.store.Group', {
    extend: 'Ext.data.Store',

    alias: 'store.group',
    model: 'command.model.Group',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'groups',
            totalProperty: 'total'
        }
    }
});
