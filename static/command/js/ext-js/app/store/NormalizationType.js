Ext.define('command.store.NormalizationType', {
    extend: 'Ext.data.Store',

    alias: 'store.data_source',
    model: 'command.model.NormalizationType',

    autoLoad: true,

    proxy: {
        type: 'memory',
        reader: {
            type: 'json',
            rootProperty: 'items'
        }
    }
});
