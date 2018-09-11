Ext.define('command.view.data_collection.experiment.ParseExperiment', {
    extend: 'Ext.panel.Panel',

    title: 'Parse Experiment',

    xtype: 'parse_experiment',

    itemId: 'parse_experiment',

    requires: [
        'command.view.data_collection.experiment.PythonEditor',
        'command.view.data_collection.experiment.ExperimentPreview'
    ],

    alias: 'widget.parse_experiment',

    command_multiple: true,

    controller: 'parse_experiment_controller',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'parse_experiment',

    layout: 'fit',

    bodyBorder: false,

    bodyPadding: 10,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [{
        xtype: 'panel',
        itemId: 'parse_experiment_details',
        layout: 'accordion',
        items: [{
            xtype: 'experiment_preview'
        }, {
            xtype: 'experiment_files'
        }, {
            xtype: 'python_editor'
        }
        ]
    }],

    listeners: {
        expand: function (p, eOpts ) {
            // Hack to prevent store to crash when reloaded without having focus
            p.getView().refresh();
        },
        //afterrender: 'onParseExperimentAfterRender',
        beforeshow: function ( me, eOpts ) {
            //
        }
    },

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.controller.onParseExperimentDestroy(this);
        this.callParent();
    }
});