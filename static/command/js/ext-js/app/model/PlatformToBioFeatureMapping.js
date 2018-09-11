Ext.define('command.model.PlatformToBioFeatureMapping', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'string'},
        {name: 'date',  type: 'date'},
        {name: 'total_aligned',  type: 'string'}
    ]
});
