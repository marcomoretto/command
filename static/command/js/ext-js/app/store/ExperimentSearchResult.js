Ext.define('command.store.ExperimentSearchResult', {
    extend: 'Ext.data.Store',

    alias: 'store.experiment_search_result',
    model: 'command.model.ExperimentSearchResult',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'experiments',
            totalProperty: 'total'
        }
    }

});
