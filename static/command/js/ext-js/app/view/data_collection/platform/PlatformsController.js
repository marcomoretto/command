Ext.define('command.view.data_collection.platform.PlatformsController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.platforms_controller',

    onPlatformAfterRender: function (me) {
        //
    },

    onDeletePlatform: function(b) {
        var grid = b.up('platforms');
        var platform = grid.getSelectionModel().getSelection()[0].data;
        var request = grid.getRequestObject('delete_platform');
        Ext.MessageBox.show({
            title: 'Delete platform',
            msg: 'Are you sure you want to delete platform ' + platform.platform_access_id + '?<br><br>' +
            'This platform is used in <strong>' + platform.n_experiments + ' experiment(s)</strong> and measures <strong>' +
            platform.n_samples + ' samples (' + platform.n_samples_imported + ' samples already imported)</strong>.',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    request.values = platform.id;
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    });
                }
            }
        })
    },
    
    onViewBioFeatureReporter: function (me) {
        var selection = me.up('grid').getSelectionModel().getSelection()[0].data;
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        if (selection.platform_type) {
            switch (selection.platform_type.name) {
                case 'rnaseq':
                    Ext.MessageBox.show({
                        title: 'RNA-seq platform',
                        msg: 'For RNA-seq platform ' + selection.platform_access_id +  ', ' +  comp.compendium_type.bio_feature_name + ' is/are directly measured',
                        buttons: Ext.MessageBox.OK,
                        icon: Ext.MessageBox.INFO,
                        fn: function (a) {
                        }
                    });
                    break
                case 'microarray':
                    var win = Ext.create({
                        xtype: 'window_bio_feature_reporter',
                        title: 'Microarray platform ' + selection.platform_access_id + ': ' +
                            comp.compendium_type.bio_feature_name + ' feature reporters (' + selection.platform_type.bio_feature_reporter_name + ')',
                        platform: selection
                    });
                    break
            }
        } else {
            Ext.MessageBox.show({
                title: 'Cannot show biological features reported',
                msg: 'Platform ' + selection.platform_access_id +  ' has no type (yet)! You probably need to first parse and import an experiment using this platform.',
                buttons: Ext.MessageBox.OK,
                icon: Ext.MessageBox.ERROR,
                fn: function (a) {
                }
            });
        }
    },

    onMapPlatformToBioFeature: function (me) {
        var selection = me.up('grid').getSelectionModel().getSelection()[0].data;
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        if (selection.platform_type) {
            switch (selection.platform_type.name) {
                case 'rnaseq':
                    Ext.MessageBox.show({
                        title: 'RNA-seq platform',
                        msg: 'RNA-seq platform ' + selection.platform_access_id +  ' is automatically mapped to ' + comp.compendium_type.bio_feature_name,
                        buttons: Ext.MessageBox.OK,
                        icon: Ext.MessageBox.INFO,
                        fn: function (a) {
                        }
                    });
                    break
                case 'microarray':
                    command.current.createWin({
                        xtype: 'window_map_microarray_platform',
                        title: 'Map microarray platform ' + selection.platform_access_id + ' to ' + comp.compendium_type.bio_feature_name,
                        platform: selection
                    });
                    break
            }
        } else {
            Ext.MessageBox.show({
                title: 'Cannot map platform to biological features',
                msg: 'Platform ' + selection.platform_access_id +  ' has no type (yet)! You probably need to first parse and import an experiment using this platform.',
                buttons: Ext.MessageBox.OK,
                icon: Ext.MessageBox.ERROR,
                fn: function (a) {
                }
            });
        }
    }
});