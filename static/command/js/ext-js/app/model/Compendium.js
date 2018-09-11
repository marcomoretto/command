Ext.define('command.model.Compendium', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id',  type: 'int'},
        {name: 'compendium_name',   type: 'string'},
        {name: 'compendium_nick_name',  type: 'string'},
        {name: 'description',  type: 'string'},
        {name: 'html_description',   type: 'string'},
        {name: 'ct',   reference: 'command.model.CompendiumType'},
        {name: 'db_engine',  type: 'string'},
        {name: 'db_user',  type: 'string'},
        {name: 'db_password',   type: 'string'},
        {name: 'db_port',  type: 'string'},
        {name: 'db_host',   type: 'string'}
    ]
});
