Ext.define('command.model.Platforms', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'platform_access_id',  type: 'string'},
        {name: 'platform_name',  type: 'string'},
        {name: 'description',  type: 'string'},
        {name: 'reporter_platform',  type: 'string'}
        //{name: 'platform_type',  type: 'string'},
    ]
});
