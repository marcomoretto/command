Ext.define('command.model.NormalizationType', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'string'},
        {name: 'name',  type: 'string'},
        {name: 'description',  type: 'string'}
    ]
});
