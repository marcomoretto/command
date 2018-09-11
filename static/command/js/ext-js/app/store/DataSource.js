Ext.define('command.store.DataSource', {
    extend: 'Ext.data.Store',

    alias: 'store.data_source',
    model: 'command.model.DataSource',

    autoLoad: true,

    proxy: {
        type: 'memory',
        reader: {
            type: 'json',
            rootProperty: 'items'
        }
    }
});
