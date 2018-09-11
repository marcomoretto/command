Ext.define('command.store.RelatedPlatforms', {
    extend: 'Ext.data.Store',

    alias: 'store.related_platforms',
    model: 'command.model.Platforms',

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
