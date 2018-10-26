Ext.define('command.view.annotation.ontologies.OntologiesController', {
    extend: 'Ext.app.ViewController',

    alias: 'controller.ontologies_controller',

    onCreateOntologyField: function (me) {
        var value = me.up('form').getForm().getValues();
        var panel = me.up('#new_ontology_panel');
        var tagfield = panel.down('#ontology_tagfield');
        var field = tagfield.store.add(value);
        console.log(tagfield.id);
        console.log(value);
        tagfield.addValue(field);
    },

    NewOntologyNodeParentAfterRender: function(me) {
        var ws = command.current.ws;
        var operation = 'read_ontology_nodes';
        var panel = me.up('new_ontology_node_panel');
        var win = panel.up('window');
        var request = panel.getRequestObject(operation);
        var requestEmpty = panel.getRequestObject(operation);
        request.values = win.ontology.id;
        ws.listen();
        ws.demultiplex(request.view, function (action, stream) {
            if (action.request.operation == request.operation) {
                if (me.getValue()) {
                    me.store.getProxy().setData(action.data);
                    me.store.suspendEvents();
                    me.store.clearFilter();
                    me.store.resumeEvents();
                    me.store.filter({
                        property: 'original_id',
                        anyMatch: true,
                        value: me.getValue()
                    });
                } else {
                    me.store.setData(action.data.nodes);
                }
            }
            if (action.request.operation == 'refresh') {
                ws.stream(request.view).send(request);
            }
        });
        requestEmpty.values = {'ontology_id': win.ontology.id, 'text': null};
        ws.stream(requestEmpty.view).send(requestEmpty);
    },

    NewOntologyNodeChange: function(me, newValue, oldValue, eOpts) {
        var panel = me.up('new_ontology_node_panel');
        var win = panel.up('window');
        var ws = command.current.ws;
        var operation = 'read_ontology_nodes';
        var panel = me.up('new_ontology_node_panel');
        var request = panel.getRequestObject(operation);
        request.values = {'ontology_id': win.ontology.id, 'text': newValue};
        ws.stream(request.view).send(request);
    },

    onDeleteOntologyNode: function(me) {
        var panel = me.up('ontologies');
        var ontology_panel = panel.down('available_ontologies');
        var tabpanel = me.up('#ontology_tabpanel');
        var node_id = null;
        var node_original_id = null;
        switch (tabpanel.getActiveTab().xtype) {
            case 'view_ontology':
                node_id = tabpanel.getActiveTab().getSelection()[0].id;
                node_original_id = tabpanel.getActiveTab().getSelection()[0].data.original_id;
                break;
            case 'cy_ontology':
                node_id = tabpanel.getActiveTab().cy.$(':selected').json().data.id;
                node_original_id = tabpanel.getActiveTab().cy.$(':selected').json().data.original_id;
                break;
        }
        var request = panel.getRequestObject('delete_ontology_node');
        console.log(panel.id);
        console.log(request);
        Ext.MessageBox.show({
            title: 'Delete ontology node',
            msg: 'Are you sure you want to delete node ' + node_original_id + '?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    request.values = node_id;
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            command.current.checkHttpResponse(response);
                            ontology_panel.getController().onSelectOntology(ontology_panel.getView(), ontology_panel.getSelection()[0]);
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                        }
                    });
                }
            }
        });
    },

    onCreateOntologyNode: function(me) {
        var panel = me.up('new_ontology_node_panel');
        var win = me.up('window');
        var tabpanel = win.tabpanel;
        var form = me.up('form').getForm();
        var combo = panel.down('#parent_node_id');
        var ontology = win.ontology;
        var request = panel.getRequestObject('create_ontology_node');
        if (combo.getSelection().data.valid) {
            request.values = form.getValues();
            request.values.id = ontology.id;
            if (form.isValid()) {
                form.submit({
                    url: request.view + '/' + request.operation,
                    waitMsg: null,
                    params: {
                        request: JSON.stringify(request)
                    },
                    success: function (f, response) {
                        command.current.checkHttpResponse(response.response);
                        var panel = tabpanel.down('available_ontologies');
                        var cy_panel = tabpanel.down('cy_ontology');
                        var grid_panel = tabpanel.down('view_ontology');
                        panel.controller._populateOntologyGraphView(panel, cy_panel, ontology.id);
                        panel.controller._populateOntologyNodesGrid(panel, grid_panel, ontology.id);
                        win.close();
                    },
                    failure: function (f, response) {
                        command.current.checkHttpResponse(response.response);
                        win.close();
                    }
                });
            }
        } else {
            Ext.MessageBox.show({
                title: 'Invalid parent node',
                msg: 'Please select a valid parent node from the dropdown menu',
                buttons: Ext.MessageBox.OK,
                icon: Ext.MessageBox.ERROR,
                fn: function () {
                }
            });
        }
    },

    onNewOntologyNode: function (me) {
        var tabpanel = me.up('ontologies');
        var panel = tabpanel.down('available_ontologies');
        var ontology = panel.getSelection()[0].data;
        var height = 300 + (35 * ontology.columns.length);
        var win = Ext.create({
            xtype: 'window_new_ontology_node',
            ontology: ontology,
            height: height,
            tabpanel: tabpanel
        });
        var fields = win.down('#json_field_columns');
        fields.setVisible(true);
        ontology.columns.forEach(function (c) {
            fields.add(
                {
                    xtype: 'textfield',
                    fieldLabel: c.text,
                    name: c.data_index,
                    anchor: '100%',
                    margin: '10 10 10 5',
                    allowBlank: true
                }
            )
        });
    },

    onNewOntology: function (me) {
        var win = Ext.create({
            xtype: 'window_new_ontology'
        });
    },

    onUpdateOntology: function (me) {
        var win = Ext.create({
            xtype: 'window_new_ontology'
        });
        console.log(me.id);
        var panel = me.up('available_ontologies');
        var ontology = panel.getSelection()[0].data;
        var button = win.down('#create_ontology_button');
        var form = win.down('#ontology_form').getForm();
        win.setTitle('Update ontology ' + ontology.name);
        button.setText('Update');
        win.down('#ontology_file').hide();
        win.down('#create_blank').hide();
        win.setHeight(420);
        form.setValues(ontology);
        var tagfield = win.down('#ontology_tagfield');
        ontology.columns.forEach(function (e) {
            var field = tagfield.store.add(e);
            tagfield.addValue(field);
        });
        win.down('#destination_bio_feature').setValue(ontology.is_biofeature);
        win.down('#destination_sample').setValue(ontology.is_sample);
        button.clearListeners();
        button.el.on('click', function() {
            var request = panel.getRequestObject('update_ontology');
            var fields = [];
            tagfield.getValueRecords().forEach(function (e) {
                var field = e.data;
                delete field.id;
                fields.push(field);
            });
            request.values = form.getValues();
            request.values.id = ontology.id;
            request.values.fields = fields;
            if (form.isValid()) {
                form.submit({
                    url: request.view + '/' + request.operation,
                    waitMsg: null,
                    params: {
                        request: JSON.stringify(request)
                    },
                    success: function (f, response) {
                        if (command.current.checkHttpResponse(response.response)) {
                            panel.getController().onSelectOntology(panel.getView(), panel.getSelection()[0]);
                            win.close();
                        }
                    },
                    failure: function (f, response) {

                    }
                });
            }
        });
    },

    _populateOntologyNodesGrid: function(panel, grid_panel, ontology_id, node_id) {
        var request = grid_panel.getRequestObject('get_ontology_nodes');
        var request_columns = panel.getRequestObject('get_ontology_columns');
        var paging = grid_panel.down('command_paging');
        var filter = grid_panel.down('command_livefilter');
        var ws = command.current.ws;
        request.values = JSON.stringify({'ontology_id': ontology_id, 'node_id': node_id});
        request_columns.values = request.values;
        paging.values = request.values;
        filter.values = request.values;
        Ext.Ajax.request({
            url: request_columns.view + '/' + request_columns.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    grid_panel.headerCt.removeAll();
                    resp.columns.forEach(function(e) {
                        grid_panel.headerCt.insert(
                            grid_panel.columns.length,
                            Ext.create('Ext.grid.column.Column', {
                                text: e.text,
                                dataIndex: e.data_index,
                                flex: 2,
                                sortable: true,
                                hidden: false
                            })
                        );
                    });
                    ws.stream(request.view).send(request);
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    _populateOntologyGraphView: function(panel, cy_panel, ontology_id, node_id) {
        var request = panel.getRequestObject('get_ontology_structure');
        request.values = JSON.stringify({'ontology_id': ontology_id, 'node_id': node_id});
        Ext.Ajax.request({
            url: request.view + '/' + request.operation,
            params: request,
            success: function (response) {
                if (command.current.checkHttpResponse(response)) {
                    var resp = JSON.parse(response.responseText);
                    cy_panel.cy = cytoscape({
                        container: document.getElementById(cy_panel.id), // container to render in
                        elements: resp.ontology,
                        style: [ // the stylesheet for the graph
                            {
                                selector: 'node',
                                style: {
                                    'content': 'data(original_id)',
                                    'text-opacity': 0.5,
                                    'text-valign': 'center',
                                    'text-halign': 'right',
                                    'background-color': 'gray'
                                  }
                            },
                            {
                                selector: 'edge',
                                style: {
                                    'curve-style': 'bezier',
                                    'width': 4,
                                    'target-arrow-shape': 'triangle',
                                    'line-color': '#9dbaea',
                                    'target-arrow-color': '#9dbaea'
                                  }
                            }
                        ],
                        layout: {
                            name: 'breadthfirst',
                            fit: false,
                            directed: true,
                            circle: false,
                            nodeDimensionsIncludeLabels: true,
                            maximalAdjustments: 10,
                            zoom: 0.5,
                            transform: function (node, pos) {
                                pos.y += 100;
                                pos.x += 100;
                                return pos;
                            }
                        }
                    });
                    cy_panel.cy.on('select', 'node', function(evt){
                        evt.target[0].animate({
                            'style': { 'background-color': 'blue' }
                        });
                        var tabpanel = cy_panel.up('#ontology_tabpanel');
                        var update_ontology_node_button = tabpanel.down('#update_ontology_node_button');
                        var delete_ontology_node_button = tabpanel.down('#delete_ontology_node_button');
                        update_ontology_node_button.setDisabled(false);
                        delete_ontology_node_button.setDisabled(false);
                    });
                    cy_panel.cy.on('unselect', 'node', function(evt){
                        evt.target[0].animate({
                            'style': { 'background-color': 'gray' }
                        });

                    });
                    /*cy_panel.cy.on('click', 'node', function(evt){
                        var node = evt.target[0]._private.data;
                        var tt = new Ext.ToolTip({
                            target: null,
                            html:   '<p>' + node.id + '</p>' +
                                    '<p>' + node.name + '</p>' +
                                    '<p>' + node.def + '</p>',
                            renderTo: cy_panel.id,
                        });
                        tt.on('hide', function(me) {
                            setTimeout(function() {
                                tt.destroy();
                            }, 2000);
                        });
                        tt.show();
                        tt.setLocalXY([evt.renderedPosition.x + (25 * evt.cy._private.zoom), evt.renderedPosition.y - (25 * evt.cy._private.zoom)])
                    });*/
                    cy_panel.cy.on('cxttap', 'node', function(evt){
                        var node = evt.target[0]._private.data;
                        panel.controller._populateOntologyGraphView(panel, cy_panel, ontology_id, node.id)
                    });
                    cy_panel.cy.nodes(function (ele) {
                        if (ele._private.data.id == node_id) {
                            ele.select();
                        }
                    });
                }
            },
            failure: function (response) {
                console.log('Server error', reponse);
            }
        });
    },

    onOntologyTabChange: function(me, newCard, oldCard, eOpts) {
        if (newCard.xtype == 'view_ontology') {
            if (newCard.getSelection().length == 0) {
                var update_ontology_node_button = me.down('#update_ontology_node_button');
                var delete_ontology_node_button = me.down('#delete_ontology_node_button');
                update_ontology_node_button.setDisabled(true);
                delete_ontology_node_button.setDisabled(true);
            }
        }
    },

    onSelectOntology: function (me, record, item, index, e, eOpts, node_id) {
        var panel = me.up('available_ontologies');
        var cy_panel = me.up('ontologies').down('cy_ontology');
        var grid_panel = me.up('ontologies').down('view_ontology');
        var tabpanel = me.up('ontologies').down('#ontology_tabpanel');
        var new_node_button = tabpanel.down('#new_ontology_node_button');
        new_node_button.setDisabled(index < 0);
        tabpanel.setTitle('Ontology: ' + record.data.name);
        panel.controller._populateOntologyGraphView(panel, cy_panel, record.id, node_id);
        panel.controller._populateOntologyNodesGrid(panel, grid_panel, record.id, node_id);
        grid_panel.getSelectionModel().deselectAll();
        var update_ontology_node_button = tabpanel.down('#update_ontology_node_button');
        var delete_ontology_node_button = tabpanel.down('#delete_ontology_node_button');
        update_ontology_node_button.setDisabled(true);
        delete_ontology_node_button.setDisabled(true);
    },

    onCreateOntology: function (me) {
        var panel = me.findParentByType('[xtype="new_ontology_panel"]');
        var win = me.findParentByType('[xtype="window_new_ontology"]');
        var operation = 'create_ontology';
        var request = panel.getRequestObject(operation);
        var form = me.up('form');
        var fields = [];
        win.down('#ontology_tagfield').getValueRecords().forEach(function (e) {
            var field = e.data;
            delete field.id;
            fields.push(field);
        });
        request.values = form.getValues();
        request.values.fields = fields;
        if (form.isValid()) {
            win.setLoading('Uploading');
            form.submit({
                url: request.view + '/' + request.operation,
                waitMsg: null,
                params: {
                    request: JSON.stringify(request)
                },
                success: function (f, response) {
                    win.setLoading(false);
                    if (command.current.checkHttpResponse(response.response)) {
                        command.current.showMessage('info', 'Gene file uploaded', 'File will now be parsed in background and data will appear in the grid once ready.')
                        win.close();
                    }
                },
                failure: function (f, response) {
                    win.setLoading(false);
                    command.current.checkHttpResponse(response.response);
                }
            });
        }
    },

    onDeleteOntology: function(b, eOpts) {
        var grid = b.up('available_ontologies');
        var node_grid = b.up('ontologies').down('view_ontology');
        var ontology = grid.getSelectionModel().getSelection()[0].data;
        var request = grid.getRequestObject('delete_ontology');
        Ext.MessageBox.show({
            title: 'Delete ontology',
            msg: 'Are you sure you want to delete ontology ' + ontology.name + '?',
            buttons: Ext.MessageBox.YESNOCANCEL,
            icon: Ext.MessageBox.QUESTION,
            fn: function (a) {
                if (a == 'yes') {
                    request.values = ontology.id;
                    grid.setLoading(true);
                    Ext.Ajax.request({
                        url: request.view + '/' + request.operation,
                        params: request,
                        success: function (response) {
                            if (command.current.checkHttpResponse(response)) {
                                node_grid.headerCt.removeAll();
                                grid.setLoading(false);
                            }
                        },
                        failure: function (response) {
                            console.log('Server error', reponse);
                            grid.setLoading(false);
                        }
                    });
                }
            }
        })
    },

    onFocusFileType: function (me) {
        var comp = JSON.parse(localStorage.getItem("current_compendium"));
        me.getStore().loadData(comp.ontology_file_types);
    },

    onCreateBlankChange: function (me, newValue, oldValue, eOpts) {
        me.up('form').down('#ontology_file').setDisabled(newValue);
        me.up('form').down('#add_json_field_columns').setDisabled(
            !me.up('form').down('#ontology_file').disabled
        );
    },

    onSelectOntologyNode: function (me, record, item, index, e, eOpts) {
        var panel = me.up('#ontologies').down('available_ontologies');
        var cy_panel = me.up('#ontologies').down('cy_ontology');
        var ontology_id = panel.getSelection()[0].id;
        var tabpanel = me.up('#ontology_tabpanel');
        var update_ontology_node_button = tabpanel.down('#update_ontology_node_button');
        var delete_ontology_node_button = tabpanel.down('#delete_ontology_node_button');
        update_ontology_node_button.setDisabled(index < 0);
        delete_ontology_node_button.setDisabled(index < 0);
        panel.controller._populateOntologyGraphView(panel, cy_panel, ontology_id, record.data.id);
    },

    CyOntologyAfterRender: function (me, eOpts) {

    }
});
