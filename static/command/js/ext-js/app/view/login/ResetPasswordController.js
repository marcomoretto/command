Ext.define('command.view.login.ResetPasswordController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.reset_password',

    onResetPasswordClick: function() {
        var view = this.getView();
        var params = view.down('[xtype="form"]').getValues();

        Ext.Ajax.request({
            url: 'reset_password/',
            params: params,
            success: function (response) {
                window.location.reload();
            },
            failure: function (response) {
                Ext.Msg.alert('Server problem', 'Server Problem');
            }
        });
    }
});
