Ext.define('command.model.NormalizationExperiments', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'experiment_access_id',  type: 'string'},
        {name: 'name',   type: 'string'},
        {name: 'status',   type: 'string'},
        {name: 'use_experiment',   type: 'boolean'}
    ]
});
