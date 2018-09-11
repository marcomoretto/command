Ext.define('command.store.ExperimentSamplesFiles', {
    extend: 'Ext.data.Store',

    alias: 'store.experiment_files',
    model: 'command.model.ExperimentSamplesFiles',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'samples',
            totalProperty: 'total'
        }
    }
});