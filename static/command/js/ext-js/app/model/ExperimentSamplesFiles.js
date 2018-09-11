Ext.define('command.model.ExperimentSamplesFiles', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',   type: 'int'},
        {name: 'sample_name',   type: 'string'},
        {name: 'description',   type: 'string'}
    ]
});
