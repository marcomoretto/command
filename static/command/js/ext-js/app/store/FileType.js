Ext.define('command.store.FileType', {
    extend: 'Ext.data.Store',

    alias: 'store.data_source',
    model: 'command.model.FileType',

    autoLoad: true,

    proxy: {
        type: 'memory',
        reader: {
            type: 'json',
            rootProperty: 'items'
        }
    }
});
