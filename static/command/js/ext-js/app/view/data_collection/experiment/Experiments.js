Ext.define('command.view.ExperimentSampleDetails', {
    extend: 'Ext.window.Window',
    xtype: 'window_experiment_sample_details',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel',
        'command.view.data_collection.experiment.ExperimentsController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: '',

    controller: 'experiments_controller',

    bodyPadding: 10,
    title: 'Experiment samples details',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 900,
    height: 600,
    constrain: true,

    items: [{
        //
    }]
});

Ext.define('command.view.NewExperiment', {
    extend: 'Ext.window.Window',
    xtype: 'window_new_experiment',

    requires: [
        'Ext.window.Window',
        'Ext.form.Panel',
        'command.view.data_collection.experiment.ExperimentsController'
    ],

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: '',

    controller: 'experiments_controller',

    bodyPadding: 10,
    title: 'New Experiment',
    closable: true,
    autoShow: true,
    modal: true,
    layout: 'fit',
    width: 1100,
    height: 600,
    constrain: true,

    items: [{
        //
    }]
});

Ext.define('command.view.data_collection.experiment.Experiments', {
    extend: 'command.Grid',

    xtype: 'experiments',

    title: 'Experiments',

    requires: [
        'Ext.panel.Panel',
        'Ext.toolbar.Paging',

        'command.view.data_collection.experiment.ExperimentsController'
    ],

    controller: 'experiments_controller',

    store: null,

    alias: 'widget.experiments',

    itemId: 'experiments',

    reference: 'experiments',

    viewModel: {},

    mixins: {
        getRequestObject: 'RequestMixin'
    },

    command_view: 'experiments',

    command_read_operation: 'read_experiments',

    viewConfig: {
        getRowClass: function(record, index, rowParams, ds) {
            if (record.data.status == 'experiment_excluded') {
                return 'red-row'
            }
            return '';
        }
    },

    listeners: {
        itemdblclick: 'onExperimentDoubleClick'
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
            if (record.data.data_source.is_local) {
                return value;
            } else {
                return '<a href="' + record.data['experiment_accession_base_link'] + value + '" target="_blank">' + value + '</a>';
            }
        }
    }, {
        text: 'Status',
        flex: 2,
        sortable: false,
        xtype: 'actioncolumn',
        dataIndex: 'status',
        iconCls: 'dimgrayIcon',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            switch (value) {
                case 'experiment_new':
                    this.items[0].glyph = command.current.experiment_status_glyph['new'];
                    this.items[0].tooltip = record.data.status_description;
                    break;
                case 'experiment_downloading':
                    this.items[0].glyph = command.current.experiment_status_glyph['downloading'];
                    this.items[0].tooltip = record.data.status_description;
                    break;
                case 'experiment_data_ready':
                    this.items[0].glyph = command.current.experiment_status_glyph['data_ready'];
                    this.items[0].tooltip = record.data.status_description;
                    break;
                case 'experiment_raw_data_imported':
                    this.items[0].glyph = command.current.experiment_status_glyph['raw_data'];
                    this.items[0].tooltip = record.data.status_description;
                    break;
                case 'experiment_excluded':
                    this.items[0].glyph = command.current.experiment_status_glyph['excluded'];
                    this.items[0].tooltip = record.data.status_description;
                    break;
            }
        }
    }, {
        text: 'Source',
        flex: 2,
        sortable: true,
        dataIndex: 'data_source',
        renderer: function (value, metaData, record, rowIdx, colIdx, store, view) {
            return value.source_name;
        }
    }, {
        text: 'N° samples',
        flex: 2,
        sortable: true,
        dataIndex: 'n_samples'
    }, {
        text: 'Experiment name',
        flex: 2,
        sortable: true,
        tdCls: 'command_tooltip',
        dataIndex: 'experiment_name'
    }, {
        text: 'Platforms',
        flex: 2,
        sortable: true,
        dataIndex: 'platforms',
        renderer: function(value, metadata, record) {
            var platforms = [];
            if (record.data.data_source.is_local) {
                record.data.platforms.forEach(function (e, i) {
                    platforms.push(e.platform_access_id);
                });
                return platforms.join();
            } else {
                record.data.platforms.forEach(function (e, i) {
                    platforms.push('<a href="' + record.data['platform_accession_base_link'] + e.platform_access_id + '" target="_blank">' + e.platform_access_id + '</a>');
                });
                return platforms.join();
            }
            return value;
        }
    }, {
        text: 'Scientific paper',
        flex: 2,
        sortable: true,
        dataIndex: 'scientific_paper_ref',
        renderer: function(value, metadata, record) {
            console.log(value);
            if (value) {
                return '<a href="' + record.data['scientific_paper_accession_base_link'] + value + '" target="_blank">' + value + '</a>';
            }
        }
    }, {
        text: 'Description',
        flex: 2,
        sortable: true,
        tdCls: 'command_tooltip',
        dataIndex: 'description'
    }],
    features: [{ftype:'grouping'}],

    bbar: [
        {
            text: 'New experiment',
            xtype: 'button',
            tooltip: {
                text: 'New experiment'
            },
            iconCls: null,
            glyph: 'xf055',
            menu: {
                xtype: 'menu',
                forceLayout: true,
                items: [{
                    text: 'From public DB',
                    scale: 'medium',
                    tooltip: {
                        text: 'From public DB'
                    },
                    glyph: 'xf0c3',
                    listeners: {
                        click: 'onNewExperimentPublicDB'
                    }
                }, {
                    text: 'From local files',
                    scale: 'medium',
                    tooltip: {
                        text: 'From local files'
                    },
                    glyph: 'xf115',
                    listeners: {
                        click: 'onNewExperimentLocalFiles'
                    }
                }]
            }
        }, {
            xtype: 'button',
            text: 'Parse/Import experiment',
            iconCls: null,
            tooltip: {
                text: 'Parse/Import experiment'
            },
            glyph: 'xf120',
            listeners: {
                click: 'onParseExperiment'
            },
            bind: {
                disabled: '{!experiments.selection}'
            }
        }, {
            xtype: 'button',
            text: 'View experiment details',
            iconCls: null,
            tooltip: {
                text: 'View experiment details'
            },
            glyph: 'f06e',
            listeners: {
                click: 'onViewExperimentDetails'
            },
            bind: {
                disabled: '{!experiments.selection}'
            }
        }, {
            xtype: 'button',
            text: 'Delete',
            iconCls: null,
            tooltip: {
                text: 'Delete'
            },
            glyph: 'xf056',
            menu: {
                xtype: 'menu',
                forceLayout: true,
                items: [{
                    text: 'Delete experiment',
                    iconCls: null,
                    tooltip: {
                        text: 'Delete experiment'
                    },
                    glyph: 'xf0c3',
                    listeners: {
                        click: 'onDeleteExperiment'
                    },
                    bind: {
                        disabled: '{!experiments.selection}'
                    }
                }, {
                    text: 'Delete parsing data',
                    iconCls: null,
                    tooltip: {
                        text: 'Delete parsing data'
                    },
                    glyph: 'xf120',
                    listeners: {
                        click: 'onDeleteParsingData'
                    },
                    bind: {
                        disabled: '{!experiments.selection}'
                    }
                }, {
                    text: 'Delete downloaded/uploaded data',
                    iconCls: null,
                    tooltip: {
                        text: 'Delete downloaded/uploaded data'
                    },
                    glyph: 'xf0c7',
                    listeners: {
                        click: 'onDeleteDownloadedUploadedData'
                    },
                    bind: {
                        disabled: '{!experiments.selection}'
                    }
                }]
            }
        }
    ],

    initComponent: function() {
        this.store = Ext.create('command.store.Experiments');
        this.callParent();
    },

    destroy: function() {
        this.callParent();
    }
});