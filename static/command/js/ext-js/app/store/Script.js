Ext.define('command.store.Script', {
    extend: 'Ext.data.Store',

    alias: 'store.script',
    model: 'command.model.Script',

    autoLoad: true,

    proxy: {
        type: 'memory',
        reader: {
            type: 'json',
            rootProperty: 'items'
        }
    }
});
