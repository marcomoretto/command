Ext.define('command.store.NormalizationExperiments', {
    extend: 'Ext.data.Store',

    alias: 'store.normalization_experiments',
    model: 'command.model.NormalizationExperiments',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'normalization_experiments',
            totalProperty: 'total'
        }
    }
});
