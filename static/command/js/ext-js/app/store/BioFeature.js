Ext.define('command.store.BioFeature', {
    extend: 'Ext.data.Store',

    alias: 'store.bio_feature',
    model: 'command.model.BioFeature',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'bio_feature',
            totalProperty: 'total'
        }
    }

});
