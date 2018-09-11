Ext.define('command.store.PlatformToBioFeatureMapping', {
    extend: 'Ext.data.Store',

    alias: 'store.platform_to_bio_feature_mapping',
    model: 'command.model.PlatformToBioFeatureMapping',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'mappings',
            totalProperty: 'total'
        }
    }

});
