Ext.define('command.model.MessageLog', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'date',   type: 'date'},
        {name: 'title',  type: 'string'},
        {name: 'message',  type: 'string'},
        {name: 'source',  type: 'string'}
    ]
});
