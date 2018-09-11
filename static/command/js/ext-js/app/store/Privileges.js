Ext.define('command.store.Privileges', {
    extend: 'Ext.data.Store',

    alias: 'store.privileges',
    model: 'command.model.Privileges',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    proxy: {
        type: 'memory',
        reader: {
            type: 'json',
            rootProperty: 'privileges',
            totalProperty: 'total'
        }
    }
});
