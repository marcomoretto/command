Ext.define('command.view.login.Login', {
    extend: 'Ext.window.Window',
    xtype: 'login',

    requires: [
        'Ext.window.Window',
        'command.view.login.LoginController',
        'Ext.form.Panel'
    ],

    controller: 'login',
    bodyPadding: 10,
    title: 'Login',
    closable: false,
    autoShow: true,
    modal: true,

    items: {
        xtype: 'form',
        reference: 'form',
        items: [{
            xtype: 'panel',
            name: 'text',
            html: 'Ciao',
            hidden: true
        }, {
            xtype: 'textfield',
            name: 'username',
            fieldLabel: 'Username',
            allowBlank: false
        }, {
            xtype: 'textfield',
            name: 'password',
            inputType: 'password',
            fieldLabel: 'Password',
            allowBlank: false
        }],
        buttons: [{
            text: 'Login',
            formBind: true,
            listeners: {
                click: 'onLoginClick'
            }
        }]
    },

    initComponent: function() {

        this.callParent();
    }
});