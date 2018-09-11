Ext.define('command.store.ExperimentPlatformsFiles', {
    extend: 'Ext.data.Store',

    alias: 'store.experiment_files',
    model: 'command.model.ExperimentPlatformsFiles',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'platforms',
            totalProperty: 'total'
        }
    }
});