Ext.define('command.view.normalization.norm_manager.NormalizationExperiment', {
    extend: 'Ext.panel.Panel',
    xtype: 'normalization_experiment',
    title: 'Normalize experiment',

    requires: [
        'Ext.panel.Panel'
    ],

    controller: 'normalization_experiment_controller',

    alias: 'widget.normalization_experiment',

    itemId: 'normalization_experiment',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    layout: 'fit',

    command_view: 'normalization_experiment',

    layout: 'border',
    bodyBorder: false,

    defaults: {
        collapsible: true,
        split: true,
        bodyPadding: 10
    },

    items: [],

    listeners: {
        afterrender: 'onNormalizationExperimentAfterRender'
    },

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});