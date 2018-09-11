Ext.define('command.store.Compendium', {
    extend: 'Ext.data.Store',

    alias: 'store.compendium',
    model: 'command.model.Compendium',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'compendia',
            totalProperty: 'total'
        }
    }
});
