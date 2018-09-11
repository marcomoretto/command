Ext.define('command.view.data_collection.experiment.ImportExperimentLocal-Card0', {
    extend: 'Ext.panel.Panel',
    controller: 'import_experiment_local_controller',

    xtype: 'import_experiment_local_card0',

    layout: 'anchor',
    bodyBorder: false,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [{
        xtype: 'panel',
        html: '<h2>Experiment identifier</h2>' +
        '<p>Step 1 of 3</p>' +
        '<p>Please select an identifier for your new experiment and press the "Next" button to continue...</p>'
    },{
        xtype: 'textfield',
        margin: '10 0 0 5',
        anchor: '50%',
        allowBlank: false,
        fieldLabel: 'Experiment ID',
        name: 'experiment_id',
        emptyText: 'MY_NEW_EXPERIMENT',
        listeners: {
            change: 'onExperimentIDChange'
        }
    }]
});

Ext.define('command.view.data_collection.experiment.ImportExperimentLocal-Card1', {
    extend: 'Ext.form.Panel',
    controller: 'import_experiment_local_controller',

    xtype: 'import_experiment_local_card1',

    layout: 'anchor',
    bodyBorder: false,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [{
        xtype: 'panel',
        html: '<h2>Experiment structure</h2>' +
        '<p>Step 2 of 3</p>' +
        '<p>Please upload a valid YAML that hold the experiment structure and press the "Next" button to continue...</p>'
    },{
        xtype: 'filefield',
        anchor: '80%',
        margin: '10 0 0 5',
        hideLabel: true,
        name: 'experiment_structure_file',
        clearOnSubmit: false,
        listeners: {
            change: 'onExperimentStructureFileChange'
        }
    }, {
        xtype: 'panel',
        html: '<h4>Example</h4>' +
        '<p>experiment:<br>' +
        '&nbsp;&nbsp;platform_1:<br>' +
        '&nbsp;&nbsp;&nbsp;&nbsp;samples: [sample_1, sample_2]<br>' +
        '&nbsp;&nbsp;platform_2:<br>' +
        '&nbsp;&nbsp;&nbsp;&nbsp;samples: [samples_3, samples_4, sample_5]</p>'
    }]
});

Ext.define('command.view.data_collection.experiment.ImportExperimentLocal-Card2', {
    extend: 'Ext.form.Panel',
    controller: 'import_experiment_local_controller',

    xtype: 'import_experiment_local_card2',

    layout: 'anchor',
    bodyBorder: false,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [{
        xtype: 'panel',
        html: '<h2>Experiment files</h2>' +
        '<p>Step 3 of 3</p>' +
        '<p>Please upload a valid ZIP (or TAR.GZ) file that contains all experiment files and press the "Upload experiment" button to continue...</p>'
    },{
        xtype: 'filefield',
        anchor: '80%',
        margin: '10 0 0 5',
        hideLabel: true,
        clearOnSubmit: false,
        name: 'experiment_data_file',
        listeners: {
            change: 'onExperimentDataChange'
        }
    }]
});

Ext.define('command.view.data_collection.experiment.ImportExperimentLocal', {
    extend: 'Ext.panel.Panel',

    requires: [
        'Ext.panel.Panel',
        'Ext.layout.container.Card',
        'command.view.data_collection.experiment.ImportExperimentLocalController'
    ],

    alias: 'widget.import_experiment_local',

    controller: 'import_experiment_local_controller',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'experiment_local',

    layout: 'card',
    bodyBorder: false,

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    bbar: ['->',
        {
            itemId: 'card-prev',
            text: '&laquo; Previous',
            handler: 'showPrevious',
            disabled: true
        },
        {
            itemId: 'card-next',
            text: 'Next &raquo;',
            handler: 'showNext',
            disabled: true
        },
        {
            itemId: 'upload_experiment',
            text: 'Upload experiment',
            handler: 'onExperimentDataFileUpload',
            hidden: true
        }
    ],

    items: [
        {
            id: 'card-0',
            xtype: 'import_experiment_local_card0'
        },
        {
            id: 'card-1',
            xtype: 'import_experiment_local_card1'
        },
        {
            id: 'card-2',
            xtype: 'import_experiment_local_card2'
        }
    ],

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});