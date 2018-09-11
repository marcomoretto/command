Ext.define('command.view.data_collection.experiment.ExperimentSearchOptions', {
    extend: 'Ext.panel.Panel',
    xtype: 'experiment_search_options',
    title: 'Search options',

    requires: [
        'Ext.panel.Panel',
        'command.store.DataSource',
        'command.view.data_collection.experiment.ImportExperimentPublicController'
    ],

    controller: 'import_experiment_public_controller',

    alias: 'widget.experiment_search_options',

    itemId: 'experiment_search_options',

    layout: 'fit',

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'experiment_public',

    items: {
        xtype: 'form',

        items: [
            {
                xtype: 'textfield',
                fieldLabel: 'Term',
                name: 'search_term',
                emptyText: 'term',
                itemId: 'search_term',
                allowBlank: false,
                anchor: '50%'
            },
            {
                xtype: 'combo',
                fieldLabel: 'Database',
                name: 'source_id',
                itemId: 'source_name',
                valueField: 'id',
                displayField: 'source_name',
                editable: false,
                allowBlank: false,
                autoSelect: true,
                forceSelection: true,
                anchor: '50%',
                store: Ext.create('command.store.DataSource'),
                listeners: {
                    focus: 'onFocusPublicDatabase'
                }
            }],
            buttons: [{
                text: 'Stop search',
                formBind: false,
                listeners: {
                    click: 'onStopSearchExperimentPublic'
                }
            }, {
                text: 'Search',
                formBind: true,
                listeners: {
                    click: 'onSearchExperimentPublic'
                }
            }]
    }
});

Ext.define('command.view.data_collection.experiment.ExperimentSearchResult', {
    extend: 'command.Grid',
    xtype: 'experiment_search_result',
    title: 'Experiment search result',

    requires: [
        'Ext.panel.Panel',
        'Ext.toolbar.Paging',

        'command.store.ExperimentSearchResult',
        'command.model.ExperimentSearchResult',
        'command.view.data_collection.experiment.ImportExperimentPublicController'
    ],

    controller: 'import_experiment_public_controller',

    store: null,

    alias: 'widget.experiment_search_result',

    itemId: 'experiment_search_result',

    reference: 'experiment_search_result',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'experiment_public',

    command_read_operation: 'read_experiment_search_results',

    viewConfig: {
        getRowClass: function(record, index, rowParams, ds) {
            if (record.data.tag == 'platform') {
                return 'orange-row'
            }
            if (record.data.tag == 'excluded') {
                return 'red-row'
            }
            if (record.data.tag == 'present') {
                return 'green-row'
            }
            return '';
        }
    },

    selModel: {
        selType: 'checkboxmodel',
        mode: 'MULTI',
        checkOnly: true,
        allowDeselect: false
    },
    columns: [{
        text: 'ID',
        flex: 1,
        sortable: true,
        dataIndex: 'id',
        hidden: false
    }, {
        text: 'Accession',
        flex: 2,
        sortable: true,
        dataIndex: 'experiment_access_id',
        renderer: function(value, metadata, record) {
            return '<a href="' + record.data['experiment_accession_base_link'] + value + '" target="_blank">'+ value +'</a>';
        }
    }, {
        text: 'Status',
        flex: 1,
        sortable: false,
        xtype: 'actioncolumn',
        dataIndex: 'status',
        iconCls: 'dimgrayIcon',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            switch (value.name) {
                case 'experiment_new':
                    this.items[0].glyph = command.current.experiment_status_glyph['new'];
                    this.items[0].tooltip =value.description;
                    break;
                case 'experiment_scheduled':
                    this.items[0].glyph = command.current.experiment_status_glyph['scheduled'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'experiment_downloading':
                    this.items[0].glyph = command.current.experiment_status_glyph['downloading'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'experiment_data_ready':
                    this.items[0].glyph = command.current.experiment_status_glyph['data_ready'];
                    this.items[0].tooltip = value.description;
                    break;
                case 'experiment_excluded':
                    this.items[0].glyph = command.current.experiment_status_glyph['excluded'];
                    this.items[0].tooltip = value.description;
                    break;
            }
            if (record.data.tag == 'platform') {
                //this.items[0].glyph = command.current.experiment_status_glyph['downloading'];
                this.items[0].tooltip += '. Platform(s) is already imported.'
            }
        }
    }, {
        text: 'Database',
        flex: 1,
        sortable: true,
        dataIndex: 'data_source',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            return value.source_name;
        }
    }, {
        text: 'Original ID',
        flex: 2,
        sortable: true,
        dataIndex: 'ori_result_id'
    }, {
        text: 'Alternative accession',
        flex: 2,
        sortable: true,
        dataIndex: 'experiment_alternative_access_id'
    }, {
        text: 'Date',
        flex: 2,
        sortable: true,
        dataIndex: 'date'
    }, {
        text: 'N° samples',
        flex: 1,
        sortable: true,
        dataIndex: 'n_samples'
    }, {
        text: 'Experiment name',
        flex: 2,
        sortable: true,
        tdCls: 'command_tooltip',
        dataIndex: 'experiment_name'
    }, {
        text: 'Platform',
        flex: 2,
        sortable: true,
        dataIndex: 'platform',
        renderer: function(value, metadata, record) {
            if (record.data['platform_accession_base_link']) {
                return '<a href="' + record.data['platform_accession_base_link'] + value + '" target="_blank">'+ value +'</a>';
            }
            return value;
        }
    }, {
        text: 'Scientific paper',
        flex: 2,
        sortable: true,
        dataIndex: 'scientific_paper_ref',
        renderer: function(value, metadata, record) {
            return '<a href="' + record.data['scientific_paper_accession_base_link'] + value + '" target="_blank">'+ value +'</a>';
        }
    }, {
        text: 'Type',
        flex: 2,
        sortable: true,
        dataIndex: 'type'
    }, {
        text: 'Description',
        flex: 2,
        sortable: true,
        tdCls: 'command_tooltip',
        dataIndex: 'description'
    }],

    buttons: [{
        text: 'Exclude',
        disabled : true,
        bind     : {
            disabled : '{!experiment_search_result.selection}'
        },
        listeners: {
            click: 'onExcludeExperiment'
        }
    }, {
        text: 'Download',
        disabled : true,
        bind     : {
            disabled : '{!experiment_search_result.selection}'
        },
        listeners: {
            click: 'onDownloadExperimentData'
        }
    }],

    initComponent: function() {
        this.store = Ext.create('command.store.ExperimentSearchResult');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});

Ext.define('command.view.data_collection.experiment.ImportExperimentPublic', {
    extend: 'Ext.panel.Panel',

    requires: [
        'Ext.panel.Panel',
        'command.view.data_collection.experiment.ImportExperimentPublicController'
    ],

    alias: 'widget.import_experiment_public',

    controller: 'import_experiment_public_controller',

    layout: 'border',
    bodyBorder: false,

    layout: {
        type: 'vbox',
        pack: 'start',
        align: 'stretch'
    },

    defaults: {
        frame: false,
        bodyPadding: 5
    },

    items: [
        {
            xtype: 'experiment_search_result',
            border: false,
            flex: 5
        },
        {
            xtype: 'experiment_search_options',
            border: false,
            flex: 2
        }
    ],

    initComponent: function() {
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});