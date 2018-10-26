Ext.define('command.store.OntologyNodes', {
    extend: 'Ext.data.Store',

    alias: 'store.ontology_nodes',
    model: 'command.model.OntologyNodes',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'nodes',
            totalProperty: 'total'
        }
    }
});
