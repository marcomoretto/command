Ext.define('command.store.BioFeatureReporter', {
    extend: 'Ext.data.Store',

    alias: 'store.bio_feature_reporter',
    model: 'command.model.BioFeatureReporter',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'bio_feature_reporter',
            totalProperty: 'total'
        }
    }

});
