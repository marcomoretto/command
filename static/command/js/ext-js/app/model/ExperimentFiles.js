Ext.define('command.model.ExperimentFiles', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'name',   type: 'string'},
        {name: 'path',   type: 'string'},
        {name: 'type',   type: 'string'},
        {name: 'size',   type: 'int'},
        {name: 'date',   type: 'date'}
    ]
});
