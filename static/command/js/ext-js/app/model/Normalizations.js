Ext.define('command.model.Normalizations', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'name',   type: 'string'},
        {name: 'date',  type: 'date'},
        {name: 'type',   type: 'string'},
        {name: 'version',   type: 'string'},
        {name: 'n_exp',   type: 'int'},
        {name: 'public',   type: 'boolean'}
    ]
});
