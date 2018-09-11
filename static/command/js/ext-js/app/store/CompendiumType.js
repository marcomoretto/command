Ext.define('command.store.CompendiumType', {
    extend: 'Ext.data.Store',

    alias: 'store.compendium_type',
    model: 'command.model.CompendiumType',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'compendium_types',
            totalProperty: 'total'
        }
    }
});
