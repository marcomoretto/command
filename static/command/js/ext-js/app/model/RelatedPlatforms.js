Ext.define('command.model.RelatedPlatforms', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'original_platform',  type: 'string'},
        {name: 'reporter_platform',  type: 'string'},
        {name: 'experiments',  type: 'string'}
    ]
});
