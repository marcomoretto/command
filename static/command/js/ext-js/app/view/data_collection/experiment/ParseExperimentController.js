Ext.define('command.view.data_collection.experiment.ParseExperimentController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.parse_experiment_controller',

    onParseExperimentDestroy: function (me) {
        var request = me.getRequestObject('remove_experiment_channel');
        request.values = JSON.stringify(me.command_params);
        Ext.Ajax.request({
            url: request.view + '/' + request.operation + '/' + me.command_params,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
            },
            failure: function (response) {
                console.log('Server error');
            }
        });
    }
});