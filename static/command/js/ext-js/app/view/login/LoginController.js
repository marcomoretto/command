Ext.define('command.view.login.LoginController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.login',

    onLoginClick: function() {
        var view = this.getView();
        var login_params = view.down('[xtype="form"]').getValues();

        Ext.Ajax.request({
            url: 'check_login/',
            params: login_params,
            success: function (response) {
                var resData = Ext.decode(response.responseText);
                if (resData.login) {
                    localStorage.setItem("current_compendium", null);
                    localStorage.setItem("views", JSON.stringify(resData.views));
                    window.location.reload();
                } else {
                    Ext.Msg.alert('Login', 'Incorrect login');
                }
            },
            failure: function (response) {
                Ext.Msg.alert('Server problem', 'Server Problem');
            }
        });
    }
});
