Ext.define('command.model.User', {
    extend: 'Ext.data.Model',

    idProperty: 'id',

    fields: [
        {name: 'id',  type: 'int'},
        {name: 'username',   type: 'string'},
        {name: 'first_name',   type: 'string'},
        {name: 'last_name',   type: 'string'},
        {name: 'email',   type: 'string'},
        {name: 'groups',   reference: 'command.model.Group'},
        {name: 'last_login',   type: 'date'},
        {name: 'date_joined',   type: 'date'},
        {name: 'is_active',   type: 'bool'},
        {name: 'is_superuser',   type: 'bool'}
    ]
});
