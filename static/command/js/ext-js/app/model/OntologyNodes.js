Ext.define('command.model.OntologyNodes', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'id',  type: 'string'},
        {name: 'original_id',   type: 'string'},
        {name: 'valid',   type: 'boolean'},
    ]
});
