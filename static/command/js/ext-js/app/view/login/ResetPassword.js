Ext.define('command.view.login.ResetPassword', {
    extend: 'Ext.window.Window',
    xtype: 'reset_password',

    requires: [
        'Ext.window.Window',
        'command.view.login.ResetPasswordController',
        'Ext.form.Panel'
    ],

    controller: 'reset_password',
    bodyPadding: 10,
    title: 'Reset password for user',
    closable: false,
    autoShow: true,

    items: {
        xtype: 'form',
        reference: 'form',
        items: [{
            xtype: 'textfield',
            name: 'password',
            inputType: 'password',
            fieldLabel: 'New password',
            allowBlank: false
        }],
        buttons: [{
            text: 'Submit',
            formBind: true,
            listeners: {
                click: 'onResetPasswordClick'
            }
        }]
    },

    initComponent: function() {

        this.callParent();
    }
});