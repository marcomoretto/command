Ext.define('command.model.FileType', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'string'},
        {name: 'file_type',  type: 'string'}
    ]
});
