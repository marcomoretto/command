Ext.define('command.model.DataSource', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'string'},
        {name: 'source_name',   type: 'string'},
        {name: 'python_class',  type: 'string'},
        {name: 'is_local',  type: 'boolean'}
    ]
});
