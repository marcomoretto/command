Ext.define('command.model.ParsingDetails', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'input_filename', reference: 'command.model.ExperimentFiles'},
        {name: 'script_name',   type: 'string'},
        {name: 'order',   type: 'int'},
        {name: 'parameters',   type: 'string'}
    ]
});
