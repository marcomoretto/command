Ext.define('command.model.ExperimentSearchResult', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        //{name: 'database',   reference: 'command.model.PublicDatabase'},
        //{name: 'status',   reference: 'command.model.ExperimentStatus'},
        {name: 'date',  type: 'date'},
        {name: 'experiment_access_id',  type: 'string'},
        {name: 'ori_result_id',  type: 'string'},
        {name: 'organism',  type: 'string'},
        {name: 'experiment_alternative_access_id',  type: 'string'},
        {name: 'n_samples',  type: 'int'},
        {name: 'experiment_name',  type: 'string'},
        {name: 'platform',  type: 'string'},
        {name: 'scientific_paper_ref',  type: 'string'},
        {name: 'type',  type: 'string'},
        {name: 'description',  type: 'string'}
    ]
});
