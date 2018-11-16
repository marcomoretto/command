Ext.define('command.store.Ontologies', {
    extend: 'Ext.data.Store',

    alias: 'store.ontologies',
    model: 'command.model.Ontologies',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'ontologies',
            totalProperty: 'total'
        }
    }
});
