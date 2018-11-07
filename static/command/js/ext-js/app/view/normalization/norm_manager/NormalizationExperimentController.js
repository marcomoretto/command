Ext.define('command.view.normalization.norm_manager.NormalizationExperimentController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.normalization_experiment_controller',

    onNormalizationExperimentAfterRender: function(me) {
        var request = me.getRequestObject('get_experiment_details');
        request.values = me.command_params;
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                command.current.checkHttpResponse(response);
                var resp = JSON.parse(response.responseText);
                console.log(resp);
                me.setTitle('Normalize experiment ' + resp.normalization_experiment.experiment.experiment_access_id);
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    }

});
