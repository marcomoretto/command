Ext.define('command.store.NormalizationDesignGroup', {
    extend: 'Ext.data.Store',

    alias: 'store.normalizations',
    model: 'command.model.NormalizationDesignGroup',

    autoLoad: false,

    remoteSort: false,

    remoteFilter: true,

    pageSize: 50,

    proxy: {
        type: 'memory',
        enablePaging: 'true',
        reader: {
            type: 'json',
            rootProperty: 'normalization_design_group',
            totalProperty: 'total'
        }
    }
});
