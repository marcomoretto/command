Ext.define('command.store.ExperimentFiles', {
    extend: 'Ext.data.Store',

    alias: 'store.experiment_files',
    model: 'command.model.ExperimentFiles',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'files',
            totalProperty: 'total'
        }
    }
});