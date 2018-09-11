Ext.define('command.model.ExperimentPlatformsFiles', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',   type: 'int'},
        {name: 'platform_name',   type: 'string'},
        {name: 'description',   type: 'string'}
    ]
});
